import math  # Importa o módulo math para cálculos matemáticos
import random  # Importa o módulo random para geração de números aleatórios

import pygame  # Importa a biblioteca pygame
from pygame import mixer  # Importa o mixer da biblioteca pygame

# Inicializa o pygame
pygame.init()

# Cria a tela do jogo
screen = pygame.display.set_mode((800, 600))

# Carrega o fundo
background = pygame.image.load('background.png')

# Carrega o som de fundo
mixer.music.load("background.wav")
mixer.music.play(-1)

# Configura o título e o ícone da janela do jogo
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Configurações do jogador
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 480
playerX_change = 0

# Configurações do inimigo
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(4)
    enemyY_change.append(40)

# Configurações da bala
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = "ready"

# Pontuação
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
textY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)


# Função para exibir a pontuação na tela
def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


# Função para exibir a mensagem de "Game Over" na tela
def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))


# Função para exibir o jogador na tela
def player(x, y):
    screen.blit(playerImg, (x, y))


# Função para exibir o inimigo na tela
def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


# Função para disparar a bala
def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


# Função para verificar colisões entre a bala e o inimigo
def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False


# Loop principal do jogo
running = True
while running:

    # Define a cor de fundo da tela
    screen.fill((0, 0, 0))
    # Exibe a imagem de fundo
    screen.blit(background, (0, 0))
    
    # Captura eventos do teclado e do mouse
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Verifica se alguma tecla foi pressionada
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.K_SPACE:
                if bullet_state is "ready":
                    bulletSound = mixer.Sound("laser.wav")
                    bulletSound.play()
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)

        # Verifica se alguma tecla foi solta
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    # Movimenta o jogador
    playerX += playerX_change
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    # Movimenta o inimigo
    for i in range(num_of_enemies):
        if enemyY[i] > 440:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break

        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0:
            enemyX_change[i] = 4
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -4
            enemyY[i] += enemyY_change[i]

        # Verifica colisões entre a bala e o inimigo
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            explosionSound = mixer.Sound("explosion.wav")
            explosionSound.play()
            bulletY = 480
            bullet_state = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, 736)
            enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)

    # Movimenta a bala
    if bulletY <= 0:
        bulletY = 480
        bullet_state = "ready"

    if bullet_state is "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change

    # Exibe o jogador e a pontuação na tela
    player(playerX, playerY)
    show_score(textX, textY)
    
    # Atualiza a tela
    pygame.display.update()
