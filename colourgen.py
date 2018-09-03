"""
Small library for generating n amount of distinct colours
Based on https://gist.github.com/adewes/5884820
"""
import random

def get_random_colour(pastel_factor):
    return [
        (x + pastel_factor) / (1.0 + pastel_factor)
        for x in [random.uniform(0, 1) for i in [1, 2, 3]]]


def colour_distance(c1, c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])


def generate_new_colour(existing_colours, pastel_factor):
    max_distance = None
    best_colour = None
    for _ in range(100):
        colour = get_random_colour(pastel_factor)
        if not existing_colours:
            return colour
        best_distance = min([colour_distance(colour, c) for c in existing_colours])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_colour = colour
    return best_colour


def get_rgb_fill(amount):
    colours = []
    rgbs = []
    for _ in range(amount):
        colour = generate_new_colour(colours, pastel_factor=0.9)
        colours.append(colour)
        rgb = (int(colour[0] * 255), int(colour[1] * 255), int(colour[2] * 255), 255)
        rgbs.append(rgb)
    return rgbs
