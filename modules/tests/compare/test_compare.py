import json
import pandas as pd
import dtlpy as dl
from modules.model_compare import comparator

ENV = 'prod'
PROJECT_NAME = 'CVPR 2023 Demo'

# PROJECT_NAME = 'Test Project'
PROJECT_ID = ''  # fe18d5c9-58e5-41df-b170-16bfcfa0b504'  # Active lEarninG 1.3

PACKAGE_NAME = ''  # 'dummy-model-package'
DATASET_NAME = 'big cats split 3'  # 'test'

dl.setenv(ENV)
if dl.token_expired():
    dl.login()

try:
    project = dl.projects.get(project_name=PROJECT_NAME)
except dl.exceptions.NotFound:
    project = dl.projects.get(project_id=PROJECT_ID)


def upload_model(model_name, metrics_path):
    codebase = project.codebases.pack(directory='./')

    package = project.packages.push(package_name=PACKAGE_NAME,
                                    codebase=codebase,
                                    modules=[])
    dataset = project.datasets.get(dataset_name=DATASET_NAME)
    model = package.models.create(model_name=model_name,
                                  description='model for offline model logging',
                                  dataset_id=dataset.id,
                                  labels=[])

    pre_sheet = pd.read_csv(metrics_path)
    for i, (iou_th, model_name, label, TP, FP, FN, precision, recall, f1) in pre_sheet.iterrows():
        for mes in ['TP', 'FP', 'FN', 'precision', 'recall', 'f1']:
            model.metrics.create(samples=dl.PlotSample(figure=label,
                                                       legend=mes,
                                                       x=iou_th,
                                                       y=locals()[mes]),
                                 dataset_id=model.dataset_id)


def compare_models_by_name(model_a_name, model_b_name):
    package = project.packages.get(package_name=PACKAGE_NAME)

    model_1 = package.models.get(model_name=model_a_name)
    model_2 = package.models.get(model_name=model_b_name)

    with open('configuration.json') as conf_file:
        conf_dict = json.load(conf_file)
    res = comparator.compare_models(model_1, model_2, conf_dict["evaluate_stage"])
    print(res.id, res.name)


def compare_models(model_1, model_2, conf_filename):
    with open(conf_filename) as conf_file:
        conf_dict = json.load(conf_file)
    winning_model_id = comparator.compare_models(model_1, model_2, conf_dict)
    if winning_model_id == model_2.id:
        print("the new model", model_2.name, 'is better than', model_1.name)
    else:
        print("the original", model_1.name, 'is better than', model_2.name)


# def main():
# upload_model('nozzle-1', 'nozzle-model-1-scores.csv')
# upload_model('nozzle-2', 'nozzle-model-2-scores.csv')
# upload_model('nozzle-2-old', 'nozzle-model-2-scores-old.csv')
# upload_model('nozzle-4', 'nozzle-model-4-scores.csv')

# compare_models('nozzle-1', 'nozzle-2')
# print('========')
# compare_models('nozzle-2', 'nozzle-1')
# print('========')
# compare_models('nozzle-1', 'nozzle-4')


if __name__ == '__main__':
    # main()
    # model 1 id 6473460c93bd972f490a47e1
    # model 2 (old resnet) id 646e09bdb689567103d38452
    # compare_models_by_name('pretrained-resnet50-new-1685276171', 'big cats-resnet-clone-2')

    # for active learning
    dl.setenv('prod')
    model_1_id = '6488df5a9a02a7448c95ed84'  # active-learning-model-cycle-0.
    model_2_id = '648bff9da20a426561396733'  # yolov8-cloned-baseline-2023-06-16T06:22:21

    config_name = 'compare_config.json'

    # # for orpak testing
    # model_1_id = '644a881835fcec7d600df785'
    # model_2_id = '644a885735fcec5ad10df7f2'
    # config_name = 'configuration.json'

    model_1 = dl.models.get(None, model_1_id)
    model_2 = dl.models.get(None, model_2_id)
    compare_models(model_1, model_2, config_name)

    # for checking metrics_to_df
    # yolo model id: 646d1094429e2d9e4ed72e88
    # resnet model id: 647df70563bf94327a2cf92c
    # model = dl.models.get(None, model_id='646d1094429e2d9e4ed72e88')
