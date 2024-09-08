# ипорты
from pygame import *
from random import randint
from time import time as timer
import sys
import os
 
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    elif hasattr(sys, "_MEIPASS2"):
        return os.path.join(sys._MEIPASS2, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)
 
image_folder = resource_path(".")
mixer.init()
font.init()

# константы
WIDTH = 700
HEIGHT = 500
GREEN = (0, 255, 0) 
RED = (255, 0, 0)
YELLOW = (250, 255, 0)
FPS = 60



# музыка
music_back = os.path.join(image_folder, 'space.ogg')
sound_fire = os.path.join(image_folder, 'fire.ogg')

mixer.music.load(music_back)
mixer.music.play(-1)
mixer.music.set_volume(0.1)
fire = mixer.Sound(sound_fire)

# текст
font_text = font.Font(None, 80)
font_score = font.Font(None, 36)


score_text = font_score.render('Счёт :', True, (255, 255, 255))

win_text = font_text.render(f"You win :D", True, GREEN)
lose_text = font_text.render(f"You lose D:", True, RED)




# счёт
score = 0
lost = 0
max_score = 10
max_lose = 5
lifes = 3


# спрайты
img_hero = os.path.join(image_folder, 'rocket.png')
img_enemy = os.path.join(image_folder, 'ufo.png')
img_back = os.path.join(image_folder, 'galaxy.jpg')
img_bullet = os.path.join(image_folder, 'bullet.png')
img_asteroid = os.path.join(image_folder, 'asteroid.png')

icon = os.path.join(image_folder, 'ufo.png')
display.set_icon(image.load(icon))


class GameSprite(sprite.Sprite):
    def __init__(self, p_img: str, x: int, y: int, w: int, h: int, speed: int):
        super().__init__()
        self.image = transform.scale(image.load(p_img), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, p_img: str, x: int, y: int, w: int, h: int, speed: int, max_bullets: int):
        super().__init__(p_img, x, y, w, h, speed)
        self.max_bullets = max_bullets
        self.current_bullets = max_bullets
        self.last_reload_time = 0
        self.reload_duration = 3
        
        self.reloading = False

    def update(self):
        keys_pressed = key.get_pressed()
        
        if keys_pressed[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < 640:
            self.rect.x += self.speed
    
    def fire(self):
        if self.current_bullets > 0:
            bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 5)
            bullets.add(bullet)
            self.current_bullets -= 1
        else:
            self.start_reload()
    
    def start_reload(self):
        self.reloading = True
        self.last_reload_time = timer()
    
    def reload(self):
        if self.reloading:
            now_time = timer()
            if now_time - self.last_reload_time >= self.reload_duration:
                self.current_bullets = self.max_bullets
                self.reloading = False




class Enemy(GameSprite):
    def __init__(self, p_img: str, x: int, y: int, w: int, h: int, speed: int):
        super().__init__(p_img, x, y, w, h, speed)
    
    def update(self):
        global lost
        self.rect.y += self.speed
        
        if self.rect.y == HEIGHT - 50:
            self.rect.x = randint(1, WIDTH - 100)
            self.rect.y = 0
            lost += 1

class Asteroid(GameSprite):
    def __init__(self, p_img: str, x: int, y: int, w: int, h: int, speed: int):
        super().__init__(p_img, x, y, w, h, speed)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.y == HEIGHT - 50:
            self.rect.x = randint(1, WIDTH - 100)
            self.rect.y = 0

        


class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

class AmmoIndicator(sprite.Sprite):
    def __init__(self, p_img: str, x: int, y: int, w: int, h: int, speed: int, max_bullets: int):
        super().__init__()
        self.image = transform.scale(image.load(p_img), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.max_bullets = max_bullets
    
    def update(self, current_bullets):
        self.rect.x = WIDTH - self.rect.width - 10
        self.rect.y = HEIGHT - self.rect.height
        for i in range(self.max_bullets):
            if i < current_bullets:
                window.blit(self.image, (self.rect.x - i * (self.rect.width + 5), self.rect.y))




## игрок
player = Player(img_hero, 0, HEIGHT - 100, 60, 100, 5, 10)

## пуля

bullets = sprite.Group()
ammo_indicator = AmmoIndicator(img_bullet, WIDTH - 10, HEIGHT - 10, 15, 20, 5, 10)



## враги
monsters = sprite.Group()

for i in range(6):
    monster = Enemy(img_enemy, randint(1, WIDTH - 100), -50, 100, 50, randint(1, 2))
    monsters.add(monster)

## астероиды
asteroids = sprite.Group()

for i in range(3):
    asteroid = Asteroid(img_asteroid, randint(1, WIDTH - 100), -50, 70, 70, randint(1, 2))
    asteroids.add(asteroid)
     

# основной экран
window = display.set_mode((WIDTH, HEIGHT))
display.set_caption('Шутер')
background = transform.scale(image.load(img_back), (WIDTH, HEIGHT))
clock = time.Clock()

# Игровой цикл
run = True
finish = False

keys_pressed = key.get_pressed()

def restart_game():
    global score, lost, finish, lifes
    score = 0 
    lost = 0
    finish = False
    mixer.music.play()

    player.reloading = True

    for b in bullets:
        b.kill()
    
    for m in monsters:
        m.kill()
    
    for a in asteroids:
        a.kill()
    
    lifes = 3
    
    for i in range(6):
        monster = Enemy(img_enemy, randint(1, WIDTH - 100), -50, 100, 50, randint(1, 2))
        monsters.add(monster)
    
    for i in range(3):
        asteroid = Asteroid(img_asteroid, randint(1, WIDTH - 100), -50, 70, 70, randint(1, 2))
        asteroids.add(asteroid)

    

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False

                    
        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                player.fire()
                fire.play()
            if e.key == K_r:
                restart_game()



    if not finish:
        window.blit(background, (0, 0))
        # игрок
        player.reset()
        player.update()
        
        # враг
        monsters.draw(window)
        monsters.update()
        
        # пуля
        bullets.draw(window)

        bullets.update()

        ammo_indicator.update(player.current_bullets)
        if player.reloading:
            reload_text = font_score.render('ПЕРЕЗАРЯДКА...', True, RED)
            window.blit(reload_text, (250, 450))
            player.reload()
        
        # астероиды
        asteroids.draw(window)
        asteroids.update()
        
        
        
        # текст
        score_text = font_score.render('Счёт: ' + str(score), True, (255, 255, 255))
        window.blit(score_text, (0, 0))

        lost_text = font_score.render('Пропущено: ' + str(lost), True, (255, 255, 255))
        window.blit(lost_text, (0, 40))

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for collides in collides:
            score += 1
            monster = Enemy(img_enemy, randint(1, WIDTH - 100), -50, 100, 50, randint(1, 2))
            monsters.add(monster)

        if sprite.spritecollide(player, monsters, False) or sprite.spritecollide(player, asteroids, False):
            sprite.spritecollide(player, asteroids, True)
            sprite.spritecollide(player, monsters, True)
            lifes -= 1

        sprite.groupcollide(asteroids, bullets, False, True)


        
        if score == max_score:
            finish = True
            window.blit(win_text, (200, 200))
        
        
        if lifes == 0 or lost >= max_lose:
            finish = True
            
            window.blit(lose_text, (200, 200))

        if lifes >= 3:
            life_color = GREEN
        elif lifes == 2:
            life_color = YELLOW
        elif lifes == 1:
            life_color = RED

        text_life = font_score.render('Жизни: ' + str(lifes), True, life_color)
        window.blit(text_life, (570, 0))


    display.update()
    clock.tick(FPS)



