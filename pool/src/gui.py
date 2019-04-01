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

SCREEN_DIMENSIONS = WIDTH, HEIGHT = 1000, 1000
TABLE_LENGTH = 800
TABLE_OFFSET_X, TABLE_OFFSET_Y = 100, 100

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
    screen.fill((0, 0, 0))


def draw_pool_table(screen, table: PoolTable):
    table_color = (0, 200, 0)

    nw = coords_to_pygame(Coordinates(table.left, table.top), HEIGHT)
    se = coords_to_pygame(Coordinates(table.right, table.bottom), HEIGHT)

    # left, top, width, height = TABLE_OFFSET_X, TABLE_OFFSET_Y, table.length, table.width
    left, top, width, height = nw.x, nw.y, table.length, table.width

    # Draw table cloth
    pygame.draw.rect(screen, table_color, pygame.Rect(left, top, width, height), 0)

    # Draw table pockets
    for hole_center in table.hole_centers:
        pocket_color = (0, 0, 0)
        p = coords_to_pygame(hole_center, HEIGHT)
        x, y, r = int(p.x), int(p.y), int(table.hole_radius)
        pygame.draw.circle(screen, pocket_color, (x, y), r)


def draw_cue_stick_line(screen, table: PoolTable):
    # TODO

    if table.cue_deflect_line_start is None:
        return

    p1 = coords_to_pygame(table.cue_ball.pos, HEIGHT)
    p2 = coords_to_pygame(table.cue_deflect_line_start, HEIGHT)

    x1, y1 = int(p1.x), int(p1.y)
    x2, y2 = int(p2.x), int(p2.y)
    color = (255, 255, 255)

    pygame.gfxdraw.line(screen, x1, y1, x2, y2, color)

    # DRAW GHOST BALL
    p = coords_to_pygame(table.cue_deflect_line_start, HEIGHT)

    x, y, r = int(p.x), int(p.y), int(table.cue_ball.radius)
    color = table.cue_ball.ball_type.color

    # Draw a circle
    pygame.gfxdraw.aacircle(screen, x, y, r, color)


def draw_cue_ghost_ball(screen, table: PoolTable):
    # TODO
    return


def draw_cue_ball_deflection_line(screen, table: PoolTable):
    if table.cue_deflect_line_end is None:
        return

    p1 = coords_to_pygame(table.cue_deflect_line_start, HEIGHT)
    p2 = coords_to_pygame(table.cue_deflect_line_end, HEIGHT)

    x1, y1 = int(p1.x), int(p1.y)
    x2, y2 = int(p2.x), int(p2.y)
    color = (255, 255, 255)

    pygame.gfxdraw.line(screen, x1, y1, x2, y2, color)

    # # DRAW GHOST BALL
    p = coords_to_pygame(table.cue_deflect_line_end, HEIGHT)

    x, y, r = int(p.x), int(p.y), int(table.cue_ball.radius)
    color = table.cue_ball.ball_type.color
    pygame.gfxdraw.aacircle(screen, x, y, r, color)


def draw_object_ball_deflection_line(screen, table: PoolTable):
    if table.object_deflect_line_start is None or table.object_deflect_line_end is None:
        return

    p1 = coords_to_pygame(table.object_deflect_line_start, HEIGHT)
    p2 = coords_to_pygame(table.object_deflect_line_end, HEIGHT)

    x1, y1 = int(p1.x), int(p1.y)
    x2, y2 = int(p2.x), int(p2.y)
    color = (255, 255, 255)

    pygame.gfxdraw.line(screen, x1, y1, x2, y2, color)

    # # DRAW GHOST BALL
    p = coords_to_pygame(table.object_deflect_line_end, HEIGHT)

    x, y, r = int(p.x), int(p.y), int(table.cue_ball.radius)
    color = table.cue_ball.ball_type.color
    pygame.gfxdraw.aacircle(screen, x, y, r, color)


def draw_pool_ball(screen, ball: PoolBall):
    p = coords_to_pygame(ball.pos, HEIGHT)

    x, y, r = int(p.x), int(p.y), int(ball.radius)
    color = ball.ball_type.color

    # Draw a circle
    pygame.gfxdraw.aacircle(screen, x, y, r, color)
    pygame.gfxdraw.filled_circle(screen, x, y, r, color)


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
            print('AFTER SETTING cue_angle', table.cue_angle)
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

    # Table time step
    table.time_step()

    # Draw pool table
    draw_pool_table(screen, table)

    draw_cue_stick_line(screen, table)
    draw_cue_ghost_ball(screen, table)
    draw_cue_ball_deflection_line(screen, table)
    draw_object_ball_deflection_line(screen, table)

    # Draw all pool balls
    for ball in balls:
        draw_pool_ball(screen, ball)

    pygame.display.flip()


def main():
    """
    Main function for pygame to be run by itself.
    """
    screen = gui_init()

    # Create pool table
    nw = coords_from_pygame((TABLE_OFFSET_X, TABLE_OFFSET_Y), HEIGHT)
    se = coords_from_pygame((TABLE_OFFSET_X + TABLE_LENGTH, TABLE_OFFSET_Y + TABLE_LENGTH / 2), HEIGHT)
    table = PoolTable(nw, se)

    while 1:
        # Get just the list of balls to iterate easily
        balls = list(table.balls.values())

        clear_screen()

        # Check Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                # These positions assume origin lower-left
                target_pos = coords_from_pygame(pygame.mouse.get_pos(), HEIGHT)
                cue_pos = table.cue_ball.pos

                table.cue_angle = get_angle(target_pos, cue_pos)
                print('AFTER SETTING cue_angle', table.cue_angle)
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

        # Table time step
        table.time_step()

        # Draw pool table
        draw_pool_table(screen, table)

        draw_cue_stick_line(screen, table)
        draw_cue_ghost_ball(screen, table)
        draw_cue_ball_deflection_line(screen, table)
        draw_object_ball_deflection_line(screen, table)

        # Draw all pool balls
        for ball in balls:
            draw_pool_ball(screen, ball)

        pygame.display.flip()

# if __name__ == '__main__':
#     main()
