#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import numpy as np
from skimage import io
from skimage import filter
from skimage import measure
from skimage.morphology import disk
# from random import randint


CONFIDENCE_INTERVAL = 0.1
THRESHOLD_LEVEL = 0.4


def perfect_six(args):
    return {'perfect_for_corner': [1.0, 1.6, 1.88, 2.0, 2.56], 'perfect_for_side': [1.0, 1.0, 1.6, 1.88, 1.88]}


def perfect_five(args):
    return {'perfect_for_corner': [1.0, 1.41, 1.41, 2.0], 'perfect_for_center': [1.0, 1.0, 1.0, 1.0]}


def perfect_four(args):
    return {'perfect_for_corner': [1.0, 1.0, 1.41]}


def perfect_three(args):
    return {'perfect_for_corner': [1.0, 2.0], 'perfect_for_center': [1.0, 1.0]}


def perfect_two(r):
    return {'perfect_for_corner': [8.0*r[0]]}


def threshold(image):
    for i in range(len(image)):
        for j in range(len(image[i])):
            if image[i][j] < THRESHOLD_LEVEL:
                image[i][j] = 0
            else:
                image[i][j] = 1
    return image


def convert_image(image):
    image = threshold(image)
    image = filter.rank.median(image, disk(18))
    return image


def load_image(i):
    try:
        if i < 10:
            image = io.imread('kostki_ex/' + 'kostka_0' + str(i) + '.JPG', as_grey=True)
        else:
            image = io.imread('kostki_ex/' + 'kostka_' + str(i) + '.JPG', as_grey=True)
        return image
    except FileNotFoundError:
        blank_image = np.zeros((50, 50), np.uint8)
        return blank_image


def load_all_from_range(start, end):
    images = []
    for i in range(start, end):
        image = load_image(i)
        images.append(image)
    return images


def circle_center(contour):
    x = 0
    y = 0
    for i in range(len(contour)):
        x += contour[i][0]
        y += contour[i][1]
    return [x/len(contour), y/len(contour)]


def point_distance(point1, point2):
    return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2))


def avg_radius(contour, center):
    r = 0
    for i in range(len(contour)):
        r += point_distance(contour[i], center)
    return r/len(contour)


def check_circle(contour, center, avgr):
    hits = 0
    for i in range(len(contour)):
        r = point_distance(contour[i], center)
        if avgr + 0.1*avgr >= r >= avgr - 0.1*avgr:
            hits += 1
    return hits/len(contour)


def draw_contours(image):
    contours = measure.find_contours(image, level=0)

    sum_shape = 0.0
    for n, contour in enumerate(contours):
        sum_shape += contour.shape[0]
    avg = sum_shape/len(contours)

    circles = []
    radius = []

    for n, contour in enumerate(contours):
        cc = circle_center(contour)
        average_radius = avg_radius(contour, cc)
        accuracy = check_circle(contour, cc, average_radius)
        if accuracy > 0.95:
            circles.append(cc)
            radius.append(average_radius)

    return circles, radius


def unified_length_to_rest(circles_list):
    result = []
    for center in circles_list[1:]:
        result.append(point_distance(circles_list[0], center))
    return sorted([x/min(result) for x in result])


def arrays_probably_match(length, perfect_values, param):
    for i, distance in enumerate(length):
        if abs(distance - perfect_values[i]) > param:
            return 0
    return 1


def are_proper_dice_configuration(circles, function, radius_list=None):
    if radius_list is not None:
        length = point_distance(circles[0], circles[1])
    else:
        length = unified_length_to_rest(circles)
    print('Długości: ', length)
    for n, schema in function(radius_list).items():
        print('Długości idealne: ', schema)
        if arrays_probably_match(schema, length, CONFIDENCE_INTERVAL):
            return 1
    return 0


def get_from_binary_coded(circles, binary, radius_list=None):
    result = []
    if radius_list is not None:
        for index, char in enumerate(reversed(binary)):
            if char == '1':
                result.append(radius_list[len(radius_list)-(index + 1)])
    else:
        for index, char in enumerate(reversed(binary)):
            if char == '1':
                result.append(circles[len(circles)-(index + 1)])
    return result


def check_radius(circles, binary, radius_list):
    return get_from_binary_coded(circles, binary, radius_list)


def find_configuration(circles, param, function, radius_list=None):
    if len(circles) < param:
        return 0

    for i in range(0, (2**len(circles))):
        if bin(i).count('1') == param:
            if param == 2 and radius_list is not None:
                if are_proper_dice_configuration(get_from_binary_coded(circles, bin(i)), function, check_radius(circles, bin(i), radius_list)):
                    return 1
            elif are_proper_dice_configuration(get_from_binary_coded(circles, bin(i)), function):
                return 1
    return 0


def print_result(res):
    print('Wynik: ', res)


def option(opt):
    return {
        '2': perfect_two,
        '3': perfect_three,
        '4': perfect_four,
        '5': perfect_five,
        '6': perfect_six
    }[opt]


def main():
    image = load_image(5)
    image = convert_image(image)
    circles, radius_list = draw_contours(image)
    print('Kontury: ', len(circles))
    for i in range(6, 0):
        if i == 1:
            print_result(i)
        elif i == 2:
            if find_configuration(circles, 2, option(i), radius_list):
                print_result(i)
                break
        elif find_configuration(circles, i, option(i)):
            print_result(i)
            break
    exit(0)


if __name__ == '__main__':
    main()
