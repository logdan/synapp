#!/usr/bin/env python

import numpy as np
import tensorflow as tf
from synapp.core.EEGNet_Modify import EEGNet_SynApp

# Input: model prediction array
# Output: Index/class number of the most confident predicted class
def get_prediction_simple(predictionarray) :
    maxindex = np.argmax(predictionarray)
    if type(maxindex) is np.ndarray:
        maxindex = maxindex[0]

    return maxindex

# Input: model prediction array, and minimum confidence for a class to be predicted
# Output: Index/class number of the most confident predicted class, or default (has to be a possible value)
def get_prediction(prediction_array, minimum_confidence, default) :
    max_index = np.argmax(prediction_array)
    if type(max_index) is np.ndarray:
        max_index = max_index[0]

    confidence_val = prediction_array[max_index]

    if confidence_val < minimum_confidence:
        prediction = max_index
    else:
        # not confident enough - output the default class ("rest")
        prediction = default

    return prediction



def getmodel(num_classes, num_channels, window_length, eegnet=False) :
    if not eegnet :
        model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(num_channels, window_length)),
        tf.keras.layers.Dense(window_length, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
    else:
        model = EEGNet_SynApp(num_classes,num_channels,window_length)

    return model

def reshape_trial_for_model(trial):
    trial = trial[:, 0:4]
    #print(np.shape(trial))
    trial_reshaped = np.reshape(trial, (1, trial.shape[1], trial.shape[0]))
    return trial_reshaped


def getpredicted(prediction, predictionmap=None):
    if predictionmap is None:
        predictionmap = getWinkBlinkPredictionMapping()
    output = predictionmap[prediction]

    return output


def getWinkBlinkPredictionMapping():
    predictionmap = {-1: 'none',
                     0: 'still',
                     1: 'winkright',
                     2: 'winkleft'}
    return predictionmap
