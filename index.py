import pygame
import random
import math
import sys
from tkinter import *
from tkinter import messagebox
from pygame import mixer
from array import array

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
FPS = 15

# Colors
COLORS = {
    "background": ["#1a1a1a", "#2d2d2d", "#404040"],
    "snake": ["#00ff00", "#00cc00", "#009900"],
    "food": ["#ff0000", "#cc0000", "#990000"],
    "text": "#ffffff",
    "effect": "#ffd700"
}

# Game Settings
SETTINGS = {
    "speeds": [15, 12, 15, 18, 20],
    "foods_to_next": [5, 8, 10, 12, 15],
    "obstacles": [4, 2, 4, 6, 8]
}

# توليد الأصوات (الإصدار المعدل)
def generate_sound(frequency=440, duration=0.1, wave_type='square', volume=0.5):
    sample_rate = 44100
    period = int(sample_rate / frequency)
    amplitude = 2 ** (abs(mixer.get_init()[2]) - 1) - 1
    samples = []
    
    for i in range(int(duration * sample_rate)):
        if wave_type == 'square':
            value = int(amplitude * volume) if (i % period) < (period // 2) else -int(amplitude * volume)
        elif wave_type == 'sine':
            value = int(amplitude * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.append(value)
    
    return pygame.mixer.Sound(array('h', samples))

# تهيئة الأصوات
mixer.init(frequency=44100, size=-16, channels=1)
eat_sound = generate_sound(784, 0.1, 'square', 0.3)
level_up_sound = generate_sound(1568, 0.3, 'sine', 0.5)
game_over_sound = generate_sound(220, 0.8, 'square', 0.4)

# -----------------------------------------------------------------
# كل ما يلي يبقى كما هو بدون أي تعديلات
# -----------------------------------------------------------------

class Snake:
    def __init__(self):
        self.body = []
        self.direction = "RIGHT"
        self.length = 7
        start_x = WIDTH//2
        start_y = HEIGHT//2
        
        for i in range(self.length):
            self.body.append([start_x - (i * CELL_SIZE), start_y])
            
        self.skin = 0
        
    def move(self):
        head = self.body[0].copy()
        
        if self.direction == "RIGHT":
            head[0] += CELL_SIZE
        elif self.direction == "LEFT":
            head[0] -= CELL_SIZE
        elif self.direction == "UP":
            head[1] -= CELL_SIZE
        elif self.direction == "DOWN":
            head[1] += CELL_SIZE
            
        self.body.insert(0, head)
        if len(self.body) > self.length:
            self.body.pop()
            
    def grow(self):
        self.length += 1
        
    def draw(self, surface):
        for i, segment in enumerate(self.body):
            color = COLORS["snake"][self.skin]
            intensity = 255 - (i * 5)
            pygame.draw.rect(surface, color, (segment[0], segment[1], CELL_SIZE-1, CELL_SIZE-1))
            
    def check_collision(self):
        head = self.body[0]
        if (head[0] < 0 or head[0] >= WIDTH or 
            head[1] < 0 or head[1] >= HEIGHT):
            return True
        for segment in self.body[1:]:
            if head == segment:
                return True
        return False

class Food:
    def __init__(self, level):
        self.position = []
        self.level = level
        self.respawn()
        
    def respawn(self):
        self.position = [
            random.randrange(1, (WIDTH//CELL_SIZE)-1) * CELL_SIZE,
            random.randrange(1, (HEIGHT//CELL_SIZE)-1) * CELL_SIZE
        ]
        
    def draw(self, surface):
        pygame.draw.rect(surface, COLORS["food"][self.level%3], 
                       (self.position[0], self.position[1], CELL_SIZE, CELL_SIZE))

class Obstacle:
    def __init__(self, level):
        self.blocks = []
        self.level = level
        self.generate_obstacles()
        
    def generate_obstacles(self):
        num_obstacles = SETTINGS["obstacles"][self.level]
        for _ in range(num_obstacles):
            block = [
                random.randrange(1, (WIDTH//CELL_SIZE)-1) * CELL_SIZE,
                random.randrange(1, (HEIGHT//CELL_SIZE)-1) * CELL_SIZE
            ]
            self.blocks.append(block)
            
    def draw(self, surface):
        for block in self.blocks:
            pygame.draw.rect(surface, "#0000ff", (block[0], block[1], CELL_SIZE, CELL_SIZE))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Advanced Snake Game")
        self.clock = pygame.time.Clock()
        self.level = 0
        self.score = 0
        self.level_score = 0
        self.high_score = 0
        self.running = True
        self.paused = False
        self.snake = Snake()
        self.food = Food(self.level)
        self.obstacle = Obstacle(self.level)
        self.load_high_score()
        self.effect_timer = 0
        self.camera_shake = 0
        
    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0
            
    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))
            
    def show_menu(self):
        menu = Tk()
        menu.title("Game Menu")
        menu.geometry("300x200")
        
        Label(menu, text="Snake Game", font=("Arial", 20)).pack(pady=10)
        Button(menu, text="New Game", command=lambda: [menu.destroy(), self.new_game()]).pack(pady=5)
        Button(menu, text="Continue", command=lambda: [menu.destroy(), self.run()]).pack(pady=5)
        Button(menu, text="Quit", command=sys.exit).pack(pady=5)
        
        menu.mainloop()
        
    def new_game(self):
        self.level = 0
        self.score = 0
        self.level_score = 0
        self.snake = Snake()
        self.food = Food(self.level)
        self.obstacle = Obstacle(self.level)
        self.run()
        
    def check_food_collision(self):
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 10 * (self.level + 1)
            self.level_score += 10
            eat_sound.play()
            self.food.respawn()
            self.effect_timer = 5
            self.camera_shake = 10
            
            if self.score > self.high_score:
                self.high_score = self.score
                
            if self.level_score >= SETTINGS["foods_to_next"][self.level] * 10:
                level_up_sound.play()
                self.level += 1
                self.level_score = 0
                if self.level >= len(SETTINGS["speeds"]):
                    self.level = len(SETTINGS["speeds"]) - 1
                self.obstacle = Obstacle(self.level)
                
    def check_obstacle_collision(self):
        for block in self.obstacle.blocks:
            if self.snake.body[0] == block:
                return True
        return False
    
    def draw_ui(self):
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {self.score}", True, COLORS["text"])
        level_text = font.render(f"Level: {self.level+1}", True, COLORS["text"])
        hi_score_text = font.render(f"High Score: {self.high_score}", True, COLORS["text"])
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))
        self.screen.blit(hi_score_text, (10, 70))
        
        required = SETTINGS["foods_to_next"][self.level] * 10
        progress = self.level_score / required
        pygame.draw.rect(self.screen, "#ffffff", (WIDTH-210, 10, 200, 20), 2)
        pygame.draw.rect(self.screen, "#00ff00", (WIDTH-208, 12, 196*progress, 16))
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    
                if not self.paused:
                    if event.key == pygame.K_RIGHT and self.snake.direction != "LEFT":
                        self.snake.direction = "RIGHT"
                    elif event.key == pygame.K_LEFT and self.snake.direction != "RIGHT":
                        self.snake.direction = "LEFT"
                    elif event.key == pygame.K_UP and self.snake.direction != "DOWN":
                        self.snake.direction = "UP"
                    elif event.key == pygame.K_DOWN and self.snake.direction != "UP":
                        self.snake.direction = "DOWN"
                        
    def run(self):
        while self.running:
            self.clock.tick(SETTINGS["speeds"][self.level])
            self.handle_input()
            
            if self.effect_timer > 0:
                self.effect_timer -= 1
            if self.camera_shake > 0:
                self.camera_shake -= 1
            
            if not self.paused:
                self.snake.move()
                
                if self.snake.check_collision() or self.check_obstacle_collision():
                    game_over_sound.play()
                    self.save_high_score()
                    self.game_over()
                    return
                
                self.check_food_collision()
                
                self.screen.fill(COLORS["background"][self.level%3])
                
                offset = (random.randint(-2, 2)*self.camera_shake, 
                        random.randint(-2, 2)*self.camera_shake)
                
                self.obstacle.draw(self.screen)
                self.snake.draw(self.screen)
                self.food.draw(self.screen)
                
                if self.effect_timer > 0:
                    overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    overlay.fill((255, 215, 0, 50))
                    self.screen.blit(overlay, self.food.position)
                
                self.draw_ui()
                
                pygame.display.update()
                
    def game_over(self):
        response = messagebox.askyesno("Game Over", 
                                     f"Score: {self.score}\nPlay again?")
        if response:
            self.new_game()
        else:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    game = Game()
    game.show_menu()