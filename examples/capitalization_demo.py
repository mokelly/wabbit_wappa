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


print("Start a Vowpal Wabbit learner in logistic regression mode")
vw = VW(loss_function='logistic')
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
    prediction = vw.get_prediction(features).prediction
    # Test whether the floating-point prediction is in the right direction (signs agree)
    if label * prediction > 0:
        num_good_tests += 1
print("Correctly predicted", num_good_tests, "out of", num_tests)
print()

print("We can go on training, without restarting the process.  Let's train on 1,000 more examples.")
for i in range(1000):
    label, features = get_example()
    vw.send_example(label, features=features)
print()

print("Now how good are our predictions?")
num_tests = 100
num_good_tests = 0
for i in range(num_tests):
    label, features = get_example()
    # Give the features to the model, witholding the label
    prediction = vw.get_prediction(features).prediction
    # Test whether the floating-point prediction is in the right direction
    if label * prediction > 0:
        num_good_tests += 1
print("Correctly predicted", num_good_tests, "out of", num_tests)
print()
filename = 'capitalization.saved.model'
print("We can save the model at any point in the process.")
print("Saving now to", filename)
vw.save_model(filename)
vw.close()
print()

print("We can reload our model using the 'i' argument:")
vw2 = VW(loss_function='logistic', i=filename)
print("""vw2 = VW(loss_function='logistic', i=filename)""")
print("VW command:", vw2.command)

print("How fast can we train and test?")
num_examples = 10000
# Generate examples ahead of time so we don't measure that overhead
examples = [ get_example() for i in range(num_examples) ]
print("Training on", num_examples, "examples...")
start_time = time.time()
for example in examples:
    label, features = example
    # Turning off parse_result mode speeds up training when we
    # don't care about the result of each example
    vw2.send_example(label, features=features, parse_result=False)
duration = time.time() - start_time
frequency = num_examples / duration
print("Trained", frequency, "examples per second")

start_time = time.time()
print("Testing on", num_examples, "examples...")
for example in examples:
    label, features = example
    # Give the features to the model, witholding the label
    prediction = vw2.get_prediction(features).prediction
duration = time.time() - start_time
frequency = num_examples / duration
print("Tested", frequency, "examples per second")
