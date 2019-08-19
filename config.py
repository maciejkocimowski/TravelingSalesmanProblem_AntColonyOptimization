import pygame

RESOLUTION = (750, 750)
SCALE = 140
MOVE = 25
WHITE = (255, 255, 255)
win = pygame.display.set_mode(RESOLUTION, pygame.RESIZABLE)
pygame.display.set_caption("ACO")

POINTS = [('A', 1, 0),
          ('B', 5, 3),
          ('C', 5, 1),
          ('D', 0, 1),
          ('E', 0, 5),
          ('F', 3, 3)]

START_POINT = 'A'
INIT_PHEROMONE = 3
ALPHA = 3
BETA = 1
RHO = 0.3
END_COUNTER = 100
