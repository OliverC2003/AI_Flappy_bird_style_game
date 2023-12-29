import pygame
import random
import os
import neat

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
            self.velocity_y = max(10, (self.fall_count//fps)*self.gravity)
            self.fall_count += 1

    def check_top_bottom(self):
        if (self.Y >= self.bot) or (self.Y <= self.top): 
            self.velocity_y = 0
            self.dead = 1

    def jump(self):
        self.velocity_y = self.jump_speed
        

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


def draw_screen():
    window.blit(background, (0, 0))
    spikes_group.draw(window)

def eval_genomes(genomes, config):
    

    nets = []
    ge = []
    players = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(100, 300))
        ge.append(g)
    
    run = True
    while run:
        global last_spike_spawn_time

        current_time = pygame.time.get_ticks()
        if current_time - last_spike_spawn_time >= spike_spawn_interval:
            x = 1300
            y = random.randint(0, 450)
            spikes_group.add(Spikes(x, y))
            last_spike_spawn_time = current_time

        spikes_list = list(spikes_group)
        ind_spike = 0
        if len(spikes_list) == 0:
            continue
        elif len(players) > 0:
            if len(spikes_group) > 1 and players[0].rect.x > spikes_list[0].rect.x + spikes_list[0].rect.width:
                ind_spike = 1


        else:
            for spike in spikes_group:
                spike.kill()
            run = False
            print("Banged")
            break
        
        #print(ind_spike)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                print("banged1")
                pygame.quit()
                quit()
        
        timer.tick(fps)
        draw_screen()
        
        
        for i in range(len(players) - 1, -1, -1):
            player = players[i]
            player.update()
            player.draw(window)
            if player.Y <= 180 or player.Y >= 450:    #the players seem to tend towards the upper and lower parts of the screen due to nature of game, lets adjust fitness to counteract this
                ge[i].fitness -= 0.05
                print("111")
            else:
                ge[i].fitness += 0.05

            # diff_Y = abs(player.Y - spikes_list[ind_spike].Y)
            # diff_X = abs(spikes_list[ind_spike].rect.x - (player.rect.x + player.rect.width))
            diff_ceiling = abs(player.top - player.Y)
            diff_floor = abs(player.bot - player.Y)
            diff_Y_top = abs((spikes_list[ind_spike].rect.y + spikes_list[ind_spike].rect.height) - player.rect.y)
            diff_Y_bot = abs(spikes_list[ind_spike].rect.y - (player.rect.y + player.rect.height))

            output = nets[i].activate((player.Y,diff_ceiling, diff_floor, diff_Y_top, diff_Y_bot, player.velocity_y))

            if output[0] > 0.5:
                player.jump()

            if pygame.sprite.spritecollideany(player, spikes_group, pygame.sprite.collide_mask): #checks for pixel perfect Collision
                ge[i].fitness -= 3
                player.dead = 1 
            for spike in spikes_group:
                if spike.X == player.X - 150: #If we pass an obstacle, improve fitness function 
                    ge[i].fitness += 10
            if player.dead == 1: #If the character has died (touched floor, ceiling, spike), we reduce the fitness function
                ge[i].fitness -= 0.5
                players.pop(i)
                nets.pop(i)
                ge.pop(i)
        pygame.display.update()
        spikes_group.update() 

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)

    pop = neat.Population(config)

    winner = pop.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
