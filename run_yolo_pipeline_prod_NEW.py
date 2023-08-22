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
dl.setenv(ENV)

project = dl.projects.get(project_name='CVPR 2023 Demo')

pipeline_name = 'Active Learning with YOLO'
pipeline = dl.pipelines.get(pipeline_name=pipeline_name)

# tasks' IDs
annot_task = dl.tasks.get(task_id='6488cf067557af258cb7ea05')
qa_task = dl.tasks.get(task_id='6488cf0677a28c20e839aebe')

COPIED_ITEMS = 1900
DATASET_CLEANUP = False
ADD_DATA = True

# a dataset for simulating the image stream to the pipeline
dataset_origin = project.datasets.get(dataset_name='Active Learning Inputs')
# the dataset with the pipeline input / ground truth data
dataset_input = project.datasets.get(dataset_name='Active Learning for Object Detection')

# to make sure each run of the file is the same order of items
filters = dl.Filters(resource=dl.FiltersResource.ITEM)
filters.sort_by(field='name', value=dl.FiltersOrderByDirection.ASCENDING)
pages = dataset_origin.items.list(filters=filters)

if DATASET_CLEANUP is True and COPIED_ITEMS == 0:
    for item in dataset_input.items.list().all():
        item.delete()
    copy_items_start = 0
else:
    copy_items_start = COPIED_ITEMS

exec_count = 0
items_copied = 0
# copy items from dataset to stream from to input dataset, i is the # items copied count
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

        # after 1000 are copied, execute the pipeline for bit cats split 3
        if i % 2000 == 0:

            complete_task(annot_task)
            complete_task(qa_task)

            # for pausing the execution until the previous one is done
            # if items_copied == 1000:  # TODO remove after the first run
            #     time.sleep(7200)

            execution = pipeline.execute()

            exec_count += 1
            print(f'began pipeline execution {exec_count} time(s)')

            HOURS_WAIT = 0.5
            # try:
            #     var = inputimeout(prompt='press enter to continue the next cycle', timeout=HOURS_WAIT * 3600)
            # except TimeoutOccurred:
            #     var = 'no manual input entered, \n'
            while execution.status not in ['success', 'failed']:
                print("execution still running, waiting for 30 minutes")
                time.sleep(HOURS_WAIT * 3600)

                execution = dl.pipeline_executions.get(pipeline_id=pipeline.id, pipeline_execution_id=execution.id)

            if exec_count < 4:
                print('starting next cycle')
            else:
                print('ending execution')
                break
