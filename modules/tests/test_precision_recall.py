import json
import dtlpy as dl
import pandas as pd
from dtlpymetrics.scoring import create_model_score
from dtlpymetrics.precision_recall import plot_precision_recall
from modules.model_evaluation import evaluator

dl.setenv('new-dev')
filename = r"C:\Users\Yaya\PycharmProjects\APPS\active-learning\.dataloop\649076c45a9c968a5c32ed65.csv"

model = dl.models.get(None, '649076c45a9c968a5c32ed65')
dataset = model.dataset

# ## test the model scoring
# success, response = create_model_score(model=model,
#                                                          dataset=dataset,
#                                                          filters=filters,
#                                                          compare_types=[model.output_type])


data = pd.read_csv(filename)

plot = plot_precision_recall(scores=data)

print()
