import sys

import numpy as np
import os
import pygame
import pygame.gfxdraw

from speed_detection.speed_detection import SpeedDetection
from pool.src.physics.coordinates import Coordinates
from pool.src.physics.utility import get_angle
from pool.src.physics.vector import Vector
from pool.src.pool.ball_type import BallType
from pool.src.pool.pool_ball import PoolBall
from pool.src.pool.pool_table import PoolTable

TABLE_OFFSET_X, TABLE_OFFSET_Y = 0, 0

# Use these for projector output
# SCREEN_DIMENSIONS = WIDTH, HEIGHT = TABLE_LENGTH, TABLE_WIDTH = 1573, 768  # Table fits entire screen

# Use these for Macbook Pro 13" mirroring
# HORIZONTAL: -8, VERTICAL: -20
SCREEN_DIMENSIONS = WIDTH, HEIGHT = TABLE_LENGTH, TABLE_WIDTH = 1668, 778  # Table fits entire screen
"""
Table length: 95.55cm -> 17.4568288854 pixels/cm for x-axis
Table width: 48.8cm -> 15.9426229508 pixels/cm for y-axis
"""

# Initialize pygame window to overlay on top of pool table
SCREEN_X_OFFSET = 3000 # This one just needs to be above 2000 because of projector position
SCREEN_Y_OFFSET = 175

BACKGROUND_COLOR = (0, 0, 0)
FOREST_GREEN = (1, 68, 33)
BLACK = (0,0,0)
TABLE_COLOR = BLACK
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
    Start the gui at the offsets specified.

    :return: pygame screen to use for all gui functions
    """
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (SCREEN_X_OFFSET,SCREEN_Y_OFFSET)
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
        # draw_circle(screen, hole_center, table.hole_radius, pocket_color, filled=True)
        # Draw a rectangle for pockets, instead
        left_top_coords = Coordinates(hole_center.x - table.hole_radius, hole_center.y + table.hole_radius)
        left_top_pg = coords_to_pygame(left_top_coords, HEIGHT)
        width = height = 2 * table.hole_radius
        pygame.draw.rect(screen, pocket_color, pygame.Rect(left_top_pg.x, left_top_pg.y, width, height), 0)

def draw_cue_stick(screen, table: PoolTable):
    if table.cue_stick_tip is None or table.cue_stick_back is None:
        return

    brown_rgb = (165, 42, 42)
    draw_line(screen, table.cue_stick_tip, table.cue_stick_back, brown_rgb)

    # Draw tiny red circle for the cue stick tip
    draw_circle(screen, table.cue_stick_tip, 1, (255, 0, 0), filled=True)

    # Draw extended, floating cue stick line
    if table.floating_cue_stick:
        assert table.cue_stick_tip is not None, 'table says floating cue stick, but cue front point is None'
        assert table.floating_cue_stick_line_end is not None, 'table says floating cue stick, but cue stick line end is None'
        draw_line(screen, table.cue_stick_tip, table.floating_cue_stick_line_end, (255, 255, 255))



def draw_ball_lines(screen, table: PoolTable, white_lines=False):
    if table.ghost_ball_lines is {}:
        return

    for ball, ghost_lines in table.ghost_ball_lines.items():
        if white_lines:
            color = (255, 255, 255)
        else:
            color = ball.ball_type.color

        # Draw traveling line
        travel_line_start, travel_line_end = ball.pos, ghost_lines[0]
        draw_line(screen, travel_line_start, travel_line_end, color)

        # Draw ghost ball start
        draw_circle(screen, travel_line_end, ball.radius, color)

        # Draw ghost line
        ghost_line_start, ghost_line_end = ghost_lines[0], ghost_lines[1]
        draw_line(screen, ghost_line_start, ghost_line_end, color)

        # Draw ghost ball end, only for non-cue ball
        if ball.ball_type is not BallType.CUE:
            draw_circle(screen, ghost_line_end, ball.radius, color)

def draw_pool_ball(screen, ball: PoolBall):
    # Draw a circle
    # draw_circle(screen, ball.pos, ball.radius, ball.ball_type.color, filled=False)

    # DEBUG: Make all the balls white for now
    draw_circle(screen, ball.pos, ball.radius, (255, 255, 255), filled=False)


def gui_update(screen, table, speed: SpeedDetection):
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
                table = PoolTable(nw, se, speed)


    # Table time step
    table.time_step()

    # Draw pool table
    draw_pool_table(screen, table)
    draw_ball_lines(screen, table, white_lines=True)

    # Draw all pool balls
    for ball in balls:
        draw_pool_ball(screen, ball)

    # Draw the physical cue stick
    draw_cue_stick(screen, table)

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
