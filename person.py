import math
import random as r
import rssi
import config
import numpy

PERSON_UPDATE_MULTIPLIER = 5

CM_PER_SEC = 70


class Person:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.to_reset = True

        # self.vx = r.random() * 2 - 1
        # self.vy = r.random() * 2 - 1

        # length = math.sqrt(math.pow(self.vx, 2) + math.pow(self.vy, 2))
        # speed = CM_PER_SEC / 100 / (PERSON_UPDATE_MULTIPLIER * (1 / rssi.DELAY))

        # self.vx = self.vx / length * speed
        # self.vy = self.vy / length * speed

    def update(self):
        if self.x < 4 or self.x > config.M_WIDTH - 5:
            self.vx = -self.vx

        if self.y < 4 or self.y > config.M_HEIGHT - 5:
            self.vy = -self.vy

        self.x = self.x + self.vx
        self.y = self.y + self.vy

    def walk_along_path(self, path, side_length):
        if len(path) == 0:
            return path

        if (self.to_reset):
            self.to_reset = False
            self.x, self.y = path[0][0][0], path[0][0][1]
            return path[1:]

        screen_factor = config.SCREEN_W / 1300
        speed = CM_PER_SEC / side_length / (PERSON_UPDATE_MULTIPLIER * (1 / rssi.DELAY)) * screen_factor

        best = [[], -1]
        for i, p in enumerate(path):
            dist = math.dist((self.x, self.y), p[0])

            if dist > speed:
                path = path[i:]
                break

        move_vector = (path[0][0][0] - self.x, path[0][0][1] - self.y)
        move_vector = move_vector / numpy.linalg.norm(move_vector)
        move_vector = move_vector * speed

        self.x += move_vector[0]
        self.y += move_vector[1]

        if len(path) <= 10:
            path.clear()
            self.to_reset = True

        # return path
        return path
