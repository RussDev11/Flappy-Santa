import pygame
from pygame.locals import *
import random
import os

pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 850
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Santa')

# Background music
pygame.mixer.music.load("bgmusic/bgmusic.mp3")
pygame.mixer.music.play(-1)

# Game Over sound
game_over_music = pygame.mixer.Sound("bgmusic/gameover.mp3")  

# Define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Define colors
white = (255, 255, 255)

# Define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
high_score = 0  # To store the highest score

# Load images
bg = pygame.image.load('img/snowbg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function to reset the game
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    return 0

# Function to show instructions at the start of the game
def show_instructions():
    font = pygame.font.SysFont('Bauhaus', 50)
    screen.blit(bg, (0, 0))
    draw_text("FLAPPY SANTA", font, white, screen_width // 3, screen_height // 3 + 40)
    draw_text("Press SPACEBAR or Click to Play", font, white, screen_width // 7, screen_height // 2 - 30)
    draw_text("Score points by passing through pipes!", font, white, screen_width // 7, screen_height // 2 + 30)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == K_SPACE):
                waiting = False

# Load the high score from a file
def load_high_score():
    global high_score
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as file:
            high_score = int(file.read())
    else:
        high_score = 0

# Save the high score to a file
def save_high_score():
    with open("highscore.txt", "w") as file:
        file.write(str(high_score))

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/santa{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        global flying
        if flying:
            # Apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            # Jump on mouse click or spacebar
            keys = pygame.key.get_pressed()
            if (pygame.mouse.get_pressed()[0] == 1 or keys[K_SPACE]) and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0 and not keys[K_SPACE]:
                self.clicked = False

            # Handle animation
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # Point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe1.png")
        self.rect = self.image.get_rect()
        # Position variable determines if the pipe is coming from the bottom or top
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # Get mouse position
        pos = pygame.mouse.get_pos()
        # Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

# Load the highest score
load_high_score()

# Show instructions before starting the game
show_instructions()

run = True
while run:
    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))

    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()

    # Draw and scroll the ground
    screen.blit(ground_img, (ground_scroll, 768))

    # Check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and \
                bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    # Draw the current score
    draw_text(f"{score}", font, white, int(screen_width / 2) - 50, 20)

    # Look for collision (bird and pipes)
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        if not game_over:
            game_over = True
            game_over_music.play()

    # Once the bird has hit the ground, it's game over and no longer flying
    if flappy.rect.bottom >= 768:
        if not game_over:
            game_over = True
            flying = False
            game_over_music.play()

    if flying and not game_over:
        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()

        # Scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    # Handle game over and reset
    if game_over:
        if score > high_score:
            high_score = score
            save_high_score()  # Save the new high score

        # Show the restart button
        if button.draw():
            game_over = False
            score = reset_game()
            game_over_music.stop()

        # Draw the high score only after the game is over
        draw_text(f"High Score: {high_score}", font, white, int(screen_width / 2) - 150, 80)

    # Handle events like quitting and starting the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if (event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == K_SPACE)) and not flying and not game_over:
            flying = True

    pygame.display.update()

# Quit pygame
pygame.quit()
