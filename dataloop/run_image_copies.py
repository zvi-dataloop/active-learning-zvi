import dtlpy as dl
import time
from tqdm import tqdm

project = dl.projects.get(project_name='Active Learning 1.3')

# a dataset for simulating the image stream to the pipeline
dataset_origin = project.datasets.get(dataset_name='big cats')

# the dataset for initiating the pipeline
dataset_input = project.datasets.get(dataset_name='big cats input')
filters = dl.Filters(resource=dl.FiltersResource.ITEM)
filters.sort_by(field='name', value=dl.FiltersOrderByDirection.ASCENDING)
pages = dataset_origin.items.list(filters=filters)

# the final dataset for training, which needs cleaning before starting the script
dataset_pipeline = project.datasets.get(dataset_name='big cats split 3')

for item in dataset_input.items.list().all():
    item.delete()
for item in dataset_pipeline.items.list().all():
    item.delete()
copy_items_start = 0

# items_copied = 0
for i, item_orig in enumerate(pages.all()):
    print(i, item_orig.filename)

    buffer = item_orig.download(save_locally=False)
    buffer.name = item_orig.name
    new_item = dataset_input.items.upload(local_path=buffer)
    new_item.annotations.upload(item_orig.annotations.list())

    if not isinstance(new_item, dl.Item):
        print(f'The file {buffer.name} could not be uploaded to {dataset_input.name}')
        continue

    if (i+1) % 100 == 0:
        input(f'uploaded {i} items, press any key to continue')
        # time.sleep(1800)


## upload ground truth annotations 
for item in pages.all():
    folder = item.filename.split('/')[1]
    print(folder)
    builder = item.annotations.builder()

    builder.add(annotation_definition=dl.Classification(label=folder))
    item.annotations.upload(builder)