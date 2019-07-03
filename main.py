from constants import *

import pygame

import pymunk
import pymunk.pygame_util

import sys

import os

import math

# TODO: Resize assets, add levels, use constants instead of arbitrary numbers

# A rocket landing simulator game that has multiple levels/rockets


def in_rad(degrees):
    return degrees * math.pi / 180


def in_deg(radians):
    return radians * 180 / math.pi


def pm_to_pg_y(pm_y):
    return HEIGHT - pm_y


def pg_to_pm_y(pg_y):
    return HEIGHT + pg_y


class Rocket(pygame.sprite.Sprite):  # Calculate its own positions and display
    def __init__(self, space, type_of_rocket, x, y):
        super().__init__()

        self.type_of_rocket = type_of_rocket

        self.body_image = []
        self.left_rcs_images = []
        self.right_rcs_images = []
        self.thrust_images = []

        self.load_images()

        self.original_image = pygame.transform.scale(self.body_image[0], (100, 250))
        self.image = self.original_image

        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

        # Pymunk

        self.rocket_mass = 100  # pseudo mass guess and check
        self.rocket_size = (self.rect.width, self.rect.height)

        # Shape/body config

        self.rocket_moment = pymunk.moment_for_box(self.rocket_mass, self.rocket_size)  #

        self.rocket_body = pymunk.Body(self.rocket_mass, self.rocket_moment)
        self.rocket_body.position = (x, y)  # subject to change

        self.rocket_shape = pymunk.Poly.create_box(self.rocket_body, self.rocket_size)

        self.space = space
        self.space.add(self.rocket_body, self.rocket_shape)

        self.rocket_shape.elasticity = 5

        self.previous_velocity = [0, 0]  # x, y
        self.acceleration = [0, 0]  # x, y

    def load_images(self):
        # TODO: put all image variables into dictionary or else:

        self.body_image = [pygame.image.load(os.getcwd() + "/assets/{}/body/".format(self.type_of_rocket) + file)
                           for file in os.listdir(os.getcwd() + "/assets/{}/body/".format(self.type_of_rocket))]

        self.left_rcs_images = [
            pygame.image.load(os.getcwd() + "/assets/{}/left_rcs/".format(self.type_of_rocket) + file)
            for file in os.listdir(os.getcwd() + "/assets/{}/left_rcs/".format(self.type_of_rocket))]

        self.right_rcs_images = [
            pygame.image.load(os.getcwd() + "/assets/{}/right_rcs/".format(self.type_of_rocket) + file)
            for file in os.listdir(os.getcwd() + "/assets/{}/right_rcs/".format(self.type_of_rocket))]

        self.thrust_images = [pygame.image.load(os.getcwd() + "/assets/{}/thrust/".format(self.type_of_rocket) + file)
                              for file in os.listdir(os.getcwd() + "/assets/{}/thrust/".format(self.type_of_rocket))]

    def update(self):
        self.image = pygame.transform.rotate(self.original_image, in_deg(self.rocket_body.angle))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = (self.rocket_body.position[0], pm_to_pg_y(self.rocket_body.position[1]))

        self.acceleration = [self.previous_velocity[0] - self.rocket_body.velocity[0],
                             self.previous_velocity[1] - self.rocket_body.velocity[1]]

    def store_velocity(self):
        self.previous_velocity[0] = self.rocket_body.velocity[0]
        self.previous_velocity[1] = self.rocket_body.velocity[1]

    def thrust_up(self):
        self.rocket_body.apply_force_at_local_point((0, 200000), (0, 0))

    def right_rcs(self):
        self.rocket_body.apply_force_at_local_point((-50000, 0), (0, 25))

    def left_rcs(self):
        self.rocket_body.apply_force_at_local_point((50000, 0), (0, 25))


class Platform(pygame.sprite.Sprite):
    def __init__(self, space):
        super().__init__()
        # Pygame
        self.image = pygame.Surface([100, 20])
        self.image.fill((0, 0, 0))

        # Coordinates
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT - 20)

        # Pymunk
        self.floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.floor_shape = pymunk.Segment(self.floor_body, pymunk.Vec2d(250, 20), pymunk.Vec2d(350, 20), 10)
        self.floor_shape.friction = 0.3
        space.add(self.floor_body, self.floor_shape)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, space):
        super().__init__()
        game = Game()
        rocket = Rocket(game.space, "spacey", 300, 600)
        self.image = pygame.transform.scale(pygame.image.load(os.getcwd() + "/assets/props/explosion01.jpg"),
                                                             (800, 800))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.explosion_body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.explosion_shape = pymunk.Poly.create_box(self.explosion_body, self.rect)
        space.add(self.explosion_body, self.explosion_shape)


class Game:
    def __init__(self):
        # Pygame initialization
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.surface = pygame.transform.scale(pygame.image.load(os.getcwd() + "/assets/props/skyLevel.jpg").convert(),
                                                               (600, 800))
        self.intro = True
        self.font = pygame.font.SysFont(None, 25)
        self.sprite_group = pygame.sprite.Group()

        # Pymunk initialization
        self.space = pymunk.Space()
        self.space.gravity = (0.0, GRAVITY)
        self.dt = 1 / FRAMERATE

        # Initialize unchangeable variables/pygame
        self.game_exit = False
        self.objects = []

    def message_to_screen(self, msg, color):
        screen_text = self.font.render(msg, True, color)
        self.screen.blit(screen_text, [50, 50])

    def start(self):
        while self.intro is True:
            self.screen.fill(WHITE)
            self.message_to_screen("Welcome to PyLander! press S to start Q to quit", BLUE)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.intro = False
                        self.game_loop()
                    if event.key == pygame.K_q:
                        self.intro = False
                        self.game_exit = True
            pygame.display.update()

    def game_over_screen(self):
        while True:
            self.message_to_screen("Game over! Thanks for playing. Press S to start or Q to quit", RED)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.game_loop()
                    if event.key == pygame.K_q:
                        sys.exit()
                if event.type == pygame.QUIT:
                    sys.exit()
            pygame.display.update()

    def game_loop(self):
        rocket = Rocket(self.space, "spacey", 300, 600)
        platform = Platform(self.space)
        explosion = Explosion(self.space)
        sprite_group = pygame.sprite.Group()

        sprite_group.add(rocket)
        sprite_group.add(platform)

        explosion_group = pygame.sprite.Group()
        explosion_group.add(explosion)

        while not self.game_exit:
            # Exit controls
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                rocket.thrust_up()
            if keys[pygame.K_d]:
                rocket.right_rcs()
            if keys[pygame.K_a]:
                rocket.left_rcs()

            rocket.store_velocity()

            self.space.step(STEP_SIZE)

            self.screen.fill((WHITE))
            self.screen.blit(self.surface, (0, 0))

            sprite_group.update()
            sprite_group.draw(self.screen)

            pygame.display.update()

            self.clock.tick(FRAMERATE)

            if rocket.rocket_body.position.int_tuple[1] < 0 or rocket.rocket_body.position.int_tuple[0] < 0 \
               or rocket.rocket_body.position.int_tuple[0] > 600 or abs(rocket.acceleration[0]) > 250\
               or abs(rocket.acceleration[1]) > 250:
                self.space.remove(rocket.rocket_body, rocket.rocket_shape)
                explosion_group.update()
                explosion_group.draw(self.screen)
                self.game_over_screen()


if __name__ == "__main__":
    game = Game()
    game.start()
