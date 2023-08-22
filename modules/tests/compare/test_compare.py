import json
import pandas as pd
import dtlpy as dl
from modules.model_compare import ServiceRunner

ENV = 'rc'
PROJECT_NAME = 'Test Project'
PACKAGE_NAME = 'dummy-model-package'
DATASET_NAME = 'test'

dl.setenv(ENV)
if dl.token_expired():
    dl.login()

project = dl.projects.get(project_name=PROJECT_NAME)


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


def compare_models(model_a_name, model_b_name):
    package = project.packages.get(package_name=PACKAGE_NAME)

    model_a = package.models.get(model_name=model_a_name)
    model_b = package.models.get(model_name=model_b_name)

    with open('configuration.json') as conf_file:
        conf_dict = json.load(conf_file)
    res = ServiceRunner().compare_models(model_a, model_b, conf_dict["evaluate_stage"])
    print(res.id, res.name)


def main():
    # upload_model('nozzle-1', 'nozzle-model-1-scores.csv')
    # upload_model('nozzle-2', 'nozzle-model-2-scores.csv')
    # upload_model('nozzle-2-old', 'nozzle-model-2-scores-old.csv')
    # upload_model('nozzle-4', 'nozzle-model-4-scores.csv')

    compare_models('nozzle-1', 'nozzle-2')
    print('========')
    compare_models('nozzle-2', 'nozzle-1')
    print('========')
    compare_models('nozzle-1', 'nozzle-4')


if __name__ == '__main__':
    main()
