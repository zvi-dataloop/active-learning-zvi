import dtlpy as dl
from modules import model_compare
from dtlpymetrics import scoring

dl.setenv('rc')

model1 = dl.models.get(model_id='6481a2f4cce96a272025eec9')
model2 = dl.models.get(model_id='6481f19bf18d2526d10af94c')
dataset = model1.dataset

metrics1 = scoring.get_model_scores_df(dataset=dataset, model=model1)
metrics2 = scoring.get_model_scores_df(dataset=dataset, model=model2)

config = {
    "wins": 0.6,
    "checks": [
        {
            "type": "label_score"
        }
    ]
}

model_compare.compare_model_evaluation(metrics1, metrics2, config)

# original example JSON
# {
#   "wins": "any",
#   "checks": [
#     {
#       "type": "plot",
#       "legend": "metrics",
#       "figure": "mAP50(B)",
#       "x_index": -1,
#       "maximize": true,
#       "min_delta": 0.1
#     },
#     {
#       "type": "plot",
#       "legend": "val",
#       "figure": "box_loss",
#       "x_index": -1,
#       "maximize": false,
#       "min_delta": 0.1
#     }
#   ]
# }
