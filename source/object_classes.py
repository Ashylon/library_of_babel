import pygame
import utils
from animator_object import *
from utils import *
from constants import *


def generate_hitbox(position: pygame.Vector2, hitbox_image: pygame.Surface) -> (pygame.Rect, pygame.Vector2):
    """Generates a rectangular hitbox based on the non-transparent part of hitbox_image, and returns the offset."""
    bbox = hitbox_image.get_bounding_rect()  # Get bounding rectangle of non-transparent area

    if bbox.width > 0 and bbox.height > 0:
        # Calculate the hitbox rect and its offset from the top-left corner of the image
        hitbox = pygame.Rect(position.x + bbox.x, position.y + bbox.y, bbox.width, bbox.height)
        offset = pygame.Vector2(bbox.x, bbox.y)  # The offset between the image and the hitbox
    else:
        # If fully transparent, return a default empty hitbox and zero offset
        hitbox = pygame.Rect(position.x, position.y, 0, 0)
        offset = pygame.Vector2(0, 0)

    return hitbox, offset


class GameObject:
    def __init__(self, position: pygame.Vector2, image: pygame.Surface):
        self.image = image.convert_alpha()  # Sprite image
        self.position = position

    def update(self, delta: float, game_world):
        pass

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        position = self.position - camera_pos
        screen.blit(self.image, position)


class ColliderObject(GameObject):
    """Base class for all object with a collider"""

    def __init__(self, position: pygame.Vector2, image: pygame.Surface, hitbox_image: pygame.Surface = None):
        super().__init__(position, image)

        # Use image to generate hitbox if no other hitbox is provided:
        if hitbox_image:
            rect, offset = generate_hitbox(position, hitbox_image)
            self.rect = rect
            self.sprite_offset = offset
        else:
            self.rect = self.image.get_rect(topleft=position)
            self.sprite_offset = pg.Vector2()  # null vector for no offset

    def draw(self, screen, camera_pos):
        """Draw object on screen."""
        position = self.rect.topleft - camera_pos
        screen.blit(self.image, position - self.sprite_offset)


class InteractableObject(ColliderObject):
    """Base class for all objects that define special behaviour when colliding with player"""

    def on_collide(self, player, game_world) -> None:
        pass


class MovingObject(InteractableObject):
    """Base class for all moving objects with physical collision handling"""

    def __init__(self, position: pygame.Vector2, image: pygame.Surface, has_gravity: bool,
                 hitbox_image: pygame.Surface = None):
        super().__init__(position, image, hitbox_image)
        self.max_y_velocity = 800.0
        self.gravity = 30.0
        self.speed_x = 75.0
        self.speed_y = 400.0
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.has_gravity = has_gravity
        self.has_collided = False

    def set_animation(self, animation) -> None:
        pass

    def does_collide(self, rect, objects: list) -> bool:
        """Check if hit box collides with another object."""
        for o in objects:
            if rect.colliderect(o.rect):
                return True
        return False

    def check_is_grounded(self, objects: list) -> bool:
        """Check if element is on the floor."""
        preview_rect = self.rect.move(0, 1)
        if self.does_collide(preview_rect, objects):
            return True
        else:
            return False

    def update(self, delta: float, game_world):
        """update hit box and position depending on collision"""

        # Apply gravity
        self.velocity.y = min(self.velocity.y + self.gravity, self.max_y_velocity)

        # Calculate movement
        dx, dy = self.velocity * delta

        # Move x and check collisions
        self.position.x += dx
        self.rect.topleft = self.position

        self.has_collided = False

        for o in game_world.static_objects:
            if self.rect.colliderect(o):  # Check collision
                self.has_collided = True
                if dx > 0:  # Moving right
                    self.rect.right = o.rect.left
                elif dx < 0:  # Moving left
                    self.rect.left = o.rect.right
                self.position.x, _ = self.rect.topleft  # Reset precise position
                break  # break out of the loop (only handle first collision per axis)

        # move y and check collisions
        self.position.y += dy
        self.rect.topleft = self.position

        for o in game_world.static_objects:
            if self.rect.colliderect(o):  # Check collision
                if dy > 0:  # Falling down
                    self.rect.bottom = o.rect.top
                    self.velocity.y = 0
                    # self.on_ground = True
                elif dy < 0:  # Hitting the ceiling
                    self.rect.top = o.rect.bottom
                    self.velocity.y = 0
                _, self.position.y = self.rect.topleft  # Reset precise position
                break  # break out of the loop (only handle first collision per axis)


class LetterPickUp(InteractableObject):
    def __init__(self, position: pygame.Vector2, letter: str):
        self.letter = letter
        image = LETTER_IMAGES[letter]
        super().__init__(position, image, image)

    def on_collide(self, player, game_world) -> None:
        player.on_pickup_letter(self.letter)
        game_world.interactable_objects.remove(self)


class Enemy(MovingObject):

    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool):
        super().__init__(position, image, gravity)
        self.current_direction = 1

    def on_collide(self, player, game_world) -> None:
        """Is called on collision with player and reduces lives."""
        threshold = 5

        if player.velocity.y < 0 and player.rect.bottom <= self.rect.top + threshold:
            # If player jumps on top of it, enemy dies
            player.velocity.y = -250
            player.bounce_velocity_x = 0
            player.velocity.x = 0
            game_world.interactable_objects.remove(self)  # Remove enemy from the game
        else:
            player.on_hit_by_enemy(self, self.current_direction)


class Worm(Enemy):
    def __init__(self, position: pygame.Vector2):
        super().__init__(position, pygame.image.load(get_path("assets/test/worm.png")), True)
        self.speed_x = 10
        self.distance = 0
        self.max_distance = 50
        self.run = Animation("run", get_path('assets/sprites/anim/worm_walk.png'), 32, 16, 5, 10)
        #self.die = Animation(get_path(), 32, 16, x, 10)

        self.active_animation = self.run
        self.animator = Animator(self.active_animation)

    def check_animation(self) -> None:
        # if self.is_dead:
        #   self.set_animation(self.die)
        # else:
        #   pass
        pass

    def set_animation(self, animation):
        if self.active_animation.name != animation.name:
            self.active_animation = animation
            self.animator = Animator(animation)
            self.animator.reset_animation(animation)

    def update(self, delta: float, game_world):

        self.velocity.x = self.current_direction * self.speed_x

        super().update(delta, game_world)

        if not self.has_collided:
            self.distance += abs(self.velocity.x * delta)

        if self.distance >= self.max_distance or self.has_collided:
            self.current_direction *= (-1)
            self.distance = 0
            self.has_collided = False

        self.animator.update()

    def draw(self, screen, camera_pos):
        position = self.rect.topleft - camera_pos
        screen.blit(self.animator.get_frame(self.current_direction), position)
        # Draw hit box, just for debugging:
        # pygame.draw.rect(screen, (255, 0, 0), self.rect.move(-camera_pos), 2)
