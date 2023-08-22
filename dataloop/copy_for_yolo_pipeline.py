import dtlpy as dl
from inputimeout import inputimeout, TimeoutOccurred
import random

ENV = 'rc'
dl.setenv(ENV)

project = dl.projects.get(project_name='Active Learning 1.3')

dataset_origin = project.datasets.get(dataset_name='hard hats')
pages = dataset_origin.items.list()

dataset_stream = project.datasets.get(dataset_name='hard hats input')


def create_first_model():
    import dtlpy as dl
    dl.setenv('prod')
    model = dl.models.get(None, '6488df5a9a02a7448c95ed84')
    clone = model.clone(project_id=model.project.id,
                        model_name='active-learning-model-cycle-0.',
                        dataset=dataset,
                        train_filter=train_filter,
                        validation_filter=validation_filter
                        )
    clone.metrics = model.metrics
    clone.update()

def copy_all_items(pages):
    for i, item in enumerate(pages.all()):
        # item.clone(dst_dataset_id=dataset_stream.id,
        #            with_annotations=True,
        #            with_metadata=True)

        # Download item (without save to disk)
        buffer = item.download(save_locally=False)
        # Give the item's name to the buffer
        buffer.name = item.name

        # Upload item
        print("Going to add {} to root dir".format(buffer.name))

        new_item = dataset_stream.items.upload(local_path=buffer, overwrite=False)
        new_item.annotations.upload(item.annotations.list())
        if not isinstance(new_item, dl.Item):
            print('The file {} could not be uploaded'.format(buffer.name))
            continue
        print("{} has been uploaded".format(new_item.filename))

    # if i > 5:  # this cloned 7, somehow
    #     print(i)
    #     break


# input('check the dataset copied correctly')
#
# # create recipe
# project = dataset_origin.project
# ontology_labels = list()
# for key, value in dataset_origin.instance_map.items():
#     ontology_labels.append(dl.Label(tag=key))
#
# ontology = project.ontologies.create(title=f"{dataset_stream.name}_labels",
#                                      labels=ontology_labels)
# recipe = dataset_stream.recipes.create(recipe_name=f'labelled {dataset_stream.name} recipe', labels=ontology_labels)

def copy_100_items(dataset_stream, dataset_gt, copy_items_start=0):
    random.seed(42)
    items = list(dataset_stream.items.list().all())
    random.shuffle(items)

    items_copied = 0
    for i, item_orig in enumerate(items):
        if i >= copy_items_start:
            print()
            print(i, item_orig.filename)

            buffer = item_orig.download(save_locally=False)
            buffer.name = item_orig.name
            new_item = dataset_gt.items.upload(local_path=buffer)
            new_item.annotations.upload(item_orig.annotations.list())

            if not isinstance(new_item, dl.Item):
                print(f'The file {buffer.name} could not be uploaded to {dataset_gt.name}')
                continue

            items_copied += 1
        if items_copied >= 100:
            break


def copy_new_recipe(dataset_from, dataset_to):
    ## for copying the labels to a new dataset
    # dataset_to = project.datasets.get(dataset_name='yolo cycle test input')
    recipe = dataset_to.recipes.list()[0]
    ontology = recipe.ontologies.list()[0]

    # dataset_from = project.datasets.get(dataset_name='hard hats input')
    recipe_from = dataset_from.recipes.list()[0]
    labels = recipe_from.ontologies.list()[0].labels

    ontology.add_labels(label_list=labels)
    ontology.update()


###################################
# copy 100 items to a new dataset #
###################################
# dataset_gt = project.datasets.get(dataset_name='hard hats GT')
dataset_gt = project.datasets.create(dataset_name='model eval test')
copy_100_items(dataset_stream=dataset_stream, dataset_gt=dataset_gt, copy_items_start=0)
copy_new_recipe(dataset_stream, dataset_gt)


# input('check the dataset copied correctly')


################################
# some pipeline execution code #
################################
# do execution
def execute_pipeline():
    pipeline_name = 'yolo cycle'
    pipeline = dl.pipelines.get(pipeline_name=pipeline_name)
    execution = pipeline.execute()
    print(execution)

    pipeline_id = '6481bc70eaa44a8ed72c1295'
    pipeline = dl.pipelines.get(pipeline_id=pipeline_id)
    execution = pipeline.execute()
    print(execution)


##############################
# some model evaluation code #
##############################
def evaluate_model():
    model_for_eval = dl.models.get(None, '6481ccc1216aa32321ec4f4a')
    print(model_for_eval.dataset)
    model_for_eval.evaluate(dataset_id=model_for_eval.dataset.id)

    model = model_for_eval.clone(model_name='test_metadata',
                                 dataset=model_for_eval.dataset)
