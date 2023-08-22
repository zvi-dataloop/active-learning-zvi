import dtlpy as dl

evaluator = dl.AppModule(name='Model Evaluation', description='My testing')


@evaluator.set_init()
def load_model():
    evaluator.my_custom_model = 'WHAAAAAAAAAAAAAA'
    print('loadinggggg')
    pass


@evaluator.add_function(display_name='Model Evaluation')
def evaluate_model(model: dl.Model, dataset: dl.Dataset = None, query: dict = None) -> str:
    """
    Evaluate and upload metrics (if exists in the model's code)

    """
    print('evaluatinggggggg')
    print(evaluator.my_custom_model)
    print(evaluator.name)
    # adapter = model.build()
    # adapter.evaluate()
    return 'done'


if __name__ == "__main__":
    evaluator.init()
    evaluator.evaluate_model('model')
    import pprint

    pprint.pprint(evaluator.to_json())
