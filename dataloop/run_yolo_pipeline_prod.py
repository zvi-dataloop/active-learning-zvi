import dtlpy as dl
from inputimeout import inputimeout, TimeoutOccurred
import time


def complete_task(task: dl.Task):
    dataset = task.dataset

    # # Get assignments list - in a task
    assignments = task.assignments.list()
    for assignment in assignments:
        items = list(assignment.get_items().all())
        for item in items:
            if task.spec['type'] == 'annotation':
                item.update_status(status=dl.ItemStatus.COMPLETED, task_id=task.id)
            else:
                item.update_status(status=dl.ItemStatus.APPROVED, assignment_id=assignment.id)


ENV = 'prod'
NEXT_CYCLE_START = 3000
DATASET_CLEANUP = False
ADD_DATA = True

dl.setenv(ENV)

if ENV == 'prod':
    project_name = 'CVPR 2023 Demo'
    pipeline_name = 'Active Learning with YOLO'  # Active Learning YOLOv8-018
    annot_task_id = '648ebe444208da6f39fc4a76'
    qa_task_id = '648ebe454208daf097fc4a78'
    dataset_origin_name = 'Active Learning Inputs'
    dataset_input_name = 'Active Learning for Object Detection'
elif ENV == 'new-dev':
    project_name = 'Active Learning'
    pipeline_name = 'Active Learning'  # Active Learning YOLOv8-018
    annot_task_id = '648f6d028d31193a7654a30d'
    qa_task_id = '648f6d028d3119ceb654a310'
    dataset_origin_name = 'Active Learning Inputs'
    dataset_input_name = 'Ground Truth for Active Learning'

pipeline = dl.pipelines.get(pipeline_name=pipeline_name)
project = dl.projects.get(project_name=project_name)
annot_task = dl.tasks.get(task_id=annot_task_id)
qa_task = dl.tasks.get(task_id=qa_task_id)

# a dataset for simulating the image stream to the pipeline
dataset_origin = project.datasets.get(dataset_name=dataset_origin_name)
# the dataset with the pipeline input / ground truth data
dataset_input = project.datasets.get(dataset_name=dataset_input_name)
existing_items = dataset_input.items_count

# to make sure each run of the file is the same order of items
filters = dl.Filters(resource=dl.FiltersResource.ITEM)
filters.sort_by(field='name', value=dl.FiltersOrderByDirection.ASCENDING)
pages = dataset_origin.items.list(filters=filters)

if DATASET_CLEANUP is True and existing_items != 0:
    for item in dataset_input.items.list().all():
        item.delete()
    copy_items_start = 0
else:
    copy_items_start = existing_items

##########################
# Trigger upper pipeline #
##########################
# copy items from dataset to stream from to input dataset, i is the # items copied count
items_copied = 0
for i, item_orig in enumerate(pages.all()):
    if i >= copy_items_start:
        print()
        print(i, item_orig.filename)

        if ADD_DATA is True:
            buffer = item_orig.download(save_locally=False)
            buffer.name = item_orig.name
            new_item = dataset_input.items.upload(local_path=buffer)
            # TODO check that this works correctly
            if item_orig.metadata['system'].get('tags') is not None:
                new_item.metadata.update({'system': item_orig.metadata['system']['tags']})
            new_item.annotations.upload(item_orig.annotations.list())

            if not isinstance(new_item, dl.Item):
                print(f'The file {buffer.name} could not be uploaded to {dataset_input.name}')
                continue

            items_copied += 1

    if i == NEXT_CYCLE_START:
        complete_task(annot_task)
        time.sleep(60)
        complete_task(qa_task)

        time.sleep(120)

        # run the lower pipeline
        execution = pipeline.execute()

        exec_count = round(NEXT_CYCLE_START % 1000)
        print(f'copied {items_copied} new items, and ran pipeline cycles at {i} items')
        print(f'ran pipeline cycles {exec_count} time(s)')
