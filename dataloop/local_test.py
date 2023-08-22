import dtlpy as dl


def check_training():
    dl.setenv('rc')
    project = dl.projects.get(project_name='Active Learning 1.3')
    # model = project.models.get(model_name='pretrained-yolo-v8-new-1684830936')
    model_id = '646d1094429e2d9e4ed72e88'  # demo input, 30 epochs
    model_id = '646cbb26617ee7237e45722a'  # ground truth, 30 epochs?
    model = project.models.get(None, model_id)

    model.artifacts.download(local_path='./.dataloop/model',
                             overwrite=True)

    model.status = 'created'
    model.configuration.update({"epochs": 6})
    model.update()

    model = project.models.get(model_name='pretrained-yolo-v8-new-1684830936')
    print(model.status)
    print(model.configuration)

    model.train()

    # public model
    dataset = project.datasets.get(dataset_name='ground truth')
    yolo = dl.models.get(None, '6462417fcc4a02b5bea99e14')
    cloned_yolo = project.models.clone(base_model=yolo,
                                       model_name='cloned_yolo_v8')
    items = list(dataset.items.list().all())
    cloned_yolo.deploy()

    cloned_yolo.predict(item_ids=[item.id for item in items])


#### Test taco tash
o_model = dl.models.get(None, '646cbb26617ee7237e45722a')

## add variables
pipeline_id = '646db338ebccf13020f99dec'
pipeline = dl.pipelines.get(pipeline_id=pipeline_id)
payload = {'variables': [{"name": "model config full",
                          "value": {'epochs': 2,
                                    'batch_size': 2},
                          "type": "Json",
                          }
                         ]
           }
success, response = dl.client_api.gen_request(
    req_type='patch',
    path='/pipelines/{}/variables'.format(pipeline.id),
    json_req=payload
)

# exception handling
if not success:
    raise dl.exceptions.PlatformException(response)


model = dl.models.get(None, '646e09bdb689567103d38452')
samples = model.metrics.list().to_df()
