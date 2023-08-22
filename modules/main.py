import dtlpy as dl
import random
import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)


class ServiceRunner(dl.BaseServiceRunner):

    def __init__(self):
        ...

    @staticmethod
    def data_split(item: dl.Item, progress: dl.Progress, context: dl.Context) -> dl.Item:
        """
        Split data into subsets (e.g. train, validation and test sets)

        :param item:
        :param progress:
        :param context:
        :return:
        """

        node = context.node
        groups = node.metadata['customNodeConfig']['groups']
        population = [group['name'] for group in groups]
        distribution = [int(group['distribution']) for group in groups]
        action = random.choices(population=population, weights=distribution)
        progress.update(action=action[0])
        add_item_metadata = context.node.metadata.get('customNodeConfig', {}).get('itemMetadata', False)
        if add_item_metadata:
            if 'system' not in item.metadata:
                item.metadata['system'] = {}
            if 'tags' not in item.metadata['system']:
                item.metadata['system']['tags'] = {}
            item.metadata['system']['tags'][action[0]] = True
            item = item.update(True)
        return item

    @staticmethod
    def train_model(model: dl.Model):
        print(f'Hello you have reached (dummy) training')
        return model

    @staticmethod
    def evaluate_model(model: dl.Model, test_dataset: dl.Dataset, test_filter: dict):
        """
        Evaluate the model according to the test subset of the dataset
        :param test_dataset: dl.Dataset entity where test items are located
        :param test_filter: JSON for DQL query to get test items to predict on
        :param model: dl.Model entity to evaluate
        :return:
        """
        logging.info(f"Evaluating model {model.name} on test subset of dataset {test_dataset.name}.")
        print(f"DQL query: {test_filter}")

        # call model predict function
        # do some scoring/metrics to give the precision recall, F1, or confusion matrix
        # upload metrics to feature management?

        return model

    @staticmethod
    def compare_models(model_1: dl.Model, model_2: dl.Model, comparison_subset: dl.Item):
        """
        Compare the two models according to the config dictionary

        :param model_1:
        :param model_2:
        :param comparison_subset:
        :return:
        """

        logging.info(f'Comparing models {model_1.name} and {model_2.name}.')
        # check model status, must be "trained" or "deployed"

        return model_1, model_2

    @staticmethod
    def ping():
        print(f'Ponggggg: {datetime.datetime.now().isoformat()}')
