import pygame
import time
import random
import math

pygame.init()
pygame.font.init()
pygame.mixer.init()  # সাউন্ডের জন্য মিক্সার ইনিশিয়ালাইজেশন

# মনিটরের রেজোলিউশন অনুযায়ী স্ক্রিন সাইজ সেট করা
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Fullscreen মোড
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Rocket Space Dodge")

# ব্যাকগ্রাউন্ড ইমেজ লোড করা
try:
    BG = pygame.transform.scale(pygame.image.load("bg.jpg"), (WIDTH, HEIGHT))
except:
    BG = pygame.Surface((WIDTH, HEIGHT))
    BG.fill((10, 10, 30))  # ইমেজ না পেলে ডার্ক ব্লু ব্যাকগ্রাউন্ড

# ব্যাকগ্রাউন্ড মিউজিক এবং সাউন্ড ইফেক্ট লোড
try:
    pygame.mixer.music.load("space_bgm.mp3")  # ব্যাকগ্রাউন্ড মিউজিক ফাইল
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)  # লুপে বারবার বাজবে

    EXPLOSION_SOUND = pygame.mixer.Sound("explosion.wav")
    EXPLOSION_SOUND.set_volume(0.7)
except:
    EXPLOSION_SOUND = None
    print("Sound files not found. Continuing without audio.")

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 60

PLAYER_VEL = 10
ASTEROID_WIDTH = 40
ASTEROID_HEIGHT = 40
ASTEROID_VEL = 7

# ফন্ট সেটআপ
FONT = pygame.font.SysFont("Arial", 30)
EMOJI_FONT = pygame.font.SysFont("segoe ui emoji", 50)
LARGE_FONT = pygame.font.SysFont("Arial", 60)

# রকেটের থ্রাস্টার পার্টিকেল (আগুনের শিখা ইফেক্ট)
particles = []

def create_thruster_particles(x, y):
    """রকেটের নিচ দিয়ে ছোট ছোট আগুনে পার্টিকেল তৈরি করে ডায়নামিক মোশন আনে"""
    particles.append({
        "x": x + PLAYER_WIDTH // 2 + random.randint(-6, 6),
        "y": y + PLAYER_HEIGHT - 10,
        "radius": random.randint(3, 7),
        "color": random.choice([(255, 69, 0), (255, 140, 0), (255, 215, 0)]),  # লাল, কমলা, হলুদ
        "vel_y": random.uniform(2, 5),
        "life": 15
    })

def update_and_draw_particles(surface):
    for p in particles[:]:
        p["y"] += p["vel_y"]
        p["radius"] -= 0.3
        p["life"] -= 1
        if p["life"] <= 0 or p["radius"] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), int(p["radius"]))

def render_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def draw(player, elapsed_time, asteroids, score, tilt_angle=0, is_hit=False):
    WIN.blit(BG, (0, 0))

    # সময় ও স্কোর রেন্ডার
    time_text = FONT.render(f"Time: {round(elapsed_time)}s", True, "white")
    score_text = FONT.render(f"Score: {score}", True, "yellow")
    WIN.blit(time_text, (20, 20))
    WIN.blit(score_text, (20, 60))

    if not is_hit:
        # রকেটের পেছনে থ্রাস্টার এনিমেশন ড্র করা
        create_thruster_particles(player.x, player.y)
        update_and_draw_particles(WIN)

        # রকেট ইমোজি রেন্ডার করা এবং ডানে/বামে মোশনের সাথে সাপেক্ষে Tilt (কাত) করা
        rocket_surf = EMOJI_FONT.render("🚀", True, "white")
        rotated_rocket = pygame.transform.rotate(rocket_surf, tilt_angle)
        new_rect = rotated_rocket.get_rect(center=(player.x + PLAYER_WIDTH // 2, player.y + PLAYER_HEIGHT // 2))
        WIN.blit(rotated_rocket, new_rect.topleft)
    else:
        explosion = EMOJI_FONT.render("💥", True, "white")
        WIN.blit(explosion, (player.x - 5, player.y - 10))

    # উল্কাপিন্ড রেন্ডার
    for ast in asteroids:
        rock = EMOJI_FONT.render("🪨", True, "white")
        WIN.blit(rock, (ast.x - 5, ast.y - 5))

    pygame.display.update()

def game_loop():
    run = True
    player = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 50,
                         PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    ast_add_increment = 1500
    ast_count = 0

    asteroids = []
    score = 0
    hit = False
    tilt_angle = 0  # মোশন ডাইনামিক করার জন্য এঙ্গেল

    while run:
        ast_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        # উল্কাপিন্ড তৈরি
        if ast_count > ast_add_increment:
            for _ in range(random.randint(2, 4)):
                ast_x = random.randint(0, WIDTH - ASTEROID_WIDTH)
                ast = pygame.Rect(ast_x, -ASTEROID_HEIGHT, ASTEROID_WIDTH, ASTEROID_HEIGHT)
                asteroids.append(ast)

            ast_add_increment = max(300, ast_add_increment - 40)
            ast_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        keys = pygame.key.get_pressed()
        
        # স্মুথ মোশন এবং রকেট টিল্ট (Tilt) লজিক
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
            tilt_angle = 15  # বামে গেলে হালকা কাত হবে
        elif keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
            tilt_angle = -15 # ডানে গেলে উল্টো দিকে কাত হবে
        else:
            tilt_angle = 0   # সোজা থাকলে স্বাভাবিক

        for ast in asteroids[:]:
            ast.y += ASTEROID_VEL
            if ast.y > HEIGHT:
                asteroids.remove(ast)
                score += 10
            elif ast.colliderect(player):
                hit = True
                if EXPLOSION_SOUND:
                    EXPLOSION_SOUND.play()
                break

        if hit:
            draw(player, elapsed_time, asteroids, score, tilt_angle, is_hit=True)
            pygame.time.delay(600)

            # Game Over স্ক্রিন
            WIN.blit(BG, (0, 0))
            render_text("GAME OVER", LARGE_FONT, "red", WIN, WIDTH//2 - 160, HEIGHT//2 - 100)
            render_text(f"Final Score: {score}", FONT, "white", WIN, WIDTH//2 - 90, HEIGHT//2 - 20)
            render_text("Press R to Restart or ESC to Quit", FONT, "yellow", WIN, WIDTH//2 - 220, HEIGHT//2 + 40)
            pygame.display.update()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            return True
                        if event.key == pygame.K_ESCAPE:
                            return False

        draw(player, elapsed_time, asteroids, score, tilt_angle)

    return False

def main():
    restart = True
    while restart:
        particles.clear()
        restart = game_loop()
    pygame.quit()

if __name__ == "__main__":
    main()