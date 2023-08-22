import json
import dtlpy as dl
from modules.new_model import new_model

ENV = 'new-dev'
# PROJECT_ID = 'e370fbba-7b8a-4f72-abf3-52b079f019e9'
PROJECT_NAME = 'Active learning'
# YOLOV8
MODEL_NAME = 'yolov5-clone-1687102636180'
DATASET_NAME = 'GT mini'

dl.setenv(ENV)
if dl.token_expired():
    dl.login()
# project = dl.projects.get(project_id=PROJECT_ID)
project = dl.projects.get(project_name=PROJECT_NAME)
model = project.models.get(model_name=MODEL_NAME)
dataset = project.datasets.get(dataset_name=DATASET_NAME)

cloned_model = new_model(base_model=model,
                         dataset=dataset,
                         train_subset=dl.Filters(),
                         validation_subset=dl.Filters(),
                         model_configuration={},
                         )


pipeline = dl.pipelines.get(pipeline_id='64b00c53e85bbc23865c8ef1')
pipeline.execute()
