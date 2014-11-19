
import random
import os
import time

from wabbit_wappa import *


def test_namespace():
    namespace = Namespace('MetricFeatures', 3.28, [('height', 1.5), ('length', 2.0), 'apple', '1948'])
    namespace_string = namespace.to_string()
    assert namespace_string == 'MetricFeatures:3.28 height:1.5 length:2.0 apple 1948 '

    namespace = Namespace(None, 3.28, ['height', 'length'])
    namespace_string = namespace.to_string()
    assert namespace_string == ' height length '


def test_validation():
    try:
        namespace = Namespace('Metric Features', 3.28, [('height|', 1.5), ('len:gth', 2.0)],
                              escape=False)
    except WabbitInvalidCharacter:
        pass  # This is the correct behavior
    else:
        assert False, "to_string() should error out for these inputs when escape==False"


def test_escaping():
    namespace = Namespace('Metric Features', 3.28, [('height|', 1.5), ('len:gth', 2.0)])
    namespace_string = namespace.to_string()
    assert 'Metric Features' not in namespace_string
    assert '|' not in namespace_string
    assert 'len:gth' not in namespace_string


def test_command():
    command = make_command_line(predictions='/dev/stdout',
                                quiet=True,
                                save_resume=True,
                                compressed=True,
                                q_colon=['a', 'b'],
                                b=20,
                                )
    # Test that command has all expected elements
    assert 'vw ' in command
    assert '--predictions /dev/stdout' in command
    assert '--quiet' in command
    assert '--save_resume' in command
    assert '--compressed' in command
    assert '--q: a' in command
    assert '--q: a' in command
    assert '-b 20' in command
    assert '--b 20' not in command
    # Test that VW runs with this command
    vw = VW(command)


def test_training():
    # TODO: pytest probably has a framework for testing hyperparameters like this
    for active_mode in [False, True]:
        vw = VW(loss_function='logistic', active_mode=active_mode)
        # Train with an easy case
        for i in range(20):
            # Positive example
            vw.send_example(response=1.,
                            importance=2.,
                            tag='positive',
                            features=[('a', 1 + random.random()),
                                      ('b', -1 - random.random())]
                            )
            vw.send_example(response=-1.,
                            importance=.5,
                            tag='negative',
                            features=[('lungfish', 1 + random.random()),
                                      ('palooka', -1 - random.random())]
                            )
        prediction1 = vw.get_prediction([('a', 1),
                                        ('b', -2)]).prediction
        # Prediction should be definitively positive
        assert prediction1 > 1.
        prediction2 = vw.get_prediction([('lungfish', 3)]).prediction
        # Prediction should be negative
        assert prediction2 < 0
        prediction3 = vw.get_prediction([('a', 1),
                                        ('b', -2)]).prediction
        # Making predictions shouldn't affect the trained model
        assert prediction1 == prediction3

        # Continue training with very different examples
        for i in range(20):
            # Positive example
            vw.add_namespace('space1',
                             1.0,
                             ['X', 'Y', 'Z'],
                             )
            vw.send_example(response=1.)
            # Negative example
            vw.add_namespace('space2',
                             2.0,
                             ['X', 'Y', 'Z'],
                             )
            vw.send_example(response=-1.)
        vw.add_namespace('space1',
                         1.0,
                         ['X'],
                         )
        prediction4 = vw.get_prediction().prediction
        # Prediction should be positive
        assert prediction4 > 0
        vw.add_namespace('space2',
                         1.0,
                         ['X'],
                         )
        prediction5 = vw.get_prediction().prediction
        # Prediction should be negative
        assert prediction5 < 0

        # Save the model to a temporary file
        filename = '__temp.model'
        vw.save_model(filename)
        # This sleep is required only in active_mode, in the (unusual) case
        # that the model file is used immediately
        time.sleep(0.1)

        # Load a new VW instance from that model
        vw2 = VW(loss_function='logistic', i=filename)
        # Make the same prediction with each model (testing cache_string to boot)
        namespace1 = Namespace(features=[('a', 1), ('b', -2)], cache_string=True)
        namespace2 = Namespace('space1', 1.0, ['X', 'Y'], cache_string=True)
        prediction1 = vw.get_prediction(namespaces=[namespace1, namespace2]).prediction
        prediction2 = vw2.get_prediction(namespaces=[namespace1, namespace2]).prediction
        assert prediction1 == prediction2
        assert prediction1 > 1.

        # Clean up
        vw.close()
        vw2.close()
        os.remove(filename)


def test_daemons():
    # Launch one VW in daemon_mode
    vw = VW(loss_function='logistic', daemon_mode=True, port=30000)
    # Connect to that one without launching another
    vw2 = VW(daemon_ip='127.0.0.1', port=30000)


