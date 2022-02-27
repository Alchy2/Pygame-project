import pygame
from sys import exit
from pygame.math import Vector2
import random

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = pygame.Surface((25,25))
		self.image.fill((255,255,0))
		self.rect = self.image.get_rect(center = (screen_width/2,screen_height/2))
		self.direction_x = 0
		self.direction_y = 0
		self.acceleration = 2
		self.max_speed = 14
		self.x_momentum = 0
		self.y_momentum = 0
		self.friction = 1 / self.acceleration
		self.timer = pygame.time.get_ticks() + 100
		self.health = 3
		self.shoot_sound = pygame.mixer.Sound('audio/laserShoot.wav')
		self.shoot_sound.set_volume(0.15)
	def movement(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_w]:
			self.y_momentum -= self.acceleration
		if keys[pygame.K_s]:
			self.y_momentum += self.acceleration
		if keys[pygame.K_a]:
			self.x_momentum -= self.acceleration
		if keys[pygame.K_d]:
			self.x_momentum += self.acceleration

		if self.rect.right >= screen_width or self.rect.left <= 0:
			self.x_momentum *= -2
		if self.rect.bottom >= screen_height or self.rect.top <= 0:
			self.y_momentum *= -2

		if self.y_momentum != 0:
			self.y_momentum = (abs(self.y_momentum) - self.friction) * (self.y_momentum / abs(self.y_momentum))

		if self.y_momentum > self.max_speed or self.y_momentum < -self.max_speed:
			self.y_momentum = self.max_speed * self.y_momentum / abs(self.y_momentum)

		self.rect.y += self.y_momentum * 0.5

		if self.x_momentum != 0:
			self.x_momentum = (abs(self.x_momentum) - self.friction) * (self.x_momentum / abs(self.x_momentum))

		if self.x_momentum > self.max_speed or self.x_momentum < -self.max_speed:
			self.x_momentum = self.max_speed * self.x_momentum / abs(self.x_momentum)

		self.rect.x += self.x_momentum * 0.5

	def update(self):
		if self.health <= 0:
			self.kill()
		self.movement()
		if pygame.time.get_ticks() > self.timer + 100:
			self.create_bullet()
			self.timer = pygame.time.get_ticks()

	def create_bullet(self):
		self.fired = 0
		self.direction_y = 0
		self.direction_x = 0
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP]:
			self.direction_y = -1
			self.fired = 1
		if keys[pygame.K_DOWN]:
			self.direction_y = 1
			self.fired = 1
		if keys[pygame.K_LEFT]:
			self.direction_x = -1
			self.fired = 1
		if keys[pygame.K_RIGHT]:
			self.direction_x = 1
			self.fired = 1
		if self.fired:
			self.shoot_sound.play()
			bullet = Bullet(self.rect.x,self.rect.y,self.direction_x,self.direction_y)
			bullet_group.add(bullet)
	
class Bullet(pygame.sprite.Sprite):
	def __init__(self,pos_x,pos_y,direction_x,direction_y):
		super().__init__()
		self.image = pygame.Surface((5, 15)).convert_alpha()
		self.image.fill((255,255,0))

		self.direction_x = direction_x
		self.direction_y = direction_y
		self.angle = abs(direction_x)*(360 + direction_x * 180 % 360) + (abs(direction_y)*(360 + direction_y * 90 % 360)) + 90 / (abs(direction_x) + abs(direction_y))+ 90 * (abs(abs(direction_x + direction_y) // 2))
		self.image = pygame.transform.rotozoom(self.image, self.angle, 1)
		self.rect = self.image.get_rect(center = (pos_x + 25/2,pos_y + 25/2))

	def bullet_movement(self):
		self.rect.x += self.direction_x*12
		self.rect.y += self.direction_y*12

	def update(self):
		self.bullet_movement()
		if self.rect.left <= -100:
			self.kill()
		if self.rect.right >= screen_width + 100:
			self.kill()
		if self.rect.top <= -100:
			self.kill()
		if self.rect.bottom >= screen_height + 100:
			self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self,start,player_position):
        super().__init__()
        # setup
        self.image = pygame.Surface((25,25))
        self.image.fill((random.randint(120, 255), random.randint(100, 150), random.randint(100, 150)))
        self.pos = Vector2(start)
        self.rect = self.image.get_rect(center = start)
        # positions
        self.direction = Vector2(player_position) - Vector2(start) 
        self.speed = 3 # changing this changes the direction the sprite moves

    def movement(self):
            self.pos += self.direction.normalize() * self.speed 
            self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self):
        self.direction = Vector2((player.rect.x, player.rect.y)) - Vector2(self.rect.x, self.rect.y) 
        self.movement()

pygame.init()
clock = pygame.time.Clock()
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width,screen_height))
enemy_timer = pygame.time.get_ticks()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)

player = Player()
player_group = pygame.sprite.GroupSingle()
player_group.add(player)
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

paused = 0
game_ended = 0
score = 0

bg_music = pygame.mixer.Sound('audio/music.wav')
bg_music.play(loops = -1)
death_sound = pygame.mixer.Sound('audio/death.wav')
death_sound.set_volume(0.8)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()

		if event.type == pygame.KEYDOWN and event.key == pygame.K_p and paused == 0:
			paused = 1
			bg_music.stop()
			bg_music = pygame.mixer.Sound('audio/music_paused.wav')
			bg_music.play(loops = -1)

		elif  event.type == pygame.KEYDOWN and event.key == pygame.K_p and paused == 1:
			paused = 0
			bg_music.stop()
			bg_music = pygame.mixer.Sound('audio/music.wav')
			bg_music.play(loops = -1)

		if event.type == pygame.MOUSEBUTTONDOWN and game_ended == 1:
			game_ended = 0
			bg_music = pygame.mixer.Sound('audio/music.wav')
			bg_music.play(loops = -1)
			player.rect.x, player.rect.y = screen_width/2,screen_height/2
			player_group.add(player)
			player.health = 3
			score = 0

	screen.fill((30,30,30))
	if pygame.time.get_ticks() > enemy_timer + 700 and game_ended == 0 and paused == 0:
		enemy_position = (random.randrange(screen_width) + random.choice([-0.2, 0.2]) * player.rect.x, random.randrange(screen_height) + random.choice([-0.2, 0.2]) * player.rect.y)
		enemy_group.add(Enemy((enemy_position),(player.rect.x, player.rect.y)))
		enemy_timer = pygame.time.get_ticks()

	bullet_group.draw(screen)
	player_group.draw(screen)
	enemy_group.draw(screen)

	if paused == 0:
		bullet_group.update()
		player_group.update()
		enemy_group.update()

	for bullet in bullet_group:
		enemy_hit = pygame.sprite.spritecollide(bullet, enemy_group, False)
		for enemy in enemy_hit:
			score += 1
			death_sound.play()
			bullet.kill()
			enemy.kill()
	if pygame.sprite.spritecollide(player, enemy_group, True):
			player.health -= 1
			death_sound.play()
		
	if player.health <= 0:
		game_ended = 1
		bg_music.stop()
		for bullet in bullet_group:
			bullet.kill()
		for enemy in enemy_group:
			enemy.kill()
		screen.blit(game_over_surf,game_over_rect)	

	score_surf = test_font.render(f'Score: {score}',False,(230,230,220))
	score_rect = score_surf.get_rect(center = (600,50))

	health_surf = test_font.render(f'Health: {player.health}',False,(200,100,100))
	health_rect = score_surf.get_rect(center = (200,50))

	game_over_surf = test_font.render(f'GAME OVER',False,(220,20,20))
	game_over_rect = score_surf.get_rect(center = (screen_width/2,screen_height/2))
	screen.blit(score_surf,score_rect)
	screen.blit(health_surf,health_rect)

	pygame.display.flip()
	clock.tick(60)