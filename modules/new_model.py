import dtlpy as dl
import json
import logging
import datetime

logging.basicConfig(level=logging.INFO)

ModelCreator = dl.AppModule(name='create_new_model',
                            description='Create a new version of a model. Models can be created '
                                        'from pretrained models, or from a custom model. The model '
                                        'will be created in the same project as the input model.')


@ModelCreator.set_init()
def new_model_init():
    logging.info("Initializing model nodes module.")


@ModelCreator.add_function(display_name='Create New Model')
def new_model(from_model: dl.Model,
              dataset: dl.Dataset,
              train_subset: str,
              validation_subset: str,
              model_configuration: dict) -> dl.Model:
    """
    Create a new model version from the input model

    :param from_model: model that will be used as a base for the new model.
    :param dataset:
    :param train_subset:
    :param validation_subset:
    :param model_configuration:
    :return: to_model (dl.Model), a clone of the input model with the specified parameters.
    """

    logging.info(f'Creating new model from {from_model.name}.')
    new_name = f"{from_model.name}-new-{datetime.datetime.now():%s}"
    new_dataset = dataset if dataset else from_model.dataset
    new_configuration = json.dumps(model_configuration) if model_configuration else from_model.configuration
    train_filter = dl.Filters(field="filename", values=f"{train_subset}/**") if train_subset else None
    validation_filter = dl.Filters(field="filename", values=f"{validation_subset}/**") if validation_subset \
        else None
    to_model = from_model.clone(
        model_name=new_name,
        dataset=new_dataset,
        configuration=new_configuration,
        train_filter=train_filter,
        validation_filter=validation_filter,
        status='created'
    )
    logging.info(f'New model {to_model.name} created from {from_model.name}.')
    return to_model


if __name__ == "__main__":
    import pprint

    ModelCreator.init()
    pprint.pprint(ModelCreator.to_json())
