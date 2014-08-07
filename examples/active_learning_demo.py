# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

"""
Demonstrate Wabbit Wappa by learning to tell capital letters from lowercase.


by Michael J.T. O'Kelly, 2014-04-02
"""

import string
import random
import time

from wabbit_wappa import *


NUM_SAMPLES = 9


def get_example():
    """Make an example for training and testing.  Outputs a tuple
    (label, features) where label is +1 if capital letters are the majority,
    and -1 otherwise; and features is a list of letters.
    """
    features = random.sample(string.ascii_letters, NUM_SAMPLES)
    num_capitalized = len([ letter for letter in features if letter in string.ascii_uppercase ])
    num_lowercase = len([ letter for letter in features if letter in string.ascii_lowercase ])
    if num_capitalized > num_lowercase:
        label = 1
    else:
        label = -1
    return (label, features)

MELLOWNESS=0.1

print("Start a Vowpal Wabbit learner in logistic regression mode")
print("Active Learning mellowness:", MELLOWNESS)
vw = VW(loss_function='logistic', active_mode=True, active_mellowness=MELLOWNESS)
print("""vw = VW(loss_function='logistic')""")
# Print the command line used for the VW process
print("VW command:", vw.command)
print()

print("Now generate 10 training examples, feeding them to VW one by one.")
for i in range(10):
    label, features = get_example()
    if label > 0:
        print("Label {}: {} is mostly uppercase".format(label, features))
    else:
        print("Label {}: {} is mostly lowercase".format(label, features))
    vw.send_example(label, features=features)
print()

print("How well trained is our model?  Let's make 100 tests.")
num_tests = 100
num_good_tests = 0
for i in range(num_tests):
    label, features = get_example()
    # Give the features to the model, witholding the label
    response = vw.get_prediction(features)
    prediction, importance = response.prediction, response.importance
    # Test whether the floating-point prediction is in the right direction
    if prediction * label > 0:
        num_good_tests += 1
print("Correctly predicted", num_good_tests, "out of", num_tests)
print()

print("Let's generate 1,000 more samples for training, sending labels only for those the Active Learner marks as important")
important_example_count = 0
for i in range(1000):
    label, features = get_example()
    response = vw.get_prediction(features)
    if response.importance >= 1.:
        print("Training with example {}, importance {}: {}".format(i, response.importance, features))
        vw.send_example(label, features=features)
        important_example_count += 1
print("Found", important_example_count, "important examples")
print()

print("Now how good are our predictions?")
num_tests = 100
num_good_tests = 0
for i in range(num_tests):
    label, features = get_example()
    # Give the features to the model, witholding the label
    response = vw.get_prediction(features)
    prediction, importance = response.prediction, response.importance
    # Test whether the floating-point prediction is in the right direction
    if prediction * label > 0:
        num_good_tests += 1
print("Correctly predicted", num_good_tests, "out of", num_tests)
print()

print("How fast can we train and test?")
num_examples = 10000
# Generate examples ahead of time so we don't measure that overhead
examples = [ get_example() for i in range(num_examples) ]
print("Training on", num_examples, "examples...")
important_example_count = 0
start_time = time.time()
for example in examples:
    label, features = example
    response = vw.get_prediction(features)
    if response.importance >= 1:
        vw.send_example(label, features=features)
        important_example_count += 1
print("Found", important_example_count, "important examples")
duration = time.time() - start_time
frequency = num_examples / duration
print("Trained", frequency, "examples per second")

start_time = time.time()
print("Testing on", num_examples, "examples...")
for example in examples:
    label, features = example
    # Give the features to the model, witholding the label
    response = vw.get_prediction(features)
    prediction, importance = response.prediction, response.importance
    # if importance > 0:
    #     print label, importance, features
duration = time.time() - start_time
frequency = num_examples / duration
print("Tested", frequency, "examples per second")
