import pygame
import sys
from operator import itemgetter
from numpy import cumsum
from math import sqrt, pow
from random import uniform, randint
from config import SCALE, MOVE, WHITE, win, POINTS, START_POINT, INIT_PHEROMONE, ALPHA, BETA, RHO, END_COUNTER

pygame.init()
MYFONT = pygame.font.SysFont("monospace", 30)

BEST_PATHS = {}
BEST_PATH = ()
counter = 0


class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


class Ant:
    def __init__(self, all_points, distances, pheromones, shift):
        self.ant_point = START_POINT
        self.start_end_point = START_POINT
        self.visited_points = [START_POINT]
        self.all_points = [point.name for point in all_points]
        self.points_to_visit = [point for point in self.all_points if point != self.start_end_point]
        self.probabilities = self.get_points_probabilities(self.ant_point, self.points_to_visit,
                                                           distances, pheromones)
        self.cumulative_sums = self.get_points_cumulative_sums(self.probabilities)
        self.shift = shift
        self.color = randint(0, 255), randint(0, 255), randint(0, 255)

    def __repr__(self):
        return "Ant {}, {}, {}".format(self.ant_point, self.visited_points, self.points_to_visit)

    def draw_lines(self, visited_pts):
        """
        :brief: Draw lines for ant from visited_pts list
        """
        pairs = list(zip(visited_pts[:-1], visited_pts[1:]))
        for pair in pairs:
            for ptn in points[:]:
                if ptn.name in pair[0]:
                    point_from = ptn
                elif ptn.name in pair[1]:
                    point_to = ptn
            pygame.draw.line(win, self.color, (point_from.x * SCALE + MOVE + self.shift,
                                               point_from.y * SCALE + MOVE + self.shift),
                                              (point_to.x * SCALE + MOVE + self.shift,
                                               point_to.y * SCALE + MOVE + self.shift))

    @staticmethod
    def clear_lines():
        """
        :brief: Clear existing lines drawing black ones
        """
        points_ = points[:]
        points_.append(points_[0])
        for ptn_from in points_:
            for ptn_to in points_:
                pygame.draw.line(win, (0, 0, 0), (ptn_from.x * SCALE + MOVE, ptn_from.y * SCALE + MOVE),
                                 (ptn_to.x * SCALE + MOVE, ptn_to.y * SCALE + MOVE))

    def get_next_point(self):
        """
        :brief: get next point for ant
        :return: next selected point
        """
        random_number = uniform(0, 1)
        numerical_intervals = list(zip(list(self.cumulative_sums.values()), list(self.cumulative_sums.values())[1:]))
        numerical_intervals = [(0.0, list(self.cumulative_sums.values())[0])] + numerical_intervals
        if random_number == 0.0:
            return list(self.cumulative_sums.keys())[0]
        for key, value in zip(self.cumulative_sums.keys(), numerical_intervals):
            if value[0] < random_number <= value[1]:
                return key

    def select_next_point(self):
        """
        :brief: select next point for ant
        """
        if not self.points_to_visit and (self.visited_points[-1] != self.start_end_point):
            self.points_to_visit.append(self.start_end_point)
            self.probabilities = self.get_points_probabilities(self.ant_point, self.points_to_visit,
                                                               distance_matrix, pheromone_matrix)
            self.cumulative_sums = self.get_points_cumulative_sums(self.probabilities)
        if not self.points_to_visit and (self.visited_points[-1] == self.start_end_point):
            self.clear_lines()
            self.draw_lines(self.visited_points)
            self.ant_point = self.start_end_point
            if tuple(self.visited_points) not in BEST_PATHS:
                BEST_PATHS[tuple(self.visited_points)] = 1
            else:
                BEST_PATHS[tuple(self.visited_points)] += 1
            self.visited_points = [self.ant_point]
            self.points_to_visit = [point for point in self.all_points if point != self.ant_point]
            self.probabilities = self.get_points_probabilities(self.ant_point, self.points_to_visit,
                                                               distance_matrix, pheromone_matrix)
            self.cumulative_sums = self.get_points_cumulative_sums(self.probabilities)
        else:
            next_point = self.get_next_point()
            self.ant_point = next_point
            self.points_to_visit.remove(next_point)
            self.visited_points.append(next_point)
            self.probabilities = self.get_points_probabilities(self.ant_point, self.points_to_visit,
                                                               distance_matrix, pheromone_matrix)
            self.cumulative_sums = self.get_points_cumulative_sums(self.probabilities)
            if not self.points_to_visit and (self.visited_points[-1] == self.start_end_point):
                pairs = list(zip(self.visited_points[:-1], self.visited_points[1:]))
                containter = 0
                for from_, to_ in pairs:
                    containter += 1 / distance_matrix[from_][to_]
                for from_, to_ in pairs:
                    pheromone_matrix[from_][to_] = ((1 - RHO) * pheromone_matrix[from_][to_]) + containter

    @staticmethod
    def get_point_probability(point_probability, ant_point, points_list, distances, pheromones):
        """
        :brief: get probability for point_probability from ant_point where ant is now using points_list
                and distances matrix + pheromone matrix

        :param point_probability: which point probability we want to get
        :param ant_point: ponit where ant is now
        :param points_list: all possible points for ant
        :param distances: distances matrix
        :param pheromones: pheromone matrix
        :return: probability for point_probability
        """
        container = []
        for end_point in points_list:
            container.append(pheromones[ant_point][end_point]**ALPHA * (1 / distances[ant_point][end_point])**BETA)
        return (pheromones[ant_point][point_probability]**ALPHA *
                (1 / distances[ant_point][point_probability])**BETA) / (sum(container))

    def get_points_probabilities(self, ant_point, points_list, distances, pheromones):
        """
        :brief: get probabilities for points from points_list using distance matrix + pheromone matrix
        :param ant_point: point where ant is now
        :param points_list: possible points for ant
        :param distances: distances matrix
        :param pheromones: pheromone matrix
        :return: dict of probabilities for available points for ant
        """
        probabilities = {}
        for point in points_list:
            point_probability = self.get_point_probability(point, ant_point, points_list,
                                                           distances, pheromones)
            probabilities[point] = point_probability
        return probabilities

    @staticmethod
    def get_points_cumulative_sums(probabilities_for_ant_point):
        """
        :brief: get cumulative sums for points using probabilities_matrix
        :param probabilities_for_ant_point: probabilities for ant point
        :return: cumulative sums matrix
        """
        if not probabilities_for_ant_point:
            return {}
        keys, values = zip(*sorted(probabilities_for_ant_point.items(), key=itemgetter(1)))
        total = sum(values)
        cumulative_sums = dict(zip(keys, (subtotal / total for subtotal in cumsum(values))))
        return cumulative_sums


def check_run(events):
    """
    :brief: When user press Exit button, close the program correctly
    :param events: All possible events which user can achieve
    """
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def draw_graph():
    """
    :brief: Draw all points with text label
    """
    for point in points:
        x = point.x*SCALE+MOVE
        y = point.y*SCALE+MOVE
        pygame.draw.circle(win, WHITE, (x, y), 5)

        # render text
        label = MYFONT.render(point.name, 1, (255, 0, 0))
        win.blit(label, (point.x*SCALE+MOVE, point.y*SCALE+MOVE))


def get_points(all_points):
    """
    :brief: Get points from POINTS list
    :return: list of points objects from class Point
    """
    list_of_points = []
    for point in all_points:
        p = Point(point[0], point[1], point[2])
        list_of_points.append(p)
    return list_of_points


def create_ants(ant_number):
    """
    :brief: Create ant_number of objects of Ant class
    :param ant_number: number of ant to crate
    :return: list of ant objects
    """
    ants = []
    for i in range(ant_number):
        ants.append(Ant(points, distance_matrix, pheromone_matrix, shift=i * 3))
    return ants


def get_distance_matrix():
    """
    :brief: Get matrix with distances between points

    :return: distances matrix
    """
    distances = {}
    for point_hor in points:
        point_hor_distances = {}
        for point_ver in points:
            if point_ver == point_hor:
                continue
            distance = sqrt(pow(point_ver.x-point_hor.x, 2) + pow(point_ver.y-point_hor.y, 2))
            point_hor_distances[point_ver.name] = distance
        distances[point_hor.name] = point_hor_distances
    return distances


def get_init_pheromone_matrix():
    """
    :brief: get init pheromone on lines between points. At the beginning pheromone is INIT_PHEROMONE
    :return: pheremone mattix
    """
    pheromones = {}
    for point_hor in points:
        point_hor_pheromone = {}
        for point_ver in points:
            if point_ver == point_hor:
                continue
            point_hor_pheromone[point_ver.name] = INIT_PHEROMONE
        pheromones[point_hor.name] = point_hor_pheromone
    return pheromones


def get_current_best_path(best_paths):
    """
    :brief: get best current best path from best_paths
    :param best_paths: dict of most appearance of ant paths
    :return: current best path
    """
    return max(best_paths, key=best_paths.get)

points = get_points(POINTS)
distance_matrix = get_distance_matrix()
pheromone_matrix = get_init_pheromone_matrix()
ants = create_ants(5)

while True:
    pygame.time.delay(100)
    check_run(pygame.event.get())

    for ant in ants:
        for i in range(len(points)+1):
            ant.select_next_point()

    current_best_path = get_current_best_path(BEST_PATHS)
    if current_best_path != BEST_PATH:
        BEST_PATH = current_best_path
        counter = 1
    else:
        counter += 1
    if counter >= END_COUNTER:
        print('BEST PATH: ', BEST_PATH)
        label = MYFONT.render('Best: {}'.format(BEST_PATH), 1, (255, 255, 255))
        win.blit(label, (10, 10))
        draw_graph()
        pygame.display.update()
        input()
        break

    draw_graph()
    pygame.display.update()
