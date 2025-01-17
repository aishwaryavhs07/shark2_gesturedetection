'''

You can modify the parameters, return values and data structures used in every function if it conflicts with your
coding style or you want to accelerate your code.

You can also import packages you want.

But please do not change the basic structure of this file including the function names. It is not recommended to merge
functions, otherwise it will be hard for TAs to grade your code. However, you can add helper function if necessary.

'''
from __future__ import division
from flask import Flask, request
from flask import render_template
from numpy import nan
from scipy.interpolate import interp1d
import time
import json
import numpy as np
import math


app = Flask(__name__)

# Centroids of 26 keys
centroids_X = [50, 205, 135, 120, 100, 155, 190, 225, 275, 260, 295, 330, 275, 240, 310, 345, 30, 135, 85, 170, 240, 170, 65, 100, 205, 65]
centroids_Y = [85, 120, 120, 85, 50, 85, 85, 85, 50, 85, 85, 85, 120, 120, 50, 50, 50, 50, 85, 50, 50, 120, 50, 120, 50, 120]

# Pre-process the dictionary and get templates of 10000 words
words, probabilities = [], {}
template_points_X, template_points_Y = [], []
file = open('words_10000.txt')
content = file.read()
file.close()
content = content.split('\n')
for line in content:
    line = line.split('\t')
    words.append(line[0])
    probabilities[line[0]] = float(line[2])
    template_points_X.append([])
    template_points_Y.append([])
    for c in line[0]:
        template_points_X[-1].append(centroids_X[ord(c) - 97])
        template_points_Y[-1].append(centroids_Y[ord(c) - 97])

def distance(x1,y1,x2,y2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist

def generate_sample_points(points_X, points_Y):
    '''Generate 100 sampled points for a gesture.

    In this function, we should convert every gesture or template to a set of 100 points, such that we can compare
    the input gesture and a template computationally.

    :param points_X: A list of X-axis values of a gesture.
    :param points_Y: A list of Y-axis values of a gesture.

    :return:
        sample_points_X: A list of X-axis values of a gesture after sampling, containing 100 elements.
        sample_points_Y: A list of Y-axis values of a gesture after sampling, containing 100 elements.
    '''
    sample_points_X, sample_points_Y = [], []
    dist= np.sqrt(np.ediff1d(points_X,to_begin=0) **2 + np.ediff1d(points_Y,to_begin=0) **2 )
    dist= np.cumsum(dist)
    dist=dist/dist[-1]
    xnext= interp1d(dist,points_X)
    ynext=interp1d(dist,points_Y)
    samples= np.linspace(0,1,100)
    sample_points_X=xnext(samples)
    sample_points_Y=ynext(samples)
    sample_points_X=sample_points_X.tolist()
    sample_points_Y=sample_points_Y.tolist()
    if points_X[0] == nan:
        sample_points_X[0][0]=points_X[0][0]
    if points_Y[0] == nan:
        sample_points_Y[0][0]= points_Y[0][0]

    return sample_points_X, sample_points_Y


# Pre-sample every template
template_sample_points_X, template_sample_points_Y = [], []
for i in range(10000):
    X, Y = generate_sample_points(template_points_X[i], template_points_Y[i])
    template_sample_points_X.append(X)
    template_sample_points_Y.append(Y)


def do_pruning(gesture_points_X, gesture_points_Y, template_sample_points_X, template_sample_points_Y):
    '''Do pruning on the dictionary of 10000 words.

    In this function, we use the pruning method described in the paper (or any other method you consider it reasonable)
    to narrow down the number of valid words so that the ambiguity can be avoided to some extent.

    :param gesture_points_X: A list of X-axis values of input gesture points, which has 100 values since we have
        sampled 100 points.
    :param gesture_points_Y: A list of Y-axis values of input gesture points, which has 100 values since we have
        sampled 100 points.
    :param template_sample_points_X: 2D list, containing X-axis values of every template (10000 templates in total).
        Each of the elements is a 1D list and has the length of 100.
    :param template_sample_points_Y: 2D list, containing Y-axis values of every template (10000 templates in total).
        Each of the elements is a 1D list and has the length of 100.

    :return:
        valid_words: A list of valid words after pruning.
        valid_probabilities: The corresponding probabilities of valid_words.
        valid_template_sample_points_X: 2D list, the corresponding X-axis values of valid_words. Each of the elements
            is a 1D list and has the length of 100.
        valid_template_sample_points_Y: 2D list, the corresponding Y-axis values of valid_words. Each of the elements
            is a 1D list and has the length of 100.
    '''

    valid_words, valid_template_sample_points_X, valid_template_sample_points_Y = [], [], []
    # TODO: Set your own pruning threshold
    threshold = 20
    xg1 = gesture_points_X[0]
    xg2 = gesture_points_X[-1]
    yg1 = gesture_points_Y[0]
    yg2 = gesture_points_Y[-1]
    for j in range(10000):
        xs = template_sample_points_X[j][0]  # template start x coord
        ys = template_sample_points_Y[j][0]  # template start y coord
        xe = template_sample_points_X[j][99]  # template end x coord
        ye = template_sample_points_Y[j][99]  # template end y coord
        startdist = np.sqrt((xs - xg1)**2 +(ys - yg1)**2)
        enddist = np.sqrt((xe - xg2) ** 2 + (ye - yg2) ** 2)
        if startdist <= threshold and enddist <= threshold:
            valid_template_sample_points_X.append(template_sample_points_X[j])
            valid_template_sample_points_Y.append(template_sample_points_Y[j])
            valid_words.append(words[j])

    return valid_words, valid_template_sample_points_X, valid_template_sample_points_Y



def get_shape_scores(gesture_sample_points_X, gesture_sample_points_Y, valid_template_sample_points_X, valid_template_sample_points_Y):
    '''Get the shape score for every valid word after pruning.

    In this function, we should compare the sampled input gesture (containing 100 points) with every single valid
    template (containing 100 points) and give each of them a shape score.

    :param gesture_sample_points_X: A list of X-axis values of input gesture points, which has 100 values since we
        have sampled 100 points.
    :param gesture_sample_points_Y: A list of Y-axis values of input gesture points, which has 100 values since we
        have sampled 100 points.
    :param valid_template_sample_points_X: 2D list, containing X-axis values of every valid template. Each of the
        elements is a 1D list and has the length of 100.
    :param valid_template_sample_points_Y: 2D list, containing Y-axis values of every valid template. Each of the
        elements is a 1D list and has the length of 100.

    :return:
        A list of shape scores.
    '''
    shape_scores = []
    # TODO: Set your own L
    L = 1
    width= max(gesture_sample_points_X)-min(gesture_sample_points_X)
    height=max(gesture_sample_points_Y)-min(gesture_sample_points_Y)
    scale= L/max(width,height)
    #normalizing gesture points
    gesture_sample_points_X= np.array(gesture_sample_points_X)*scale
    gesture_sample_points_Y = np.array(gesture_sample_points_Y) * scale
    for i in range(len(valid_template_sample_points_X)):
        widthtemp=max(valid_template_sample_points_X[i])-min(valid_template_sample_points_X[i])
        heighttemp=max(valid_template_sample_points_Y[i])-min(valid_template_sample_points_Y[i])
        scaletemp = L / max(widthtemp, heighttemp)
        #normalizing template points
        valid_template_sample_points_X[i]=np.array(valid_template_sample_points_X[i])*scaletemp
        valid_template_sample_points_Y[i] = np.array(valid_template_sample_points_Y[i]) * scaletemp
        xdiff = valid_template_sample_points_X[i] - gesture_sample_points_X
        ydiff = valid_template_sample_points_Y[i] - gesture_sample_points_Y
        dist = np.sqrt(xdiff ** 2 + ydiff ** 2)
        shape_scores.append(np.sum(dist) / 100)

    # TODO: Calculate shape scores (12 points)

    return shape_scores



def get_location_scores(gesture_sample_points_X, gesture_sample_points_Y, valid_template_sample_points_X, valid_template_sample_points_Y):
    '''Get the location score for every valid word after pruning.

    In this function, we should compare the sampled user gesture (containing 100 points) with every single valid
    template (containing 100 points) and give each of them a location score.

    :param gesture_sample_points_X: A list of X-axis values of input gesture points, which has 100 values since we
        have sampled 100 points.
    :param gesture_sample_points_Y: A list of Y-axis values of input gesture points, which has 100 values since we
        have sampled 100 points.
    :param template_sample_points_X: 2D list, containing X-axis values of every valid template. Each of the
        elements is a 1D list and has the length of 100.
    :param template_sample_points_Y: 2D list, containing Y-axis values of every valid template. Each of the
        elements is a 1D list and has the length of 100.

    :return:
        A list of location scores.
    '''
    location_scores = []
    radius = 15
    gesture_sample_points_X = (np.array(gesture_sample_points_X))
    gesture_sample_points_Y = (np.array(gesture_sample_points_Y))
    for i in range(len(valid_template_sample_points_X)):
        valid_template_sample_points_X[i] = (np.array(valid_template_sample_points_X[i]))
        valid_template_sample_points_Y[i] = (np.array(valid_template_sample_points_Y[i]))
        res = np.array([])
        for j in range(100):
            xdiff = valid_template_sample_points_X[i] - gesture_sample_points_X[j]
            ydiff = valid_template_sample_points_Y[i] - gesture_sample_points_Y[j]
            dist = np.sqrt(xdiff ** 2 + ydiff ** 2)
            min_dis = np.min(dist)
            np.append(res, max(min_dis - radius, 0))
        res = np.sum(res)
        res1 = np.array([])
        for k in range(100):
            xdiff = valid_template_sample_points_X[i][k] - gesture_sample_points_X
            ydiff = valid_template_sample_points_Y[i][k] - gesture_sample_points_Y
            dist = np.sqrt(xdiff ** 2 + ydiff ** 2)
            min_dis = np.min(dist)
            np.append(res1, max(min_dis - radius, 0))
        res1 = np.sum(res1)
        xdiff = valid_template_sample_points_X[i] - gesture_sample_points_X
        ydiff = valid_template_sample_points_Y[i] - gesture_sample_points_Y
        dist = np.sqrt(xdiff ** 2 + ydiff ** 2)
        delta = dist
        for var in range(100):
            if res1 == 0 and res == 0:
                delta[var] = 0
        a1 = np.linspace(1/50, 0, 50).tolist()
        a2 = np.linspace(0, 1 / 50, 50).tolist()
        alpha = a1 + a2
        alpha = np.array(alpha)
        loc = np.sum(alpha * delta)
        location_scores.append(loc)
    return location_scores


def get_integration_scores(shape_scores, location_scores):
    integration_scores = []
    # TODO: Set your own shape weight
    shape_coef = 0.5
    # TODO: Set your own location weight
    location_coef = 0.5
    for i in range(len(shape_scores)):
        integration_scores.append(shape_coef * shape_scores[i] + location_coef * location_scores[i])
    return integration_scores


def get_best_word(valid_words, integration_scores):
    '''Get the best word.

    In this function, you should select top-n words with the highest integration scores and then use their corresponding
    probability (stored in variable "probabilities") as weight. The word with the highest weighted integration score is
    exactly the word we want.

    :param valid_words: A list of valid words.
    :param integration_scores: A list of corresponding integration scores of valid_words.
    :return: The most probable word suggested to the user.
    '''
    best_word = ''
    # TODO: Set your own range.
    n = 3
    # TODO: Get the best word (12 points)
    sortmin = [i for i, x in enumerate(integration_scores) if x == min(integration_scores)]
    for i in sortmin:
        best_word += valid_words[i] + ' '

    return best_word[:-1]


@app.route("/")
def init():
    return render_template('index.html')


@app.route('/shark2', methods=['POST'])
def shark2():

    start_time = time.time()
    data = json.loads(request.get_data())

    gesture_points_X = []
    gesture_points_Y = []
    for i in range(len(data)):
        gesture_points_X.append(data[i]['x'])
        gesture_points_Y.append(data[i]['y'])
    #gesture_points_X = [gesture_points_X]
    #gesture_points_Y = [gesture_points_Y]

    gesture_sample_points_X, gesture_sample_points_Y = generate_sample_points(gesture_points_X, gesture_points_Y)

    valid_words, valid_template_sample_points_X, valid_template_sample_points_Y = do_pruning(gesture_points_X, gesture_points_Y, template_sample_points_X, template_sample_points_Y)

    shape_scores = get_shape_scores(gesture_sample_points_X, gesture_sample_points_Y, valid_template_sample_points_X, valid_template_sample_points_Y)

    location_scores = get_location_scores(gesture_sample_points_X, gesture_sample_points_Y, valid_template_sample_points_X, valid_template_sample_points_Y)

    integration_scores = get_integration_scores(shape_scores, location_scores)

    best_word = get_best_word(valid_words, integration_scores)

    end_time = time.time()

    return '{"best_word":"' + best_word + '", "elapsed_time":"' + str(round((end_time - start_time) * 1000, 5)) + 'ms"}'


if __name__ == "__main__":
    app.run()
