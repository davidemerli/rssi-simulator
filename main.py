from apscheduler.schedulers.background import BackgroundScheduler
from person import Person, PERSON_UPDATE_MULTIPLIER
import random as r
from tkinter import *
import time
from statistics import median, mean
import functools
import config
from config import *
from rssi import *

FRAME = None

ANTENNAS = []
RSSI_MATRIX = [[]]
TILES = []
RECTANGLES = []
SIMULATIONS = []
ERRORS = []
PERSONS = []

WALLS = []

PATH = []

SIDE_LENGTH = 1

sched = BackgroundScheduler(daemon=True, max_instances=2)


def get_antennas():
    """
    Populates the antennas list taking values from the matrix map

    Every antenna is stored as a tuple like (a.x, a.y)
    """

    global ANTENNAS
    ANTENNAS.clear()

    for x in range(config.M_WIDTH):
        for y in range(config.M_HEIGHT):
            antenna_tiles = ['antenna', 'inn_wall_antenna', 'perim_wall_antenna']
            if config.MATRIX[x][y] in [tiles.index(a) for a in antenna_tiles]:
                ANTENNAS.append((x, y))

    return ANTENNAS


def get_walls():
    """
    Populates the walls list taking values from the matrix map

    Every wall is stored as a list with elements like [(a.x, a.y), PATH_LOSS]
    """

    global WALLS
    WALLS.clear()
    wall_tiles = ['inner_wall', 'inn_wall_antenna', 'perimeter_wall', 'perim_wall_antenna']
    wall_tiles = [tiles.index(w) for w in wall_tiles]

    for x in range(config.M_WIDTH):
        for y in range(config.M_HEIGHT):
            if config.MATRIX[x][y] in wall_tiles:
                value = PATH_LOSS_INTERNAL if wall_tiles.index(config.MATRIX[x][y]) in [0, 1] else PATH_LOSS_PERIM
                WALLS.append([(x, y), value])

    return WALLS


def clear_tiles():
    """
    Clears all tiles on the map, for example simulation indication circles   
    """
    for i in TILES:
        FRAME.canvas.delete(i)


@functools.lru_cache()
def get_ideal_RSSI_vectors_matrix():
    """
    Generates and stores in RSSI_MATRIX the current map getting for every point the ideal RSSI that would
    be received by a beacon if it was standing there, 
    """

    global RSSI_MATRIX
    RSSI_MATRIX = [[[] for y in range(config.M_HEIGHT)]
                   for x in range(config.M_WIDTH)]

    print(numpy.asarray(RSSI_MATRIX))

    for x in range(config.M_WIDTH):
        for y in range(config.M_HEIGHT):
            for a in get_antennas():
                dist = math.dist(a, (x, y)) * SIDE_LENGTH
                walls = walls_in_between2(a, (x, y))

                value = get_ideal_RSSI(dist, walls)

                RSSI_MATRIX[x][y].append(value)

            print("calculated", x, y)

    save_matrix(RSSI_MATRIX)

    return RSSI_MATRIX


@functools.lru_cache()
def walls_in_between(pos1: tuple, pos2: tuple):
    """
    Returns wall count between two points and the path loss value
    """
    count = 0
    loss = 0

    for w in get_walls():
        x, y = w[0][0], w[0][1]

        p1 = (x, y)
        p2 = (x + 0.99, y)
        p3 = (x, y + 0.99)
        p4 = (x + 0.99, y + 0.99)

        if intersect(pos1, pos2, p1, p2) \
                or intersect(pos1, pos2, p2, p4) \
                or intersect(pos1, pos2, p3, p4) \
                or intersect(pos1, pos2, p1, p3):
            count += 1
            loss += w[1]

    return count, loss


@functools.lru_cache()
def walls_in_between2(pos1, pos2):
    """
    Returns wall count between two points and the path loss value
    (Alternative lighter version)
    """

    global WALLS

    if len(WALLS) == 0:
        WALLS = get_walls()

    length = int(math.dist(pos1, pos2))

    if pos1 == pos2 or length == 0:
        return 0, 0

    walls = []
    vect = (pos1[0] - pos2[0], pos1[1] - pos2[1])

    def in_wall(p, wall):
        return wall[0] <= p[0] <= wall[0] + 1 and wall[1] <= p[1] <= wall[1] + 1

    points = [(pos1[0] - vect[0] * (i / length), pos1[1] -
               vect[1] * (i / length)) for i in range(length + 1)]

    for W in WALLS:
        for p in points:
            if in_wall(p, W[0]) and W not in walls:
                walls.append(W)

    return len(walls), sum([w[1] for w in walls])


@functools.lru_cache()
def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


@functools.lru_cache()
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def generate_data():
    """
    Generates a vector of RSSI values for every beacon on the map.

    RSSI values are generated for all antennas starting with ideal RSSI value
    Noise is applied, then packet loss percentage

    If the packet is not lost and its power is above the config THRESHOLD, it is
    added to the list.
    """

    rssi_vectors = [((p.x * config.M_WIDTH / SCREEN_W, p.y * config.M_HEIGHT / SCREEN_H), []) for p in PERSONS]

    for i, p in enumerate(PERSONS):
        point = (p.x * config.M_WIDTH / SCREEN_W, p.y * config.M_HEIGHT / SCREEN_H)

        for j, a in enumerate(ANTENNAS):
            walls = walls_in_between(a, point)
            dist = math.dist(a, point) * SIDE_LENGTH
            ideal_RSSI = get_ideal_RSSI(dist, walls)

            value = ideal_RSSI + generate_noise()

            if value > THRESHOLD and not is_packet_lost():
                rssi_vectors[i][1].append((j, value))

    return rssi_vectors


def simulate():
    """     
    Gets generated results from beacons and simulates the three algorithms implemented 

    When done, it displays the guessed locations with different colors 
    """

    time_on_errors = 0

    for data in generate_data():
        beacon = data[0]
        data = data[1]

        data_ = [(d[0], int(d[1])) for d in data]
        data_.sort(reverse=True, key=lambda x: x[1])
        print(data_)

        start_time = time.time()

        if DEBUG_CIRCLES:
            for d in data:
                cx, cy = ANTENNAS[d[0]]
                TILES.append(FRAME.canvas.create_oval(*coords_to_circle(cx, cy), fill='blue'))

        errors = [[get_error2(data, RSSI_MATRIX[x][y]) for y in range(config.M_HEIGHT)] for x in range(config.M_WIDTH)]

        elapsed_time = time.time() - start_time

        minimum_error_coordinates = numpy.where(errors == numpy.amin(errors))

        err_x, err_y = [coord[0] for coord in minimum_error_coordinates]

        time_on_errors = time_on_errors + elapsed_time * 1000
        print('time on errors', time_on_errors)

        SIMULATIONS.append((err_x, err_y))

        # YELLOW CIRCLE -> NEW ALG
        if DEBUG_CIRCLES:
            TILES.append(FRAME.canvas.create_oval(coords_to_circle(err_x, err_y), fill='yellow'))

        # BLUE CIRCLE -> MEDIAN ON 'SIM_WINDOW' SIMULATIONS WITH NEW ARG
        cx, cy = 0, 0

        if len(SIMULATIONS) >= SIM_WINDOW:
            window_results = SIMULATIONS[-SIM_WINDOW:]
            xs, ys = [s[0] for s in window_results], [s[1] for s in window_results]

            cx, cy = median(xs), median(ys)

            if DEBUG_CIRCLES:
                TILES.append(FRAME.canvas.create_oval(coords_to_circle(cx, cy), fill='light blue'))

        # ORANGE CIRCLE -> OLD ALG
        ox, oy = ANTENNAS[max(data, key=lambda x: x[1])[0]]
        if DEBUG_CIRCLES:
            TILES.append(FRAME.canvas.create_oval(coords_to_circle(ox, oy), fill='orange'))

        # distance error from real point for every algorithm in the current simulation
        err1 = math.dist((err_x, err_y), (beacon[0], beacon[1]))
        err2 = math.dist((cx, cy), (beacon[0], beacon[1]))
        err3 = math.dist((ox, oy), (beacon[0], beacon[1]))

        # error saving for multiple simulations and comparisons
        ERRORS.append((err1, err2, err3))


def save_results():
    """
    Saves result in file
    """

    def err_sum(index):
        return sum([e[index] for e in ERRORS])

    with open('results.txt', 'a') as results:
        results.write(f'window: {SIM_WINDOW}\n')

        results.write(f'new alg: {err_sum(0)}\n')
        results.write(f'new alg(M): {err_sum(1)}\n')
        results.write(f'old alg: {err_sum(2)}\n\n\n\n')

        for i, e in enumerate(ERRORS):
            results.write(f'{i}) {e}\n')


class Test(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.initUI()

    def initUI(self):
        """
        Initializes the ui
        """
        W, H = config.SCREEN_W // config.M_WIDTH, config.SCREEN_H // config.M_HEIGHT

        self.canvas = Canvas(self,
                             width=W * config.M_WIDTH + 1,
                             height=H * config.M_HEIGHT + 1,
                             borderwidth=0)

        for y in range(config.M_HEIGHT):
            for x in range(config.M_WIDTH):
                coords = [x * W + 2, y * H + 2, x * W + W + 2, y * H + H + 2]
                self.canvas.create_rectangle(*coords, fill='light grey', outline='grey')

        antennas_text = self.canvas.create_text(40, config.SCREEN_H, text=f'antennas: {len(ANTENNAS)}')
        sim_window_text = self.canvas.create_text(180, config.SCREEN_H, text=f'window: {SIM_WINDOW}')

        for x in range(len(config.MATRIX[0])):
            for y in range(len(config.MATRIX)):
                self.canvas.itemconfig(coords_to_index(x, y) + 1, fill='light grey')

        def rect_from_coords(w, side):
            x, y = w[0] * W + W / 2, w[1] * H + H / 2
            return [x - side + 2, y - side + 2, x + side, y + side]

        def add_rectangles():
            for w in WALLS:
                wall_type = 'inner_wall' if w[1] == PATH_LOSS_INTERNAL else 'perimeter_wall'
                r = self.canvas.create_rectangle(rect_from_coords(w[0], 8), fill=colors[wall_type])
                RECTANGLES.append(r)

            for a in ANTENNAS:
                r = self.canvas.create_rectangle(rect_from_coords(a, 5), fill=colors['antenna'])
                RECTANGLES.append(r)

        def left_click(event):
            for r in RECTANGLES:
                self.canvas.delete(r)

            selected = self.canvas.find_closest(event.x, event.y)
            x, y = index_to_coords(selected[0] - 1)

            is_antenna = (x, y) in ANTENNAS
            is_perim_wall = len([w for w in WALLS if w[0] == (x, y) and w[1] == PATH_LOSS_PERIM]) > 0
            is_inner_wall = len([w for w in WALLS if w[0] == (x, y) and w[1] == PATH_LOSS_INTERNAL]) > 0

            next_index = (config.MATRIX[x][y] + 1) % len(tiles)

            config.MATRIX[x][y] = next_index

            get_antennas()
            get_walls()

            add_rectangles()

            self.canvas.itemconfig(antennas_text, text=f'antennas: {len(ANTENNAS)}')

        add_rectangles()

        def right_click(event):
            x1, y1 = (event.x - 0.5), (event.y - 0.5)
            x2, y2 = (event.x + 0.5), (event.y + 0.5)
            point = self.canvas.create_oval(x1, y1, x2, y2, fill='red', outline='red')
            PATH.append([(event.x, event.y), point])

        def clear_path(event):
            for p in PATH:
                self.canvas.delete(p[1])
            PATH.clear()

        self.canvas.bind('<B3-Motion>', right_click)
        self.canvas.bind('<ButtonPress-3>', clear_path)
        self.canvas.bind('<Button-1>', left_click)
        self.canvas.pack()


old_rect = -1
count = 0


def run():
    def update():
        """
        Updates beacons on the map
        """

        global old_rect
        if old_rect != -1:
            FRAME.canvas.delete(old_rect)

        for p in PERSONS:
            global PATH
            new_path = p.walk_along_path(PATH, config.SIDE_LENGTH)

            for rem in [el for el in PATH if el not in new_path]:
                FRAME.canvas.delete(rem[1])

            PATH = new_path

            if len(PATH) == 0:
                stop_simulation()

            old_rect = FRAME.canvas.create_rectangle(p.x - 5, p.y - 5, p.x + 5, p.y + 5, fill='red')

    def sim():
        """
        Performs a new simulation
        """

        global count
        count = count + 1
        # print('sim #', count)
        clear_tiles()

        start_time = time.time()
        simulate()
        elapsed_time = time.time() - start_time
        print('sim', count, 'time:', elapsed_time)

        if count == config.STOP_AT:
            save_results()

    sched.add_job(update, 'interval', seconds=(1 / PERSON_UPDATE_MULTIPLIER))
    sched.add_job(sim, 'interval', seconds=1)


def start_simulation():
    """
    Starts a new simulation if a path is set
    """

    sched.resume()
    run()


def stop_simulation():
    """
    Stops the current simulation
    """

    if sched.running:
        sched.remove_all_jobs()
        sched.pause()


if __name__ == '__main__':

    # Load settings and map
    load_settings("settings.json")
    read_map('maps/map2.txt')

    get_antennas()
    get_walls()

    start_time = time.time()

    # tries to load a pre saved RSSI map
    RSSI_MATRIX = read_saved_matrix()

    tt = time.time() - start_time

    print(f'Setup took {tt} ms')

    PERSONS.append(Person())
    sched.start()

    def init():
        """
        Creates the window and loads the map visually
        It also adds all the buttons
        """

        root = Tk()
        root.geometry(f'{SCREEN_W + 40}x{SCREEN_H + 100}')
        root.title('RSSI localization simulator')
        root.config(bg='#233043')

        global FRAME
        FRAME = Test(master=root)
        FRAME.pack()

        def click_save():
            print_map('maps/save1.txt')

        def reload_matrix():
            get_ideal_RSSI_vectors_matrix()

        def clear_results():
            ERRORS.clear()

        def on_closing():
            if sched.running:
                sched.remove_all_jobs()
                sched.shutdown(wait=False)
                root.destroy()
            exit(0)

        b1 = Button(root, text='Save map', command=click_save, fg='white', bg='#384D6B')
        b1.pack(side=LEFT, padx=10)
        b2 = Button(root, text='Setup Ideal Matrix', command=reload_matrix, fg='white', bg='#384D6B')
        b2.pack(side=LEFT, padx=10)
        b3 = Button(root, text='Start simulation', command=start_simulation, fg='white', bg='#384D6B')
        b3.pack(side=RIGHT, padx=10)
        b3 = Button(root, text='Stop simulation', command=stop_simulation, fg='white', bg='#384D6B')
        b3.pack(side=RIGHT, padx=10)
        b4 = Button(root, text='Save simulation results', command=save_results, fg='white', bg='#384D6B')
        b4.pack(side=RIGHT, padx=10)
        b4 = Button(root, text='Clear simulation results', command=clear_results, fg='white', bg='#384D6B')
        b4.pack(side=RIGHT, padx=10)

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    init()
