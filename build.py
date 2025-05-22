import pygame
import sys
import json

pygame.init()

WIDTH, HEIGHT = 1300, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Finder")

FONT = pygame.font.SysFont(None, 50)
SMALL_FONT = pygame.font.SysFont(None, 32)

clock = pygame.time.Clock()

# Load positional index JSON once
with open('pos_index.json', 'r', encoding='utf-8') as f:
    pos_index = json.load(f)

def draw_text(surface, text, pos, font=FONT, color=(255,255,255)):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def get_word_length():
    input_str = ''
    while True:
        screen.fill((30, 30, 30))
        draw_text(screen, "Enter word length (1-20):", (50, 50), SMALL_FONT)
        draw_text(screen, input_str, (50, 100))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_str.isdigit():
                        length = int(input_str)
                        if 1 <= length <= 20 and str(length) in pos_index:
                            return length
                    input_str = ''  # invalid input reset
                elif event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                else:
                    if event.unicode.isdigit():
                        input_str += event.unicode
        clock.tick(30)

def input_letters(length):
    letters = [''] * length
    selected = 0  # which box is active

    box_size = 50
    spacing = 10
    total_width = length * box_size + (length - 1) * spacing
    start_x = (WIDTH - total_width) // 2
    y = HEIGHT // 3

    running = True
    while running:
        screen.fill((30,30,30))
        draw_text(screen, "Type letters you know (use BACKSPACE to clear)", (50, 30), SMALL_FONT)

        # Draw boxes
        for i in range(length):
            rect = pygame.Rect(start_x + i*(box_size + spacing), y, box_size, box_size)
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            pygame.draw.rect(screen, color, rect, 3)

            # Draw letter if present
            if letters[i]:
                letter_surf = FONT.render(letters[i].upper(), True, (255,255,255))
                letter_rect = letter_surf.get_rect(center=rect.center)
                screen.blit(letter_surf, letter_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    letters[selected] = ''
                elif event.key == pygame.K_LEFT:
                    selected = max(0, selected - 1)
                elif event.key == pygame.K_RIGHT:
                    selected = min(length - 1, selected + 1)
                else:
                    ch = event.unicode.lower()
                    if ch.isalpha() and len(ch) == 1:
                        letters[selected] = ch
                        if selected < length - 1:
                            selected += 1
        clock.tick(30)

    return letters

def find_matching_words(letters):
    length = len(letters)
    length_str = str(length)
    if length_str not in pos_index:
        return []

    words = pos_index[length_str]['_words']
    letter_pos = pos_index[length_str]['_letter_pos']

    n = len(words)
    full_mask = (1 << n) - 1
    mask = full_mask

    for pos, ch in enumerate(letters):
        if ch == '' or ch == '_':
            continue
        if ch not in letter_pos:
            return []
        hex_mask = letter_pos[ch][pos]
        bitset = int(hex_mask, 16)
        mask &= bitset
        if mask == 0:
            return []

    result = []
    for i in range(n):
        if mask & (1 << i):
            result.append(words[i])

    return result

def results_screen(words):
    scroll_y = 0
    max_display = (HEIGHT - 120) // 30

    button_rect = pygame.Rect(WIDTH - 170, HEIGHT - 70, 150, 50)

    running = True
    while running:
        screen.fill((30,30,30))
        draw_text(screen, f"Found {len(words)} word(s):", (20, 20), SMALL_FONT)

        pygame.draw.rect(screen, (70, 130, 180), button_rect)
        draw_text(screen, "Play Again", (button_rect.x + 20, button_rect.y + 10), SMALL_FONT)

        start_idx = max(0, scroll_y // 30)
        display_words = words[start_idx:start_idx + max_display]

        y = 60
        for w in display_words:
            draw_text(screen, w, (50, y), SMALL_FONT)
            y += 30

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    running = False
                # Scroll wheel support
                if event.button == 4:  # scroll up
                    scroll_y = max(scroll_y - 30, 0)
                elif event.button == 5:  # scroll down
                    scroll_y += 30

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        clock.tick(30)

def main():
    while True:
        length = get_word_length()
        letters = input_letters(length)
        matches = find_matching_words(letters)
        results_screen(matches)

if __name__ == "__main__":
    main()
