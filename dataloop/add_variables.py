import dtlpy as dl

pipeline_id = '646e10a6868cd45dcaac15f4'
pipeline = dl.pipelines.get(pipeline_id=pipeline_id)

pipeline_name = ''
pipeline = dl.pipelines.get(pipeline_name=pipeline_name)
pipeline_id = pipeline.id

model_var_name = 'resnet50-trained'

payload = {'variables': [{"id": "undefined",
                          "name": model_var_name,
                          "reference": pipeline_id,
                          "creator": "yaya.t@dataloop.ai",
                          "value": "6462417fcc4a02b5bea99e14",
                          "type": "Model",
                          "createdAt": "2023-05-23T20:43:18.710Z",
                          "updatedAt": "2023-05-23T20:43:18.710Z",
                          "_id": "646d25662ecf613cd97cae5a"},
                         {"id": "undefined",
                          "name": "train subset",
                          "reference": pipeline_id,
                          "creator": "yaya.t@dataloop.ai",
                          "value": r"{\"filter\": {\"$and\": [{\"hidden\": false}, {\"$or\": [{\"metadata\": {\"system\": {\"tags\": {\"train\": true}}}}]}, {\"type\": \"file\"}]}, \"page\": 0, \"pageSize\": 1000, \"resource\": \"items\"}",
                          "type": "Json",
                          "createdAt": "2023-05-23T20:43:18.710Z",
                          "updatedAt": "2023-05-23T20:43:18.710Z",
                          "_id": "646d25662ecf6143287cae5b"},
                         {"id": "undefined",
                          "name": "val subset",
                          "reference": pipeline_id,
                          "creator": "yaya.t@dataloop.ai",
                          "value": r"{\"filter\": {\"$and\": [{\"hidden\": false}, {\"$or\": [{\"metadata\": {\"system\": {\"tags\": {\"validation\": true}}}}]}, {\"type\": \"file\"}]}, \"page\": 0, \"pageSize\": 1000, \"resource\": \"items\"}",
                          "type": "Json",
                          "createdAt": "2023-05-23T20:43:18.711Z",
                          "updatedAt": "2023-05-23T20:43:18.711Z",
                          "_id": "646d25662ecf61f0727cae5c"},
                         {"id": "undefined",
                          "name": "test subset",
                          "reference": pipeline_id,
                          "creator": "yaya.t@dataloop.ai",
                          "value": r"{\"filter\": {\"$and\": [{\"hidden\": false}, {\"$or\": [{\"metadata\": {\"system\": {\"tags\": {\"test\": true}}}}]}, {\"type\": \"file\"}]}, \"page\": 0, \"pageSize\": 1000, \"resource\": \"items\"}",
                          "type": "Json",
                          "createdAt": "2023-05-23T20:43:18.711Z",
                          "updatedAt": "2023-05-23T20:43:18.711Z",
                          "_id": "646d25662ecf612d817cae5d"},
                         {"id": "undefined",
                          "name": "compare config",
                          "reference": pipeline_id,
                          "creator": "yaya.t@dataloop.ai",
                          "value": r"{\"evaluate_stage\":{\"accuracy\":{\"lower_is_better_metrics\":false}}}",
                          "type": "Json",
                          "createdAt": "2023-05-23T20:43:18.712Z",
                          "updatedAt": "2023-05-23T20:43:18.712Z",
                          "_id": "646d25662ecf614b5c7cae60"},
                         {"id": "undefined",
                          "name": "best model",
                          "reference": pipeline_id,
                          "creator": "yaya.t@dataloop.ai",
                          "value": "6462417fcc4a02b5bea99e14",
                          "type": "Model",
                          "createdAt": "2023-05-23T20:43:18.712Z",
                          "updatedAt": "2023-05-23T20:43:18.712Z",
                          "_id": "646d25662ecf6121f07cae61"},
                         {"id": "undefined",
                          "name": "resnet config",
                          "reference": pipeline_id,
                          "creator": "yaya.t@dataloop.ai",
                          "value": "{'weights_filename': 'model.pth', 'batch_size': 16, 'num_epochs': 10, 'input_size': 256, 'artifacts_path': '/tmp/.dataloop/models/big cats-resnet-clone-2', 'id_to_label_map': {'0': 'cheetah', '1': 'leopard', '2': 'lion', '3': 'tiger'}}",
                          "type": "Json",
                          "createdAt": "2023-05-23T20:43:18.713Z",
                          "updatedAt": "2023-05-23T20:43:18.713Z",
                          "_id": "646d25662ecf61833e7cae63"}]}
success, response = dl.client_api.gen_request(
    req_type='patch',
    path='/pipelines/{}/variables'.format(pipeline.id),
    json_req=payload
)

# exception handling
if not success:
    raise dl.exceptions.PlatformException(response)
