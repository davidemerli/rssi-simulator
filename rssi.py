import numpy
import math
import random
import json

TRANSMITTED_POWER = -4
COUPLING_FACTOR = 1
WAVE_FACTOR = 40

PATH_LOSS_PERIM = -14
PATH_LOSS_INTERNAL = -3

NOISE = (-30, 0)

THRESHOLD = -95
PACKET_LOSS = 0.1

DELAY = 0.3  # seconds

SIM_WINDOW = 3


def load_settings(path):
    """
    Loads the settings from a json file
    """

    with open(path) as f:
        settings = json.loads(f.read())

        global TRANSMITTED_POWER, COUPLING_FACTOR, WAVE_FACTOR, \
            PATH_LOSS_PERIM, PATH_LOSS_INTERNAL, NOISE, THRESHOLD, \
            PACKET_LOSS, DELAY, SIM_WINDOW

        TRANSMITTED_POWER = settings["TRASMITTED_POWER"]
        COUPLING_FACTOR = settings["COUPLING_FACTOR"]
        WAVE_FACTOR = settings["WAVE_FACTOR"]
        PATH_LOSS_PERIM = settings["PATH_LOSS_PERIM"]
        PATH_LOSS_INTERNAL = settings["PATH_LOSS_INTERNAL"]
        NOISE = settings["NOISE"]
        THRESHOLD = settings["THRESHOLD"]
        PACKET_LOSS = settings["PACKET_LOSS"]
        DELAY = settings["DELAY"]
        SIM_WINDOW = settings["SIM_WINDOW"]


def get_distance_from_RSSI(received_RSSI):
    """
    Gets distance given RSSI value
    """

    return 10 ** ((TRANSMITTED_POWER - received_RSSI - WAVE_FACTOR + COUPLING_FACTOR) / 20)


def get_ideal_RSSI(distance, walls=[0, 0]):
    """
    Gets ideal RSSI given distance and wall path loss
    """

    if distance == 0:
        return TRANSMITTED_POWER

    return TRANSMITTED_POWER - WAVE_FACTOR + COUPLING_FACTOR - 20 * math.log10(distance) + walls[1]


def get_error(received, saved_RSSI):
    """
    Generates error given a list of recieved (real) RSSI values and saved ideal RSSI values

    (Works only if both vectors are with the same magnitude)
    """

    return numpy.square(numpy.subtract(received, saved_RSSI)).sum()


def get_error2(received, saved_RSSI):
    """
    Returns absolute error between a received vector of (real) RSSI values and a vector of ideal RSSI values

    Vectors can have different magnitudes, and only received antenna values are confronted
    """

    return sum([pow(r[1] - saved_RSSI[r[0]], 2) for r in received])


def generate_noise():
    """
    Generates a random noise value between given noise constraints
    """

    LAMBDA = abs(NOISE[0] - NOISE[1]) / 2
    value = 1 / (LAMBDA * math.log(random.random()))

    return numpy.clip(value, NOISE[0], NOISE[1])


def is_packet_lost():
    """
    Generates a random float between 0 and 1 and confronts it with PACKET_LOSS value

    Determines if a packet should be considered lost by accident
    """

    return random.random() <= PACKET_LOSS


if __name__ == "__main__":
    load_settings("settings.json")

    print(TRANSMITTED_POWER, COUPLING_FACTOR, WAVE_FACTOR, PATH_LOSS_PERIM, PATH_LOSS_INTERNAL, NOISE, THRESHOLD,
          PACKET_LOSS, DELAY, SIM_WINDOW)

    print(get_ideal_RSSI(100))
