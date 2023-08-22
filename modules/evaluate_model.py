import dtlpy as dl
# from modules.scoringapp.scoring_main import ScoringAndMetrics
from dtlpymetrics import main

evaluator = dl.AppModule(name='Model Evaluation', description='Models can be evaluated with a model entity and '
                                                              'configured dataset to compare predictions to ground '
                                                              'truth annotations.')


class EvalRunner(dl.BaseServiceRunner):
    @staticmethod
    def evaluate(model: dl.Model, item_ids: list):
        if model.status not in ['trained', 'deployed']:
            return False, 'Model must be trained or deployed to evaluate'

        success = EvalRunner._evaluate_model(model=model, item_ids=item_ids)

        return success

    @staticmethod
    def _evaluate_model(model: dl.Model, item_ids: list):
        # take all items, predict, and compare to the ground truth set
        model.predict(item_ids=item_ids)  # should create annotations with metadata['model']['name']

        # create model scores
        # go through items list and calculate the scores according to the GT labels
        __, annotations_list = main.ScoringAndMetrics.create_model_score(item_set_1=item_ids)

        # for bbox only
        # TODO: add other annotation types
        attributes = {'annotation_id': [],
                      'annotation_label': [],
                      'annotation_confidence': [],
                      'annotation_iou': []
                      }
        # get all relevant annotation attributes
        for annotation in annotations_list:
            # DEBUG
            # annotation = dl.annotations.get(annotation_id='64522094c755ac7178ffb8c9')
            # /DEBUG

            if annotation.metadata.get('user', None).get('model', None).get('name', None) is not None:
                attributes['confidence'].append(annotation.metadata['user']['model']['confidence'])
                attributes['annotation_id'].append(annotation.id)
                attributes['annotation_label'].append(annotation.label)
                attributes['annotation_iou'].append()  # feature set query

        return True
