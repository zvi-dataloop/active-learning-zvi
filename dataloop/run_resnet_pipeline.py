import dtlpy as dl
from inputimeout import inputimeout, TimeoutOccurred

ENV = 'rc'
dl.setenv(ENV)

project = dl.projects.get(project_name='Active Learning 1.3')

pipeline_name = 'full cycle resnet'
pipeline = dl.pipelines.get(pipeline_name=pipeline_name)
DATASET_CLEANUP = True
COPIED_ITEMS = 0

# a dataset for simulating the image stream to the pipeline
dataset_origin = project.datasets.get(dataset_name='big cats stream')

# the dataset with the pipeline input / ground truth data
dataset_input = project.datasets.get(dataset_name='big cats GT')
filters = dl.Filters(resource=dl.FiltersResource.ITEM)
filters.sort_by(field='name', value=dl.FiltersOrderByDirection.ASCENDING)
pages = dataset_origin.items.list(filters=filters)

exec_count = 0
items_copied = 0

if DATASET_CLEANUP:
    for item in dataset_input.items.list().all():
        item.delete()
    copy_items_start = 0
else:
    copy_items_start = COPIED_ITEMS

# copy items from big cats to big cats input, i is the # items copied count
for i, item_orig in enumerate(pages.all()):
    if i >= copy_items_start:
        print()
        print(i, item_orig.filename)

        buffer = item_orig.download(save_locally=False)
        buffer.name = item_orig.name
        new_item = dataset_input.items.upload(local_path=buffer)
        # TODO check that this works correctly
        new_item.item_metadata['system']['tags'] = item_orig.metadata['system']['tags']
        new_item.annotations.upload(item_orig.annotations.list())

        if not isinstance(new_item, dl.Item):
            print(f'The file {buffer.name} could not be uploaded to {dataset_input.name}')
            continue

        items_copied += 1

        # after 100 are copied, execute the pipeline for bit cats split 3
        if items_copied % 100 == 0:
            execution = pipeline.execute()

            exec_count += 1
            print(f'began pipeline execution {exec_count} time(s)')

            try:
                var = inputimeout(prompt='press enter to continue the next cycle', timeout=1800)
            except TimeoutOccurred:
                var = 'no manual input entered, \n'

            print('starting next cycle')


def cleanup_dataset():
    import dtlpy as dl
    project = dl.projects.get(project_name='Active Learning 1.3')
    # dataset = project.datasets.get(dataset_name='big cats input')
    dataset = project.datasets.get(dataset_name='big cats split 3')
    items = dataset.items.list().all()
    for item in items:
        item.delete()


##################################################
# This is for creating a new dataset directories #
##################################################
def create_dataset():
    dataset = project.datasets.get(dataset_name='big cats split 2')
    recipe = project.recipes.get(recipe_id='646e00c0823ded208296c224')
    dataset.switch_recipe(recipe=recipe)

    #### create directories for data
    labels = ['cheetah', 'leopard', 'lion', 'tiger']

    dataset = project.datasets.create(dataset_name='big cats split 3')
    dataset.items.make_dir(directory='/train')
    dataset.items.make_dir(directory='/validation')
    dataset.items.make_dir(directory='/test')
    dataset.add_labels(label_list=labels)
    dataset.update()

    dataset = dl.datasets.get(None, dataset.id)
    print(dataset.labels)


def create_input_items():
    # a dataset for simulating the image stream to the pipeline
    dataset_origin = project.datasets.get(dataset_name='big cats')
    # the dataset for initiating the pipeline
    dataset_input = project.datasets.get(dataset_name='big cats input')
    filters = dl.Filters(resource=dl.FiltersResource.ITEM)
    filters.sort_by(field='name', value=dl.FiltersOrderByDirection.ASCENDING)
    pages = dataset_origin.items.list(filters=filters)

    items_copied = 0

    for i, item_orig in enumerate(pages.all()):
        if i >= copy_items_start:
            print(i, item_orig.filename)

            buffer = item_orig.download(save_locally=False)
            buffer.name = item_orig.name
            new_item = dataset_input.items.upload(local_path=buffer)
            new_item.annotations.upload(item_orig.annotations.list())

            if not isinstance(new_item, dl.Item):
                print(f'The file {buffer.name} could not be uploaded to {dataset_input.name}')
                continue

            items_copied += 1


def clean_models():
    import dtlpy as dl

    dl.setenv('rc')
    project = dl.projects.get(project_name='Active Learning 1.3')

    models = project.models.list()
    for model in models.all():
        if 'resnet' in model.name and model.status != "deployed":
            print(model.name)
            model.delete()
