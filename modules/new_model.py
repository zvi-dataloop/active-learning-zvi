import dtlpy as dl
import json
import logging
import datetime

logging.basicConfig(level=logging.INFO)

model_creator = dl.AppModule(name='create_new_model',
                             description='Create a new version of a model. Models can be created '
                                         'from pretrained models, or from a custom model. The model '
                                         'will be created in the same project as the input model.',
                             )


@model_creator.set_init()
def new_model_init():
    logging.info("Initializing model nodes module.")


@model_creator.add_function(display_name='Create New Model')
def new_model(base_model: dl.Model,
              dataset: dl.Dataset,
              train_subset: dict,
              validation_subset: dict,
              model_configuration: dict,
              context: dl.Context) -> dl.Model:
    """
    Create a new model version from the input model

    :param base_model: model that will be used as a base for the new model.
    :param dataset: dataset that will be used for training the new model.
    :param train_subset: JSON for the DQL filter to get the train items from the given dataset
    :param validation_subset: JSON for the DQL filter to get the validation items from the given dataset
    :param model_configuration: JSON for model configurations (default is from the original model)
    :param context: IDs and other entities related to the item
    :return: new_model (dl.Model), a clone of the base model with the specified parameters.
    """
    print(f"train subset: {train_subset}")
    print(f"validation subset: {validation_subset}")
    print(f"model config: {model_configuration}")

    logging.info(f'Creating new model from {base_model.name}.')

    node = context.node
    input_name = node.metadata['customNodeConfig']['modelName']

    # TODO update when model naming format is decided
    model = base_model
    # input_name = "{model.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"  # debug
    new_name = input_name
    while '{' in new_name:
        name_start, name_end = new_name.split('{', 1)
        executable_name, name_end = name_end.split('}', 1)
        exec_var = eval(executable_name)
        new_name = name_start + exec_var + name_end

    new_dataset = dataset if dataset else base_model.dataset
    new_project = new_dataset.project

    new_configuration = model_configuration if model_configuration else base_model.configuration

    train_filter = dl.Filters(custom_filter=train_subset)
    validation_filter = dl.Filters(custom_filter=validation_subset)

    # try creating model clone with the given name, if it fails, add a number to the end of the name and try again
    i = 1
    while i != 0:
        try:
            new_model = base_model.clone(
                model_name=new_name,
                project_id=new_project.id,
                dataset=new_dataset,
                configuration=new_configuration,
                train_filter=train_filter,
                validation_filter=validation_filter,
                status='created'
            )
            break
        except dl.exceptions.BadRequest:
            new_name = f'{new_name}_{i}'
            i += 1

    # TODO: will be redundant once the clone function is fixed
    # new_model.output_type = base_model.output_type
    new_model.update()

    logging.info(f'New model {new_model.name} created from {base_model.name}.')
    return new_model
