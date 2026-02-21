import pygame
import asyncio
import datetime
from pygame.locals import *

pygame.init()

# Full canvas for maximum space (adapts to browser window)
screen = pygame.display.set_mode((0, 0))

clock = pygame.time.Clock()

# ────────────────────────────────────────────────
# Margin settings – increase margin_top for more distance from top of screen
margin_side   = 40          # left + right symmetric margin
margin_top    = 180         # ← higher = more space above the box (e.g. 200–300)
margin_bottom = 60          # bottom margin

# Aesthetic colors
BG_DARK = (8, 5, 18)              # deep cosmic background
BOX_BORDER = (90, 60, 140)        # muted violet thick frame
PURPLE_CORE = (160, 70, 220)      # rich radiant purple
PURPLE_GLOW = (210, 130, 255)     # bright glowing center
BORDER_LIGHT = (240, 200, 255)    # soft lavender-white
INNER_HIGHLIGHT = (255, 220, 255, 140)  # semi-transparent shine

# ────────────────────────────────────────────────
# Title "Hit/Miss" – aesthetic & matching tone
try:
    font = pygame.font.SysFont('segoe ui', 56, bold=True)  # clean modern font
except:
    try:
        font = pygame.font.SysFont('helvetica', 56, bold=True)
    except:
        font = pygame.font.Font(None, 56)  # fallback sans-serif

title_text = "Hit/Miss"
title_surf = font.render(title_text, True, (220, 180, 255))      # soft lavender-white

# Golden ratio conjugate → irrational, never hits corners mathematically
golden = (5 ** 0.5 - 1) / 2

async def main():
    # Initial screen size
    WIDTH, HEIGHT = screen.get_size()

    # Initial calculation before forcing square
    temp_width  = WIDTH - 2 * margin_side
    temp_height = HEIGHT - margin_top - margin_bottom

    # Force the play area to be a perfect square
    side = min(temp_width, temp_height)

    # Position the square box (horizontally centered, extra space at top)
    play_left   = (WIDTH - side) // 2
    play_top    = margin_top
    play_width  = side
    play_height = side

    # Inner bouncing square – large and proportional
    size = side // 5   # feels big (change to //4 for even larger)

    # Start exactly centered inside the square box
    x = play_left + (play_width - size) // 2
    y = play_top + (play_height - size) // 2

    # Calm speed, scaled to box size
    base_speed = side / 500.0
    speed = max(1.4, base_speed)
    vx = speed
    vy = speed * golden

    # Title rects (updated on resize)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 50))        # near top
    shadow_rect = title_rect.move(4, 4)

    # Faint underline/glow line
    underline_y = title_rect.bottom + 12
    underline_start = WIDTH // 2 - 140
    underline_end   = WIDTH // 2 + 140

    # Midnight trigger state
    triggered = False
    last_trigger_date = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == VIDEORESIZE:
                # Handle browser resize/orientation change
                WIDTH, HEIGHT = event.size
                screen = pygame.display.set_mode((WIDTH, HEIGHT))

                # Recalc play area
                temp_width  = WIDTH - 2 * margin_side
                temp_height = HEIGHT - margin_top - margin_bottom
                new_side = min(temp_width, temp_height)

                # Scale speed to keep relative speed constant
                scale_factor = new_side / side
                vx *= scale_factor
                vy *= scale_factor

                # Update dimensions
                side = new_side
                play_left   = (WIDTH - side) // 2
                play_top    = margin_top
                play_width  = side
                play_height = side

                # Update square size
                size = side // 5

                # Clamp position to new bounds
                x = max(play_left, min(play_left + play_width - size, x))
                y = max(play_top, min(play_top + play_height - size, y))

                # Update title positions
                title_rect = title_surf.get_rect(center=(WIDTH // 2, 50))
                shadow_rect = title_rect.move(4, 4)
                underline_y = title_rect.bottom + 12
                underline_start = WIDTH // 2 - 140
                underline_end   = WIDTH // 2 + 140

            if event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_AC_BACK):
                    running = False

        # Check for midnight (3-second window)
        now = datetime.datetime.now()
        current_date = now.date()
        is_midnight = (now.hour == 0 and now.minute == 0 and now.second < 3)

        if is_midnight and last_trigger_date != current_date and not triggered:
            # Force "hit" – snap to top-left corner
            x = play_left
            y = play_top
            vx = 0
            vy = 0
            triggered = True
            last_trigger_date = current_date

        # Normal motion if not triggered
        if not triggered:
            x += vx
            y += vy

            # Bounce inside square box
            if x <= play_left or x + size >= play_left + play_width:
                vx = -vx
                x = max(play_left, min(play_left + play_width - size, x))
            if y <= play_top or y + size >= play_top + play_height:
                vy = -vy
                y = max(play_top, min(play_top + play_height - size, y))

        # Draw
        screen.fill(BG_DARK)

        # Title – always visible (subtle, atmospheric)
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_surf, title_rect)
        pygame.draw.line(screen, (180, 120, 220, 80),
                         (underline_start, underline_y),
                         (underline_end, underline_y), 4)

        if triggered:
            # Full white screen – everything disappears
            screen.fill((255, 255, 255))
        else:
            # Normal: box border + radiant purple square
            pygame.draw.rect(screen, BOX_BORDER, (play_left, play_top, play_width, play_height), 10)

            # Core fill
            pygame.draw.rect(screen, PURPLE_CORE, (x, y, size, size))

            # Bright center glow
            glow_size = int(size * 0.65)
            glow_x = x + (size - glow_size) // 2
            glow_y = y + (size - glow_size) // 2
            pygame.draw.rect(screen, PURPLE_GLOW, (glow_x, glow_y, glow_size, glow_size))

            # Outer glowing border
            pygame.draw.rect(screen, BORDER_LIGHT, (x, y, size, size), 6)

            # Inner transparent shine
            inner_size = size - 20
            inner_x = x + 10
            inner_y = y + 10
            if inner_size > 0:
                surf = pygame.Surface((inner_size, inner_size), pygame.SRCALPHA)
                surf.fill(INNER_HIGHLIGHT)
                screen.blit(surf, (inner_x, inner_y))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # REQUIRED for pygbag/browser!

    pygame.quit()

asyncio.run(main())