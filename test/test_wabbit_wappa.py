
from wabbit_wappa import *


def test_namespace():
    namespace = Namespace('MetricFeatures', 3.28, [('height', 1.5), ('length', 2.0)])
    namespace_string = namespace.to_string()
    assert namespace_string == 'MetricFeatures:3.28 height:1.5 length:2.0 '

    namespace = Namespace(None, 3.28, ['height', 'length'])
    namespace_string = namespace.to_string()
    assert namespace_string == ' height length '

    namespace = Namespace('Metric Features', 3.28, [('height|', 1.5), ('len:gth', 2.0)])
    namespace_string = namespace.to_string()
    assert 'Metric Features' not in namespace_string
    assert '|' not in namespace_string
    assert 'len:gth' not in namespace_string

