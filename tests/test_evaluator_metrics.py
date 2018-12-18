import pytest
from unittest import mock
from tf_yarn.evaluator_metrics import EvaluatorMetricsLogger
import tf_yarn

MONITORED_METRICS_MOCK = {
    'metric1': 'metric1 description',
    'metric2': 'metric2 description'
}

evaluator_list = ['eval1', 'eval2']

kv_stores = [
    {'eval1/metric1': b'0.9', 'eval1/metric2': b'13.0',
     'eval2/metric1': b'5.0', 'eval2/metric2': b'16.0'},
    {'eval1/metric1': b'0.9', 'eval1/metric2': b'13.0',
     'eval2/metric1': b'13.0', 'eval2/metric2': b'26.0'},
    {'eval1/metric1': b'0.9', 'eval1/metric2': b'13.0',
     'eval2/metric1': b'13.0', 'eval2/metric2': b'26.0'},
    {'eval1/metric1': b'0.9', 'eval1/metric2': b'13.0',
     'eval2/metric1': b'13.0', 'eval2/metric2': b'26.0'},
    {'eval1/metric1': b'0.9', 'eval1/metric2': b'13.0',
     'eval2/metric1': b'13.0', 'eval2/metric2': b'26.0'}
]

last_metrics_list = [
    {'eval1': {'metric1': None, 'metric2': None},
     'eval2': {'metric1': None, 'metric2': None}},
    {'eval1': {'metric1': 0.9, 'metric2': 13.0},
     'eval2': {'metric1': 5.0, 'metric2': 16.0}},
    {'eval1': {'metric1': None, 'metric2': None},
     'eval2': {'metric1': None, 'metric2': None}},
    {'eval1': {'metric1': None, 'metric2': None},
     'eval2': {'metric1': None, 'metric2': None}},
    {'eval1': {'metric1': None, 'metric2': None},
     'eval2': {'metric1': None, 'metric2': None}}
]

log_thresholds_list = [
    None, None, {'metric1': (0.0, 1.0), 'metric2': (20.0, None)},
    {'metric1': (None, 1.0)}, {'metric2': (None, None)}
]

logs_list = [
    [((f'Statistics for eval1: metric1 description: 0.9 metric2 description: 13.0',),),
     ((f'Statistics for eval2: metric1 description: 5.0 metric2 description: 16.0',),)],
    [((f'Statistics for eval2: metric1 description: 13.0 metric2 description: 26.0',),)],
    [((f'Statistics for eval1: metric1 description: 0.9',),),
     ((f'Statistics for eval2: metric2 description: 26.0',),)],
    [((f'Statistics for eval1: metric1 description: 0.9 metric2 description: 13.0',),),
     ((f'Statistics for eval2: metric2 description: 26.0',),)],
    [((f'Statistics for eval1: metric1 description: 0.9 metric2 description: 13.0',),),
     ((f'Statistics for eval2: metric1 description: 13.0 metric2 description: 26.0',),)]
]


@pytest.mark.parametrize(
    "kv_store,last_metrics,log_thresholds,logs",
    zip(kv_stores, last_metrics_list, log_thresholds_list, logs_list)
)
def test_log(kv_store, last_metrics, log_thresholds, logs):
    tf_yarn.evaluator_metrics.MONITORED_METRICS = MONITORED_METRICS_MOCK

    def skein_kv_get(self, key):
        print(key)
        return kv_store.get(key)

    with mock.patch('tf_yarn.evaluator_metrics.skein.ApplicationClient') as skein_app_mock,\
            mock.patch('tf_yarn.evaluator_metrics.logger') as logger_mock:
        skein_app_mock.kv = kv_store
        evaluator_metrics_logger = EvaluatorMetricsLogger(
            evaluator_list,
            skein_app_mock,
            log_thresholds=log_thresholds
        )
        evaluator_metrics_logger.last_metrics = last_metrics
        evaluator_metrics_logger.log()
        assert logger_mock.info.call_args_list == logs
