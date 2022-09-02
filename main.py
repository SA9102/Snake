import pygame
import sys
from random import randint

# Head of the snake; the part that the character controls.
class SnakeHead(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill('#4e634a')
        self.rect = self.image.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
        self.direction = pygame.math.Vector2()
        # When the game starts, the initial direction will be 'right'.
        self.direction.x = 1
        self.direction.y = 0
        # A timer that determines how long to wait until an edible is rendered to the screen.
        self.edible_timer = randint(100, 170)
        # Only one edible can be rendered at a time. This is set to True when an edible is visible
        # on the screen.
        self.edible_rendered = False

    # Gets keyboard input. Control player using arrow keys or WASD keys.
    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.direction.y = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.direction.y = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.x = 0
            self.direction.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.x = 0
            self.direction.y = 1

    # Checks if the snake head is touching the game boundary. If so, then the game is over.
    def check_at_boundary(self):
        global game_active
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH or self.rect.top <= 40 or self.rect.bottom >= SCREEN_HEIGHT:
            game_active = False
            lose.play()
            self.kill()

    def render_edible(self):
        # If the 'edible timer' is zero, then render an edible to a random position on the screen within the game area.
        if self.edible_timer <= 0 and self.edible_rendered == False:
            self.edible_rendered = True
            edible.add(Edible(10, randint(10, SCREEN_WIDTH - 10), randint(50, SCREEN_HEIGHT - 10)))

    def update(self):
        global score
        global high_score
        self.input()
        self.check_at_boundary()
        self.rect.x += self.direction.x * 3
        self.rect.y += self.direction.y * 3
        # Add a snake body in every frame.
        snake_body.add(SnakeBody(20, self.rect.centerx, self.rect.centery))
        self.edible_timer -= 1
        self.render_edible()

        # If the player (snake head) is touching an edible, then add one to the points, and set a timer for the edible again.
        if pygame.sprite.spritecollide(self, edible, True):
            self.edible_rendered = False
            self.edible_timer = randint(100, 170)
            score += 1
            if score > high_score:
                high_score = score
            pickup.play()

# The snake's trailing body.
class SnakeBody(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        global score
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill('#4e634a')
        self.rect = self.image.get_rect(center = (x, y))
        self.timer = 15 + (score * 15)

        # An instance of SnakeBody will be rendered on top of the snake head in every frame.
        # This means that the snake head will immediately be touching its body, and so the player would lose instantly.
        # To circumvent this, a new instance of SnakeBody will have this timer, during which the player will not lose if it is touched.
        # Only when this timer reaches zero will the player lose if it touches this SnakeBody instance.
        self.invincibility_timer = 15

    def update(self):
        global game_active
        self.timer -= 1
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
        if self.timer <= 0:
            self.kill()

        # If the snake head is touching this body, and the invincibility timer for this body is zero. The player will lose the game.
        if pygame.sprite.spritecollide(self, snake_head, False) and self.invincibility_timer <= 0:
            game_active = False
            lose.play()

# This is what the snake consumes to grow larger
class Edible(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill('#7a4141')
        self.rect = self.image.get_rect(center = (x, y))

    def update(self):
        # This checks if an edible is rendered on top of the snake's body. If so, then it will immediately be deleted
        # without incrementing the points, and a new one will be rendered somewhere else.# If it is being touch
        if pygame.sprite.spritecollide(self, snake_body, False):
            self.kill()
            snake_head.sprite.edible_rendered = False
            snake_head.sprite.edible_timer = randint(100, 170)

SCREEN_WIDTH = 350
SCREEN_HEIGHT = 390

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

game_active = False
# This is only True when the player is at the screen when they launch the program.
# After the user starts their first game, this will always remain False.
game_begin = True
score = 0
high_score = 0
message_visible = True

snake_head = pygame.sprite.GroupSingle()
snake_body = pygame.sprite.Group()
edible = pygame.sprite.GroupSingle()

large_font = pygame.font.Font('font.ttf', 100)
big_font = pygame.font.Font('font.ttf', 80)
medium_font = pygame.font.Font('font.ttf', 40)
small_font = pygame.font.Font('font.ttf', 30)

pickup = pygame.mixer.Sound('sound/pickup.wav')
lose = pygame.mixer.Sound('sound/lose.wav')
start = pygame.mixer.Sound('sound/start.wav')

# Used to create a blinking effect for the message prompting the user to start the game.
MESSAGE_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(MESSAGE_TIMER, 800)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        

        if not game_active:
            if event.type == MESSAGE_TIMER:
                message_visible = not message_visible
            
            # If the game is over, then remove the edible and all instances of SnakeBody, so that these
            # will not be immediately visible when the user starts the next game.
            if snake_body:
                for object in snake_body:
                    object.kill()
            if edible:
                edible.sprite.kill()

            # Start the game if the user presses the space bar.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                snake_head.add(SnakeHead(20))
                score = 0
                game_active = True
                game_begin = False
                start.play()

    screen.fill('#171a1c')

    if game_active:

        # Drawing and updating the sprites.
        snake_head.draw(screen)
        snake_head.update()

        snake_body.draw(screen)
        snake_body.update()

        edible.draw(screen)
        edible.update()

        pygame.draw.rect(screen, '#474747', pygame.Rect(0, 0, SCREEN_WIDTH, 40))

        # Display current score and high score
        score_surf = small_font.render(f'Score: {score}', False, '#ffffff')
        score_rect = score_surf.get_rect(midleft = (7, 20))
        screen.blit(score_surf, score_rect)

        high_score_surf = small_font.render(f'High Score: {high_score}', False, '#ffffff')
        high_score_rect = high_score_surf.get_rect(midleft = (110, 20))
        screen.blit(high_score_surf, high_score_rect)
    else:
        if game_begin:
            # Title
            title_surf = large_font.render('Snake', False, '#ffffff')
            title_rect = title_surf.get_rect(center = (SCREEN_WIDTH / 2, 125))
            screen.blit(title_surf, title_rect)

        else:
            # Score and high score when game is over.
            score_surf = big_font.render(f'{score}', False, '#ffffff')
            score_rect = score_surf.get_rect(center = (SCREEN_WIDTH / 2, 125))
            screen.blit(score_surf, score_rect)

            high_score_surf = big_font.render(f'{high_score}', False, '#ffffff')
            high_score_rect = high_score_surf.get_rect(center = (SCREEN_WIDTH / 2, 180))
            screen.blit(high_score_surf, high_score_rect)

        if message_visible:
            # Message prompting user to start the game.
            if game_begin:
                message_surf = medium_font.render('Press SPACE to start', False, '#ffffff')
            else:
                message_surf = medium_font.render('Press SPACE to restart', False, '#ffffff')
            message_rect = message_surf.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 125))
            screen.blit(message_surf, message_rect)


    pygame.display.update()
    clock.tick(60)