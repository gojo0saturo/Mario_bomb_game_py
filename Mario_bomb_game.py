import pygame
import random
import os

pygame.init()
WIDTH, HEIGHT = 1100, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Mario Bomb Game")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

player_img_left = pygame.transform.flip(player_img_right, True, False)
player_img_up = pygame.transform.rotate(player_img_right, 90)
player_img_down = pygame.transform.rotate(player_img_right, -90)

player_img_right = pygame.transform.scale(pygame.image.load("load/player1.png"), (50, 50))
coin_img = pygame.transform.scale(pygame.image.load("load/coin.png"), (30, 30))
enemy_img = pygame.transform.scale(pygame.image.load("load/enemy.png"), (50, 50))
bomb_img = pygame.transform.scale(pygame.image.load("load/bomb.png"), (20, 20))
background_imgs = [pygame.transform.scale(pygame.image.load(f"load/bg{i}.png"), (WIDTH, HEIGHT)) for i in range(1, 4)]

def update_player_image(direction):
    if direction == "left": return player_img_left
    if direction == "right": return player_img_right
    if direction == "up": return player_img_up
    if direction == "down": return player_img_down
    return player_img_right

def draw_health(health):
    pygame.draw.rect(screen, RED, (WIDTH - 310, 20, 240, 20))
    pygame.draw.rect(screen, GREEN, (WIDTH - 310, 20, health, 20))

def draw_minimap(player, enemies):
    pygame.draw.rect(screen, BLACK, (WIDTH - 150, HEIGHT - 100, 130, 80))
    pygame.draw.rect(screen, GREEN, (WIDTH - 150 + player.x * 0.1, HEIGHT - 90, 10, 10))
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (WIDTH - 150 + enemy.x * 0.1, HEIGHT - 90, 10, 10))

def show_start_screen():
    font = pygame.font.SysFont(None, 48)
    while True:
        screen.blit(background_imgs[0], (0, 0))
        msg = font.render("PRESS ENTER TO START", True, WHITE)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return

def reset_game():
    player = pygame.Rect(100, HEIGHT - 150, 50, 50)
    player_health = 240
    player_direction = "right"
    coin_score = 0
    kills = 0
    level = 1
    player_vel_y = 0
    on_ground = True

    platforms = [
        pygame.Rect(200, HEIGHT - 200, 200, 20),
        pygame.Rect(500, HEIGHT - 300, 200, 20),
        pygame.Rect(800, HEIGHT - 250, 200, 20)
    ]

    coins = [pygame.Rect(random.randint(50, WIDTH - 80), HEIGHT - 130, 30, 30) for _ in range(20)]
    coins += [pygame.Rect(p.x + p.width // 2 - 15, p.y - 30, 30, 30) for p in platforms]

    enemies = [pygame.Rect(200 + i * 100, HEIGHT - 150, 50, 50) for i in range(10)]
    enemy_dirs = [random.choice([-1, 1]) for _ in enemies]
    bombs = []

    return player, player_vel_y, on_ground, player_health, player_direction, coins, coin_score, enemies, enemy_dirs, bombs, kills, level, platforms

GRAVITY = 1
JUMP_STRENGTH = 20
MAX_LEVEL = 20
COINS_PER_LEVEL = 20
KILLS_PER_LEVEL = 10

show_start_screen()
player, player_vel_y, on_ground, player_health, player_direction, coins, coin_score, enemies, enemy_dirs, bombs, kills, level, platforms = reset_game()

running = True
while running:
    screen.blit(pygame.transform.scale(background_imgs[(level - 1) % len(background_imgs)], (WIDTH, HEIGHT)), (0, 0))
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            player, player_vel_y, on_ground, player_health, player_direction, coins, coin_score, enemies, enemy_dirs, bombs, kills, level, platforms = reset_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
        player_direction = "left"
    if keys[pygame.K_RIGHT]:
        player.x += 5
        player_direction = "right"
    if keys[pygame.K_UP]:
        player.y -= 5
        player_direction = "up"
    if keys[pygame.K_DOWN]:
        player.y += 5
        player_direction = "down"
    if keys[pygame.K_SPACE] and on_ground:
        player_vel_y = -JUMP_STRENGTH
        on_ground = False
    if keys[pygame.K_b]:
        bomb = pygame.Rect(player.centerx, player.centery, 20, 20)
        dx = dy = 0
        if player_direction == "left": dx = -7
        elif player_direction == "right": dx = 7
        elif player_direction == "up": dy = -7
        elif player_direction == "down": dy = 7
        bombs.append({"rect": bomb, "dx": dx, "dy": dy})

    player_vel_y += GRAVITY
    player.y += player_vel_y

    if player.bottom >= HEIGHT - 100:
        player.bottom = HEIGHT - 100
        player_vel_y = 0
        on_ground = True

    for plat in platforms:
        if player.colliderect(plat) and player_vel_y >= 0:
            player.bottom = plat.top
            player_vel_y = 0
            on_ground = True

    for i, enemy in enumerate(enemies):
        enemy.x += enemy_dirs[i]
        if enemy.left <= 0 or enemy.right >= WIDTH:
            enemy_dirs[i] *= -1

        if player.colliderect(enemy):
            if player.bottom <= enemy.top + 10 and player_vel_y > 0:
                enemies.remove(enemy)
                kills += 1
                player_vel_y = -JUMP_STRENGTH // 2
            else:
                player_health -= 1
                if player_health <= 0:
                    running = False

    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            coin_score += 1

    for bomb in bombs[:]:
        bomb["rect"].x += bomb["dx"]
        bomb["rect"].y += bomb["dy"]
        if not screen.get_rect().colliderect(bomb["rect"]):
            bombs.remove(bomb)
        else:
            for enemy in enemies[:]:
                if bomb["rect"].colliderect(enemy):
                    enemies.remove(enemy)
                    bombs.remove(bomb)
                    kills += 1
                    break

    if coin_score >= COINS_PER_LEVEL * (2 ** (level - 1)) or kills >= KILLS_PER_LEVEL * (2 ** (level - 1)):
        level += 1
        WIDTH += 100
        HEIGHT += 50
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        enemies += [pygame.Rect(random.randint(50, WIDTH - 80), HEIGHT - 150, 50, 50) for _ in range(3)]
        enemy_dirs += [random.choice([-1, 1]) for _ in range(3)]
        coins += [pygame.Rect(random.randint(50, WIDTH - 80), HEIGHT - 130, 30, 30) for _ in range(10)]
        coins += [pygame.Rect(p.x + p.width // 2 - 15, p.y - 30, 30, 30) for p in platforms]

    player_img = update_player_image(player_direction)
    screen.blit(player_img, player)
    for coin in coins:
        screen.blit(coin_img, coin)
    for enemy in enemies:
        screen.blit(enemy_img, enemy)
    for bomb in bombs:
        screen.blit(bomb_img, bomb["rect"])
    for plat in platforms:
        pygame.draw.rect(screen, (100, 100, 100), plat)

    draw_health(player_health)
    draw_minimap(player, enemies)

    font = pygame.font.SysFont(None, 36)
    screen.blit(font.render(f"Coins: {coin_score}", True, BLACK), (20, 20))
    screen.blit(font.render(f"Kills: {kills}", True, BLACK), (20, 60))
    screen.blit(font.render(f"Level: {level}", True, BLACK), (20, 100))
    screen.blit(font.render(f"Next: {COINS_PER_LEVEL * (2 ** (level - 1))} Coins or {KILLS_PER_LEVEL * (2 ** (level - 1))} Kills", True, BLACK), (20, 140))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()