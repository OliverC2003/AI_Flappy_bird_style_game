import pygame
import random

pygame.init()
window_size = (1280, 720)

pygame.display.set_caption("Flight in Wonderland")

window = pygame.display.set_mode(window_size)
fps = 60
timer = pygame.time.Clock()
background = pygame.image.load('ForestBG2.jpg').convert()
background = pygame.transform.scale(background, (window_size))
main_character_down = pygame.image.load('fall.png').convert_alpha()
main_character_down = pygame.transform.scale(main_character_down, (80, 80))
font = pygame.font.Font(None, 72)
font2 = pygame.font.Font(None, 180)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.image_up = pygame.image.load('jump.png').convert_alpha()
        self.image_up = pygame.transform.scale(self.image_up, (80, 80))
        self.image_down = pygame.image.load('fall.png').convert_alpha()
        self.image_down = pygame.transform.scale(self.image_down, (80, 80))
        self.image = self.image_up
        self.X = x
        self.Y = y
        self.velocity_y = 0
        self.score = 0
        self.fall_count = 0
        self.gravity = 5
        self.jump_speed = -10
        self.top = -10
        self.bot = 640
        self.rect = self.image.get_rect(topleft=(self.X, self.Y))
        self.dead = 0
        self.mask = pygame.mask.from_surface(self.image)   

    def calc_velocity(self):
        #If spacebar then move up
        if keys[pygame.K_SPACE]:
            self.velocity_y = self.jump_speed
            self.fall_count = 0
        #lets create the case of gravity
        else:
            self.velocity_y = max(10, (self.fall_count//fps)*self.gravity)
            self.fall_count += 1

    def check_top_bottom(self):
        if (self.Y == self.bot and not keys[pygame.K_SPACE] ) or (self.Y == self.top and keys[pygame.K_SPACE]): 
            self.velocity_y = 0
            self.dead = 1

        

    def move(self, dy):
        self.Y += dy
        self.rect.y = self.Y

    def update(self):
        self.move(self.velocity_y)
        if self.velocity_y <= 0:
            self.image = self.image_down
        else:
            self.image = self.image_up
        self.calc_velocity()
        self.check_top_bottom()

    def draw(self, win):
        win.blit(self.image, self.rect)

class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.vel_X = -10
        self.X = x
        self.Y = y
        self.image = pygame.image.load('SpikedBall3.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (270, 270))
        self.rect = self.image.get_rect(topleft=(self.X, self.Y))
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dx):
        self.X += dx
        self.rect.x = self.X

    def update(self):
        if self.X < -300:
            self.kill() #deletes ball off screen
        self.move(self.vel_X)

    def draw(self, win):
        win.blit(self.image, self.rect)   
        
spikes_group = pygame.sprite.Group() #Creates a group of Spikes


last_spike_spawn_time = 0
spike_spawn_interval = 1000

def gameplay_loop():
    timer.tick(fps)
    draw_screen()
    global last_spike_spawn_time

    current_time = pygame.time.get_ticks()
    if current_time - last_spike_spawn_time >= spike_spawn_interval:
        x = 1300
        y = random.randint(0, 450)
        spikes_group.add(Spikes(x, y))
        last_spike_spawn_time = current_time

    if pygame.sprite.spritecollideany(player, spikes_group, pygame.sprite.collide_mask): #checks for pixel perfect Collision  
        player.dead = 1 
    for spike in spikes_group:
        if spike.X == player.X - 150:
            player.score += 1       

    spikes_group.update()
    player.update()
    pygame.display.update()
    pygame.display.flip()

def end_screen_loop():
    for spike in spikes_group:
        spike.vel_X = 0
    player.velocity_y = 0

    show_end_screen()
    pygame.display.flip()

    if keys[pygame.K_SPACE]:
        for spike in spikes_group:
            spike.kill()
        player.X = 100
        player.Y = 300
        player.dead = 0
        player.score = 0


def draw_screen():
    window.blit(background, (0, 0))
    player.draw(window)
    spikes_group.draw(window)
    score_text = font.render(f'Score: {player.score}', True, (255, 255, 255))  # White color
    window.blit(score_text, (10, 10))  # Position the text at (10, 10) from the top-left corner

def show_end_screen():
    window.blit(background, (0, 0))
    score_text = font2.render(f'Score: {player.score}', True, (255, 255, 255))  # White color
    player.draw(window)
    spikes_group.draw(window)
    window.blit(score_text, (300, 300))


player = Player(100, 300)

run = True
while run:
    spikes_list = list(spikes_group)
    print(len(spikes_list))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    if player.dead == 0:
        keys = pygame.key.get_pressed()
        gameplay_loop()

    elif player.dead == 1:
        keys = pygame.key.get_pressed()
        end_screen_loop()

pygame.quit()