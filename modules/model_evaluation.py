import dtlpy as dl
import logging
import json
import typing
from dtlpymetrics.scoring import create_model_score

evaluator = dl.AppModule(name='Model Evaluation', description='Models can be evaluated with a model entity and '
                                                              'configured dataset to compare predictions to ground '
                                                              'truth annotations.')
logger = logging.getLogger('ModelAdapter')


@evaluator.set_init()
def setup():
    pass


def predict_items(items: typing.List[dl.Item], model: dl.Model = None):
    """
    Run the predict function on the input list of items (or single) and return the items and the predictions.
    Each prediction is by the model output type (package.output_type) and model_info in the metadata

    :param items: `List[dl.Item]` list of items to predict
    :param model: `dl.Model` Model entity, if model is changed, the new model will be loaded before prediction

    :return: `List[dl.Item]`, `List[List[dl.Annotation]]`
    """

    logger.info(f'Received a model: name: {model.name}, id: {model.id}')
    model_entity = model
    adapter = model_entity.package.build(module_name='model-adapter',
                                         init_inputs={'model_entity': model_entity})
    logger.info(f'Done and ready to predict. Loaded model: {model_entity.name}')

    #######################
    # load configurations #
    #######################
    upload_annotations = model_entity.configuration.get('upload_annotations', True)
    conf_threshold = model_entity.configuration.get('conf_threshold', 0.1)
    batch_size = model_entity.configuration.get('batch_size', 16)

    items, annotations = adapter.predict_items(items=items,
                                               upload_annotations=upload_annotations,
                                               conf_threshold=conf_threshold,
                                               batch_size=batch_size)


def predict_dataset(model: dl.Model, dataset: dl.Dataset, filters=None):
    """
    Run the predict function on the input dataset and filters, and return the items and the predictions.
    Each prediction is by the model output type (package.output_type) and model_info in the metadata

    :param model: `dl.Model` Model entity, if model is changed, the new model will be loaded before prediction
    :param dataset: `dl.Dataset` Dataset entity to predict
    :param filters: `dl.Filters` Filters to apply on the dataset before prediction

    :return: `List[dl.Item]`, `List[List[dl.Annotation]]`
    """

    logger.info(f'Received a model: name: {model.name}, id: {model.id}')
    model_entity = model
    adapter = model_entity.package.build(module_name='model-adapter',
                                         init_inputs={'model_entity': model_entity})
    logger.info(f'Done and ready to predict. Loaded model: {model_entity.name}')

    _ = adapter.evaluate_model(model=model,
                               dataset=dataset,
                               filters=filters)


@evaluator.add_function(display_name='Evaluate Model',
                        inputs={'model': dl.Model,
                                'test_dataset': dl.Dataset,
                                'test_filter': dict},
                        outputs={'model': dl.Model})
def evaluate_model(model: dl.Model,
                   test_dataset: dl.Dataset,
                   test_filter: dict):
    """
    Evaluate the model according to the test subset of the dataset
    :param model: dl.Model entity to evaluate
    :param test_dataset: dl.Dataset entity where test items are located
    :param test_filter: JSON for DQL query to get test items to predict on
    :return:
    """
    logger.info(f"Evaluating model {model.name} on test subset of dataset {test_dataset.name}.")
    logger.info(f"Test set DQL query: {test_filter}")

    if model.status not in ['trained', 'deployed']:
        return False, 'Model must be trained or deployed to evaluate'

    if isinstance(test_filter, dict):
        test_filter = dl.Filters(custom_filter=test_filter, resource=dl.FiltersResource.ITEM)
    compare_types = model.output_type

    items = list(test_dataset.items.list(filters=test_filter).all())
    # item_ids = [item.id for item in items]

    # take all items, predict, and compare to the ground truth set
    logger.info(f"Predicting on {len(items)} test items.")
    predict_items(items=items, model=model)
    # predict_dataset(dataset=test_dataset, model=model, filters=test_filter)

    # create model scores
    # go through items list and calculate the scores according to the GT labels
    success, response = create_model_score(model=model,
                                           dataset=test_dataset,
                                           compare_types=compare_types)
    logger.info(response)

    # update model metadata
    if model.metadata['system'].get('evaluate', {}).get('datasets') is None:
        model.metadata['system']['evaluate'] = {'datasets': [test_dataset.id]}
    else:
        model.metadata['system']['evaluate']['datasets'].append(test_dataset.id)
    model.update(system_metadata=True)

    return model, test_dataset
