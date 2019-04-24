import sys

import numpy as np
import pygame
import pygame.gfxdraw

from pool.src.physics.coordinates import Coordinates
from pool.src.physics.utility import get_angle
from pool.src.physics.vector import Vector
from pool.src.pool.ball_type import BallType
from pool.src.pool.pool_ball import PoolBall
from pool.src.pool.pool_table import PoolTable

SCREEN_DIMENSIONS = WIDTH, HEIGHT = 1200, 1200
TABLE_LENGTH = 1200
TABLE_WIDTH = TABLE_LENGTH / 2.1352313167
TABLE_OFFSET_X, TABLE_OFFSET_Y = 0, 0

BACKGROUND_COLOR = (0, 0, 0)
TABLE_COLOR = (1, 68, 33)
CUE_STICK_LINE_COLOR = (255, 255, 255)
POCKET_COLOR = (255, 0, 0)
"""
Helper functions.
"""


def coords_to_pygame(xy: Coordinates, height: float) -> Coordinates:
    """
    Convert Coordinates into PyGame coordinates tuple (lower-left => top-left).
    """

    return Coordinates(int(xy.x), int(height - xy.y))


def coords_from_pygame(xy: (float, float), height: float) -> Coordinates:
    """
    Convert PyGame coordinates tuple to Coordinates (top-left => lower-left).
    """

    return Coordinates(xy[0], height - xy[1])

def draw_line(screen, p1, p2, color):
    p1, p2 = coords_to_pygame(p1, HEIGHT), coords_to_pygame(p2, HEIGHT)
    x1, y1 = int(p1.x), int(p1.y)
    x2, y2 = int(p2.x), int(p2.y)
    pygame.gfxdraw.line(screen, x1, y1, x2, y2, color)

def draw_circle(screen, center, radius, color, filled=False):
    p = coords_to_pygame(center, HEIGHT)
    x, y, r = int(p.x), int(p.y), int(radius)
    pygame.gfxdraw.aacircle(screen, x, y, r, color)

    if filled:
        pygame.gfxdraw.filled_circle(screen, x, y, r, color)


"""
PyGame functions.
"""


def gui_init():
    """
    Start the gui.

    :return: pygame screen to use for all gui functions
    """
    pygame.init()
    return pygame.display.set_mode(SCREEN_DIMENSIONS)


def clear_screen(screen):
    screen.fill(BACKGROUND_COLOR)


def draw_pool_table(screen, table: PoolTable):
    # table_color = (0, 200, 0)
    table_color = TABLE_COLOR

    nw = coords_to_pygame(Coordinates(table.left, table.top), HEIGHT)
    se = coords_to_pygame(Coordinates(table.right, table.bottom), HEIGHT)

    # left, top, width, height = TABLE_OFFSET_X, TABLE_OFFSET_Y, table.length, table.width
    left, top, width, height = nw.x, nw.y, table.length, table.width

    # Draw table cloth
    pygame.draw.rect(screen, table_color, pygame.Rect(left, top, width, height), 0)

    # Draw table pockets
    pocket_color = (0, 0, 0)
    for hole_center in table.hole_centers:
        draw_circle(screen, hole_center, table.hole_radius, pocket_color, filled=True)

def draw_cue_stick(screen, table: PoolTable):
    if table.cue_front_point is None or table.cue_back_point is None:
        print('draw_cue_stick -- returning without drawing...')
        return
    brown_rgb = (165, 42, 42)
    draw_line(screen, table.cue_front_point, table.cue_back_point, brown_rgb)

    # Draw extended, floating cue stick line
    if table.cue_stick_line_end is None:
        return
    draw_line(screen, table.cue_front_point, table.cue_stick_line_end, (255, 255, 255))



def draw_ball_lines(screen, table: PoolTable):
    if table.ghost_ball_lines is {}:
        return

    for ball, ghost_lines in table.ghost_ball_lines.items():
        # Draw traveling line
        travel_line_start, travel_line_end = ball.pos, ghost_lines[0]
        draw_line(screen, travel_line_start, travel_line_end, ball.ball_type.color)

        # Draw ghost ball start
        draw_circle(screen, travel_line_end, ball.radius, ball.ball_type.color)

        # Draw ghost line
        ghost_line_start, ghost_line_end = ghost_lines[0], ghost_lines[1]
        draw_line(screen, ghost_line_start, ghost_line_end, ball.ball_type.color)

        # Draw ghost ball end
        draw_circle(screen, ghost_line_end, ball.radius, ball.ball_type.color)

def draw_pool_ball(screen, ball: PoolBall):
    # Draw a circle
    draw_circle(screen, ball.pos, ball.radius, ball.ball_type.color, filled=True)


def gui_update(screen, table):
    # Get just the list of balls to iterate easily
    balls = list(table.balls.values())

    clear_screen(screen)

    # Check Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            # These positions assume origin lower-left
            target_pos = coords_from_pygame(pygame.mouse.get_pos(), HEIGHT)
            cue_pos = table.cue_ball.pos

            table.cue_angle = get_angle(target_pos, cue_pos)
            # print('AFTER SETTING cue_angle', table.cue_angle)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit()
            elif event.key == pygame.K_b:
                # BREAK cue ball
                mag = 500.0
                force = Vector(mag * np.cos(np.radians(table.cue_angle)),
                               mag * np.sin(np.radians(table.cue_angle)))
                table.balls[BallType.CUE].apply_force(force)
            elif event.key == pygame.K_SPACE:
                # Strike cue ball
                mag = 50.0
                force = Vector(mag * np.cos(np.radians(table.cue_angle)),
                               mag * np.sin(np.radians(table.cue_angle)))
                table.balls[BallType.CUE].apply_force(force)
            elif event.key == pygame.K_p:
                # DEBUG set all speeds to 0
                for ball in balls:
                    ball.vel.x, ball.vel.y = 0, 0
            elif event.key == pygame.K_r:
                # DEBUG reset
                # Create pool table
                nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
                se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_LENGTH / 2), HEIGHT)
                table = PoolTable(nw, se)
            # elif event.type == VIDEORESIZE:
                # size = event.dict['size']
                # screen = pygame.display.set_mode(size, RESIZABLE)


    # Table time step
    table.time_step()

    # Draw pool table
    draw_pool_table(screen, table)
    draw_cue_stick(screen, table)
    draw_ball_lines(screen, table)

    # Draw all pool balls
    for ball in balls:
        draw_pool_ball(screen, ball)

    pygame.display.flip()

    # return screen


def main():
    """
    Main function for pygame to be run by itself.
    """
    # Initialize GUI
    screen = gui_init()

    # Initialize pool table here
    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_WIDTH), HEIGHT)
    table = PoolTable(nw, se)

    while 1:
        # Here, update GUI
        gui_update(screen, table)

# if __name__ == '__main__':
#     main()
