import dtlpy as dl
import numpy as np
import pandas as pd

Comparator = dl.AppModule(name='compare_models',
                          description='Compares two models in relation to a user-specified.'
                                      'metric and attaches a "win" or "lose" action filter.')


@Comparator.set_init()
def setup():
    pass


def metrics_to_df(model: dl.Model) -> pd.DataFrame:
    samples = model.metrics.list().to_df()
    measures = list(samples['legend'].drop_duplicates())
    metrics_df = pd.DataFrame(columns=['iou_threshold', 'model_name', 'label'] + measures)
    metrics_df.set_index(['iou_threshold', 'model_name', 'label'], inplace=True)
    for i, (figure, legend, data) in samples.iterrows():
        metrics_df.loc[(data['x'], model.name, figure), legend] = data['y']
    metrics_df.reset_index(inplace=True)
    return metrics_df


@Comparator.add_function(display_name="Compare Models")
def compare_models(model_1: dl.Model,
                   model_2: dl.Model,
                   comparison_subset: dict,
                   progress: dl.Progress,
                   context: dl.Context) -> dl.Model:
    """
    Compare metrics of two models to determine which is better.

    :param model_1:
    :param model_2:
    :param comparison_subset:
    :param progress:
    :param context:
    :return:
    """
    is_improved = __compare(previous_model_metrics=metrics_to_df(model_1),
                            current_model_metrics=metrics_to_df(model_2),
                            configuration=comparison_subset)
    action = ['win', 'lose']
    progress.update(action=action[0])

    if is_improved:
        model_2.set_action_filter('win')
        model_1.set_action_filter('lose')
        return model_2

    model_1.set_action_filter('win')
    model_2.set_action_filter('lose')
    return model_1


def __compare(previous_model_metrics: pd.DataFrame,
              current_model_metrics: pd.DataFrame,
              configuration: dict) -> bool:
    """
    Using two result.csv files received from YOLOv5 testing process,
    find which of them are more advanced in his detection ability
    :param previous_model_metrics: last testing stage of the model (.csv file name)
    :param current_model_metrics: current testing stage of the model (.csv file name)
    :param configuration:
    :Keyword Arguments:

    ******* SPECIFIC METRIC *******

    * *precision* (``bool``) --
      compare models by *only* Precision metric [default: False]
    * *recall* (``bool``) --
      compare models by *only* Recall metric [default: False]
    * *f1* (``bool``) --
      compare models by *only* f1-measure metric [default: False]
    * *mAP50* (``bool``) --
      compare models by *only* mAP50 metric [default: False]
    * *mAP50_95* (``bool``) --
      compare models by *only* mAP50_95 metric [default: False]
    note: if any metric was not chosen, the calculation takes *everything*

    ******* SETTINGS *******

    * *soft_check* (``function``) --
      require custom comparison function between two columns [default: Python's builtin *any*]
    * *iou_threshold* (``list | float``) --
      perform comparison based on specific (single/boundaries) IoU value [default: everything]
    * *same_pre_model* (``bool``) --
      require that both models were trained from the same source [default: false]
    * *specific_label* (``list``) --
      perform comparison based on specific label [default: everything]
    * *min_delta* (``float``) --
      require minimum difference between the metrics before considering it as improvement [default: 0]
    * *lower_is_better_metrics* (``list``) --
      specify list of metrics which require *decrease* to represent improvement [default: 0]
    * *verbose* (``bool``) --
      stdout tabular information in runtime  [default: False]

    :return: True if the comparison detected any improvement OR equalization, else - False.
    """

    def _compare(_previous: pd.DataFrame, _current: pd.DataFrame, **kwargs):
        assert len(_previous) == len(_current), "Cannot compare non matching sizes," \
                                                " please check testing results file validity."
        delta = kwargs.get("min_delta", 0)
        check = np.any if kwargs.get("soft_check", False) else np.all
        sign = np.negative if kwargs.get("lower_is_better_metrics", False) else np.array
        _diff = _current.values - _previous.values

        # precision:    previous        current
        #               0.5             0.6         ->  0.1
        #               0.4             0.4         ->  0.0
        #               0.3             0.2         -> -0.1

        _comparison_result = check(sign(_diff) >= delta)

        return _comparison_result

    def _verbose(_previous: np.ndarray, _current: np.ndarray, **kwargs):
        print(f'[{idx}] performing comparison on {single_metric_name} metric between:')
        comparison = pd.DataFrame({
            "previous model": _previous,
            "current model": _current
        })
        comparison.columns.name = "TH"
        comparison = comparison.set_axis(axes)
        print(comparison, end='\n\n')

    def _filter(_previous_metric: pd.DataFrame, _current_metric: pd.DataFrame, **kwargs):
        """
        concatenate filtering over the dataFrames before performing metrics comparison
        :param _previous_metric: previous metric table
        :param _current_metric: current metric table
        :param kwargs: filter options
        :return: filtered tables
        """

        def _range_query(table, col, rng):
            return table.loc[table[col].isin(rng)]

        threshold = kwargs.get("iou_threshold", None)
        labels = kwargs.get("specific_label", None)
        metric_name = kwargs.get("metric_name", None)

        if kwargs.get("same_pre_model", False):
            assert set(_previous_metric["premodel"]) == set(_current_metric["premodel"]), \
                "non-matching pre-models detected"

        if threshold:
            # for [0.1, 0.5], numpy will return [0.1 ,..., 0.4]
            _rv = np.arange(*threshold, 0.1) if type(threshold) is list else np.arange(threshold, 1, 0.1)
            _rv = np.round(_rv.astype(np.float64), 1)
            # extract rows matching the range value
            _previous_metric = _range_query(
                _previous_metric, _previous_metric.columns[0], _rv
            )  # _p.loc[_p[_p.columns[0]].isin(_rv)]
            _current_metric = _range_query(_current_metric, _current_metric.columns[0], _rv)

        if labels:
            _previous_metric = _range_query(_previous_metric, "label", labels)  # _p.loc[_p["label"].isin(labels)]
            _current_metric = _range_query(_current_metric, "label", labels)

        # store X axes (to display -- F(threshold)=result -- function)
        _axes = _previous_metric[_previous_metric.columns[0]].values

        if metric_name:
            _previous_metric = _previous_metric[metric_name]
            _current_metric = _current_metric[metric_name]

        return _previous_metric, _current_metric, _axes

    conclusions = []
    previous_sheet = previous_model_metrics
    current_sheet = current_model_metrics
    opt_handlers: dict = {
        "verbose": _verbose,
    }

    for idx, single_metric in enumerate(configuration.items(), start=1):
        if type(single_metric[1]) is dict:
            single_metric_name, config = single_metric
            previous_metric, current_metric, axes = _filter(previous_sheet, current_sheet,
                                                            **{"metric_name": single_metric_name, **config})

            for key in config.keys():
                if config.get(key, False):
                    opt_handlers.get(key, lambda a, b: None)(previous_metric.values, current_metric.values)

            result = _compare(previous_metric, current_metric, **config)
            conclusions.append(result)

    return np.array(conclusions).all()


if __name__ == '__main__':
    hasattr(Comparator, "compare_models")
    import pprint

    pprint.pprint(Comparator.to_json())
