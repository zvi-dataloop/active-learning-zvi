import json
import dtlpy as dl
from dtlpymetrics.scoring import create_model_score
from modules.model_evaluation import evaluator

ENV = 'prod'
PROJECT_ID = 'e370fbba-7b8a-4f72-abf3-52b079f019e9'

dl.setenv(ENV)
if dl.token_expired():
    dl.login()
project = dl.projects.get(project_id=PROJECT_ID)

# YOLOV8
model_id = '6490054acb7eb972681fe982'
dataset_id = '648d53d0bf4c7ce5fc0b1bff'

test_filter = '{"filter": {"$and": [{"hidden": false}, {"$or": [{"metadata": {"system": {"tags": {"test": true}}}}]}, {"type": "file"}]}, "page": 0, "pageSize": 1000, "resource": "items"}'
filters = dl.Filters(custom_filter=json.loads(test_filter))

model = dl.models.get(None, model_id)
dataset = project.datasets.get(dataset_id=dataset_id)

pages = dataset.items.list(filters=filters)
print(f'items in test set: {pages.items_count}')

# test the actual evaluate function, locally (but need the right pkgs installed)
# evaluator.evaluate_model(model=model,
#                          test_dataset=dataset,
#                          test_filter=filters)

## test the model scoring
success, response = create_model_score(model=model,
                                       dataset=dataset,
                                       filters=filters,
                                       compare_types=[model.output_type])
print(response)
