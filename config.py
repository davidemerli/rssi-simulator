import numpy
import json

tiles = ['empty', 'antenna', 'inner_wall', 'perimeter_wall', 'inn_wall_antenna', 'perim_wall_antenna']
colors = {'empty': 'light grey', 'antenna': 'light green', 'inner_wall': 'grey', 'perimeter_wall': 'black'}

M_WIDTH, M_HEIGHT = 0, 0
SCREEN_W, SCREEN_H = 700, 700
MATRIX = [[]]
SIDE_LENGTH = 1

STOP_AT = 5000

DEBUG_CIRCLES = True


def index_to_coords(index):
    return index % M_WIDTH, index // M_WIDTH


def coords_to_index(x, y):
    return x + (y * M_WIDTH)


def coords_to_circle(x, y):
    W, H = SCREEN_W // M_WIDTH, SCREEN_H // M_HEIGHT
    cx, cy = x * W + W // 4, y * H + H // 4

    return cx, cy, cx + W - W // 4, cy + H - H // 4


def read_map(input_file):
    with open(input_file) as text_map:
        global MATRIX, M_WIDTH, M_HEIGHT, SIDE_LENGTH

        lines = [line.strip() for line in text_map.readlines() if line != '\n']
        SIDE_LENGTH = int(lines.pop().split(':')[1])

        M_WIDTH, M_HEIGHT = len(lines[0]), len(lines)
        MATRIX = [[0 for _ in range(M_HEIGHT)] for _ in range(M_WIDTH)]

        for y in range(M_HEIGHT):
            line = lines[y]
            for x in range(M_WIDTH):
                MATRIX[x][y] = int(line[x])

        print(M_WIDTH, M_HEIGHT)
        print('Side length:', SIDE_LENGTH)
        print(numpy.asarray(MATRIX))


def print_map(input_file):
    with open(input_file, 'w') as text_map:
        for y in range(M_HEIGHT):
            for x in range(M_WIDTH):
                text_map.write(str(MATRIX[x][y]))
            text_map.write('\n')


def read_saved_matrix():
    with open('matrix.json', 'r') as data:
        return json.loads(data.read())


def save_matrix(m):
    with open('matrix.json', 'w') as data:
        data.write(json.dumps(m))
