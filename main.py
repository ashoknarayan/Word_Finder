import pygame
import json

pygame.init()

# Constants
WIDTH, HEIGHT = 900, 300
BG_COLOR = (30, 30, 30)
BOX_COLOR = (200, 200, 200)
BOX_ACTIVE_COLOR = (255, 255, 255)
TEXT_COLOR = (240, 240, 240)
RESULT_BG = (50, 50, 50)
FONT = pygame.font.SysFont('Consolas', 36)
SMALL_FONT = pygame.font.SysFont('Consolas', 24)
INPUT_FONT = pygame.font.SysFont('Consolas', 48)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Pattern Solver")

clock = pygame.time.Clock()

# Load pos_index.json and convert hex bitsets back to int
def load_pos_index(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for length in data:
        lp = data[length]['_letter_pos']
        for letter in lp:
            for i in range(int(length)):
                lp[letter][i] = int(lp[letter][i], 16)
    return data

pos_index = load_pos_index('pos_index.json')

# Input Box class
class InputBox:
    def __init__(self, x, y, w, h, idx):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BOX_COLOR
        self.text = ''
        self.txt_surface = FONT.render(self.text, True, TEXT_COLOR)
        self.active = False
        self.idx = idx

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active if clicked
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = BOX_ACTIVE_COLOR if self.active else BOX_COLOR
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isalpha() and len(self.text) == 0:
                self.text = event.unicode.lower()
            self.txt_surface = FONT.render(self.text, True, TEXT_COLOR)

    def draw(self, screen):
        # Draw box
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Draw text centered
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)
        # Draw index below box
        idx_surf = SMALL_FONT.render(str(self.idx+1), True, TEXT_COLOR)
        idx_rect = idx_surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 2))
        screen.blit(idx_surf, idx_rect)

# Button class
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = FONT.render(text, True, TEXT_COLOR)

    def draw(self, screen):
        pygame.draw.rect(screen, BOX_COLOR, self.rect, border_radius=5)
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Search function using bitset positional index
def search_words(pattern):
    length = len(pattern)
    if length not in pos_index:
        return []

    words = pos_index[length]['_words']
    letter_pos = pos_index[length]['_letter_pos']

    # Start mask with all bits set (all words possible)
    mask = (1 << len(words)) - 1

    for i, ch in enumerate(pattern):
        if ch == '_':
            continue
        if ch < 'a' or ch > 'z':
            # ignore invalid chars
            continue
        if ch not in letter_pos:
            return []
        mask &= letter_pos[ch][i]
        if mask == 0:
            return []

    # Extract matching words from mask
    results = []
    for i in range(len(words)):
        if (mask >> i) & 1:
            results.append(words[i])
    return results

# Screens: Length input, Pattern input, Results display
def length_screen():
    input_box = InputBox(WIDTH//2 - 60, HEIGHT//2 - 30, 120, 60, 0)
    prompt = FONT.render("Enter Word Length (1-30):", True, TEXT_COLOR)

    running = True
    while running:
        screen.fill(BG_COLOR)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            input_box.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_box.text.isdigit():
                    length = int(input_box.text)
                    if 1 <= length <= 30 and str(length) in pos_index:
                        return length

        input_box.draw(screen)
        pygame.display.flip()
        clock.tick(30)

def pattern_screen(length):
    boxes = []
    margin = 10
    box_size = min(60, (WIDTH - (length+1)*margin) // length)
    start_x = (WIDTH - (box_size * length + margin*(length-1))) // 2
    y = HEIGHT//2 - box_size//2 - 20

    for i in range(length):
        box = InputBox(start_x + i*(box_size+margin), y, box_size, box_size, i)
        boxes.append(box)

    prompt = FONT.render("Fill known letters, leave blank as _ (underscore). Press ENTER to search.", True, TEXT_COLOR)

    search_button = Button(WIDTH//2 - 80, HEIGHT - 80, 160, 50, "Search")

    running = True
    while running:
        screen.fill(BG_COLOR)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, y - 70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            for box in boxes:
                box.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pattern = ''.join(box.text if box.text else '_' for box in boxes)
                    return pattern

            if event.type == pygame.MOUSEBUTTONDOWN:
                if search_button.is_clicked(event.pos):
                    pattern = ''.join(box.text if box.text else '_' for box in boxes)
                    return pattern

        for box in boxes:
            box.draw(screen)

        search_button.draw(screen)

        pygame.display.flip()
        clock.tick(30)

def results_screen(words, length):
    running = True
    play_again_button = Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "Play Again")

    # Show max 20 results neatly
    max_show = 20
    display_words = words[:max_show]

    title = FONT.render(f"Found {len(words)} words of length {length}:", True, TEXT_COLOR)

    while running:
        screen.fill(RESULT_BG)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

        y = 80
        line_height = 30
        for w in display_words:
            w_surf = SMALL_FONT.render(w, True, TEXT_COLOR)
            screen.blit(w_surf, (WIDTH//2 - w_surf.get_width()//2, y))
            y += line_height

        if len(words) > max_show:
            more_surf = SMALL_FONT.render(f"... and {len(words)-max_show} more", True, TEXT_COLOR)
            screen.blit(more_surf, (WIDTH//2 - more_surf.get_width()//2, y))
            y += line_height

        play_again_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.is_clicked(event.pos):
                    return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True

        pygame.display.flip()
        clock.tick(30)

def main():
    running = True
    while running:
        length = length_screen()
        if length is None:
            break
        pattern = pattern_screen(length)
        if pattern is None:
            break
        results = search_words(pattern)
        running = results_screen(results, length)

    pygame.quit()

if __name__ == '__main__':
    main()
