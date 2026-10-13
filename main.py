# ============================================================
# Zombie Simulation - CPS310 Assignment 1
# Author: Reese Franklin
#
# An agent-based simulation: humans wander, zombies chase them.
# When they touch, they fight. The human either kills the zombie
# or gets infected and becomes a zombie. The populations change
# over time, and each run can end differently.
# ============================================================

import pygame   # the game library: window, drawing, keyboard input
import random   # random numbers: starting positions, speeds, fight results
import math     # math tools: distance (hypot), angles (cos, sin, pi)

# ---------- SETUP ----------
pygame.init()  # start pygame (always the first thing)

WIDTH, HEIGHT = 800, 600                            # window size in pixels
screen = pygame.display.set_mode((WIDTH, HEIGHT))   # the window we draw on
pygame.display.set_caption("Zombie Simulation")     # title at the top of the window
clock = pygame.time.Clock()                         # controls how fast the loop runs
font = pygame.font.SysFont(None, 28)                # small text (counter)
big_font = pygame.font.SysFont(None, 60)            # big text (win message)

# ---------- SETTINGS ----------
# All the numbers that control the simulation, in one place.
# Change these to change the balance of the game.
NUM_HUMANS = 20
NUM_ZOMBIES = 3
FIGHT_CHANCE = 0.4  # chance a human kills the zombie instead of being infected
TIME_LIMIT = 45     # seconds until rescue arrives
FPS = 60            # frames (loop runs) per second


# ---------- HUMAN AGENT ----------
# A class is a blueprint. Every human is built from this blueprint,
# but each one has its own position, direction, and speed.
class Human:
    def __init__(self):
        # Runs once when a human is created.
        # Start at a random spot on the screen.
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

        # Pick a random direction and a random speed SEPARATELY.
        # (Bug fix: picking random x and y speeds separately made
        # diagonal humans about 1.4x faster than zombies could catch.)
        angle = random.uniform(0, 2 * math.pi)  # any direction around a full circle
        speed = random.uniform(0.5, 1.4)        # always slower than zombies (1.5)

        # cos and sin split the speed into a horizontal part (dx)
        # and a vertical part (dy), so total speed stays the same.
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    def update(self):
        # Runs every frame: move a little in our direction.
        self.x += self.dx
        self.y += self.dy

        # If we hit a wall, flip that direction so we bounce back.
        if self.x < 0 or self.x > WIDTH:
            self.dx = -self.dx
        if self.y < 0 or self.y > HEIGHT:
            self.dy = -self.dy

    def draw(self):
        # Draw a blue circle (radius 6) at our position.
        pygame.draw.circle(screen, (0, 200, 255), (int(self.x), int(self.y)), 6)


# ---------- ZOMBIE AGENT ----------
class Zombie:
    def __init__(self, x=None, y=None):
        # If we're given a position (a bitten human's spot), start there.
        # If not, start somewhere random.
        self.x = x if x is not None else random.randint(0, WIDTH)
        self.y = y if y is not None else random.randint(0, HEIGHT)
        self.speed = 1.5  # zombies are faster than every human

    def update(self, humans):
        # Runs every frame: find the closest human and move toward it.

        # Start with "no target" and a distance of infinity,
        # so the first human we check is always closer.
        closest = None
        closest_dist = float("inf")

        # Check every human and remember the closest one.
        for h in humans:
            d = math.hypot(h.x - self.x, h.y - self.y)  # straight-line distance
            if d < closest_dist:
                closest = h
                closest_dist = d

        # Move toward the closest human (if there is one).
        if closest is not None and closest_dist > 0:
            dx = closest.x - self.x
            dy = closest.y - self.y
            # Dividing by the distance makes a step of size 1 in the right
            # direction. Multiplying by speed makes every zombie move at the
            # same steady speed, no matter how far away the human is.
            self.x += dx / closest_dist * self.speed
            self.y += dy / closest_dist * self.speed

    def draw(self):
        # Draw a green circle (radius 7) at our position.
        pygame.draw.circle(screen, (80, 220, 80), (int(self.x), int(self.y)), 7)


# ---------- STARTING A GAME ----------
def new_game():
    # Create a fresh set of agents and reset the timer.
    # Used at the start and whenever R is pressed.
    humans = [Human() for _ in range(NUM_HUMANS)]     # list of 20 humans
    zombies = [Zombie() for _ in range(NUM_ZOMBIES)]  # list of 3 zombies
    frames = 0                                        # timer, counted in frames
    return humans, zombies, frames


humans, zombies, frames = new_game()


# ---------- GAME LOOP ----------
# Runs 60 times per second. Each time: 1) input  2) update  3) draw
running = True
while running:

    # 1) INPUT: check what the user did since the last frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:       # clicked the X
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # pressed R
            humans, zombies, frames = new_game()

    # Convert frames to seconds (// means divide and drop the decimal)
    seconds = frames // FPS

    # The game is over if either side is wiped out or time is up
    game_over = len(humans) == 0 or len(zombies) == 0 or seconds >= TIME_LIMIT

    # 2) UPDATE: only while the game is still going
    #    (so the screen freezes on the final result)
    if not game_over:
        frames += 1

        # Every agent moves
        for h in humans:
            h.update()
        for z in zombies:
            z.update(humans)  # zombies need the human list to find a target

        # FIGHTS: check every zombie against every human.
        # We collect changes in these lists and apply them AFTER the loop,
        # because changing a list while looping over it makes Python skip items.
        new_zombies = []
        dead_zombies = []
        for z in zombies:
            for h in humans[:]:  # [:] loops over a COPY so removing humans is safe
                # Touching = closer than 13 pixels (human radius 6 + zombie radius 7)
                if math.hypot(h.x - z.x, h.y - z.y) < 13:
                    # random.random() gives a number from 0 to 1.
                    # It's below 0.4 about 40% of the time.
                    if random.random() < FIGHT_CHANCE:
                        # Human wins: this zombie is destroyed
                        dead_zombies.append(z)
                        break  # this zombie is dead, stop checking it
                    else:
                        # Zombie wins: the human becomes a new zombie in the same spot
                        humans.remove(h)
                        new_zombies.append(Zombie(h.x, h.y))

        # Now apply the changes
        for z in dead_zombies:
            zombies.remove(z)
        zombies.extend(new_zombies)

    # 3) DRAW: paint everything for this frame
    screen.fill((30, 30, 30))  # dark background (wipes the last frame)
    for h in humans:
        h.draw()
    for z in zombies:
        z.draw()

    # Population counter and timer in the top-left corner
    counter = font.render(
        f"Humans: {len(humans)}   Zombies: {len(zombies)}   Time: {seconds}/{TIME_LIMIT}s",
        True, (255, 255, 255))
    screen.blit(counter, (10, 10))  # blit = paste the text onto the screen

    # If the game is over, show who won in the middle of the screen
    message = None
    if len(zombies) == 0:
        message = "Humans survived!"
    elif len(humans) == 0:
        message = "Zombies took over!"
    elif seconds >= TIME_LIMIT:
        message = "Rescue arrived!"  # time ran out: surviving humans are rescued
    if message:
        text = big_font.render(message, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        hint = font.render("Press R to restart", True, (200, 200, 200))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

    pygame.display.flip()  # show everything we just drew
    clock.tick(FPS)        # wait so the loop runs 60 times per second

# The loop ended (window closed), so shut pygame down
pygame.quit()