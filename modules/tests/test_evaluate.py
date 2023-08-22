import json
import dtlpy as dl
from dtlpymetrics.scoring import create_model_score
from modules.model_evaluation import evaluator

ENV = 'rc'
PROJECT_ID = '021515ea-ec9c-47fd-842e-9b4df1e89129'  # Active Learning 1.3

dl.setenv(ENV)
if dl.token_expired():
    dl.login()
project = dl.projects.get(project_id=PROJECT_ID)

# #### RESNET
# # model_id = '6473185c93bd97c6a30a47b9'  # fine tuned resnet
# model_id = "6481a032216aa3cfb1ec4f18"  # model in the full cycle to test RESNET
#
# dataset_id = "646e2c13a8386f8b38d5efb5"  # fb5 is big cats
#
# filters = dl.Filters()
# filters.add(field='dir', values='/test')

### YOLOV8
model_id = '6481f19bf18d2526d10af94c'  # yolov8 on hard hats
dataset_id = '648174bb56e25a28ae01b32e'  # hard hats

test_filter = '{"filter": {"$and": [{"hidden": false}, {"$or": [{"metadata": {"system": {"tags": {"test": true}}}}]}, {"type": "file"}]}, "page": 0, "pageSize": 1000, "resource": "items"}'
filters = dl.Filters(custom_filter=json.loads(test_filter))

model = dl.models.get(None, model_id)
dataset = project.datasets.get(dataset_id=dataset_id)

# pages = dataset.items.list(filters=filters)
# print(f'items in test set: {pages.items_count}')

# test the actual evaluate function, locally (but need the rigth pkgs installed)
# evaluator.evaluate_model(model=model,
#                          test_dataset=dataset,
#                          test_filter=filters)

## test the model scoring
success, response = create_model_score(model=model,
                                       dataset=dataset,
                                       filters=filters,
                                       compare_types=[model.output_type])
print(response)
