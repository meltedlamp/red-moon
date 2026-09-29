"""Start, level select, game over and victory screens with clickable buttons."""

import math
import random

import pygame

from .settings import (
    ACCENT_OVER, ACCENT_START, ACCENT_WIN, BUTTON_H, BUTTON_W, CARD_BG, EXIT_BTN, EYE_GLOW, HEIGHT,
    LEVELS_BTN, MENU_DIM, MENU_PANEL, PLAY_BTN, PLAY_BTN_HOVER, PLAY_BTN_TEXT, START_LIVES,
    STATE_SELECT, THEME_ACCENT, TITLE, WHITE, WIDTH,
)


class MenuMixin:
    """Game methods for the menu screens and their buttons."""

    def menu_buttons(self):
        if self.state == STATE_SELECT:
            return self.select_buttons()
        buttons = {}
        for i, name in enumerate(("play", "levels", "exit")):
            rect = pygame.Rect(0, 0, BUTTON_W, BUTTON_H)
            rect.center = (WIDTH // 2 + (i - 1) * (BUTTON_W + 20), 452)
            buttons[name] = rect
        return buttons

    def select_buttons(self):
        buttons = {}
        cols, card_w, card_h, gap = 4, 136, 118, 14
        left = (WIDTH - (cols * card_w + (cols - 1) * gap)) // 2
        for i, level in enumerate(self.levels):
            row, col = divmod(i, cols)
            span = 2 if level.get("boss") else 1
            width = span * card_w + (span - 1) * gap
            buttons[f"level{i}"] = pygame.Rect(left + col * (card_w + gap), 200 + row * (card_h + 14), width, card_h)
        back = pygame.Rect(0, 0, 150, 48)
        back.center = (WIDTH // 2, 494)
        buttons["back"] = back
        return buttons

    def button_at(self, pos):
        for name, rect in self.menu_buttons().items():
            if rect.collidepoint(pos):
                return name
        return None

    def draw_glow(self, rect, color, radius, layers, strength):
        area = rect.inflate(layers * 4, layers * 4)
        surf = pygame.Surface(area.size, pygame.SRCALPHA)
        for i in range(layers):
            ring = pygame.Rect(0, 0, rect.w + i * 4, rect.h + i * 4)
            ring.center = (area.w // 2, area.h // 2)
            alpha = int(strength * (1 - i / layers) ** 2)
            pygame.draw.rect(surf, (*color, alpha), ring, 2, border_radius=radius + i * 2)
        self.screen.blit(surf, area)

    def draw_button(self, rect, label, kind, hovered):
        r = rect.inflate(8, 6) if hovered else rect
        if kind == "play":
            self.draw_glow(r, PLAY_BTN, 14, 8, 150 if hovered else 90)
            pygame.draw.rect(self.screen, PLAY_BTN_HOVER if hovered else PLAY_BTN, r, border_radius=14)
            text_color = PLAY_BTN_TEXT
        elif kind == "levels":
            if hovered:
                self.draw_glow(r, LEVELS_BTN, 14, 8, 130)
                pygame.draw.rect(self.screen, LEVELS_BTN, r, border_radius=14)
                text_color = PLAY_BTN_TEXT
            else:
                pygame.draw.rect(self.screen, MENU_PANEL, r, border_radius=14)
                pygame.draw.rect(self.screen, LEVELS_BTN, r, 3, border_radius=14)
                text_color = LEVELS_BTN
        else:
            if hovered:
                pygame.draw.rect(self.screen, EXIT_BTN, r, border_radius=14)
                text_color = WHITE
            else:
                pygame.draw.rect(self.screen, MENU_PANEL, r, border_radius=14)
                pygame.draw.rect(self.screen, EXIT_BTN, r, 3, border_radius=14)
                text_color = EXIT_BTN
        s = self.button_font.render(label, True, text_color)
        self.screen.blit(s, s.get_rect(center=r.center))

    def draw_menu(self, title, lines, accent, play_label, moon_mood):
        self.draw_panel(title, accent)

        t = pygame.time.get_ticks() / 1000
        mx, my, R = 694, 96, 50
        if moon_mood == "talk":
            mx += random.randint(-2, 2)
            my += random.randint(-2, 2)
            laugh = self.tiny.render("HA! HA! HA!", True, EYE_GLOW)
            self.screen.blit(laugh, laugh.get_rect(center=(mx + random.randint(-2, 2), my + R + 20)))
        else:
            my += round(math.sin(t * 1.2) * 3)
        if moon_mood != "dead":
            self.moon_glow.set_alpha(150 + int(105 * (0.5 + 0.5 * math.sin(t * 3))))
            self.screen.blit(self.moon_glow, self.moon_glow.get_rect(center=(mx, my)))
        look = max(-1.0, min(1.0, (pygame.mouse.get_pos()[0] - mx) / 250))
        self.draw_moon_face((mx, my), R, t, moon_mood, look)

        y = 218
        for i, line in enumerate(lines):
            color = accent if i == 0 else MENU_DIM
            s = self.font.render(line, True, color)
            self.screen.blit(s, s.get_rect(center=(WIDTH // 2, y)))
            y += 32

        hovered = self.button_at(pygame.mouse.get_pos())
        buttons = self.menu_buttons()
        self.draw_button(buttons["play"], play_label, "play", hovered == "play")
        self.draw_button(buttons["levels"], "Levels", "levels", hovered == "levels")
        self.draw_button(buttons["exit"], "Exit", "exit", hovered == "exit")

        hint = self.small.render("Enter to play  •  M to mute  •  Esc to quit", True, MENU_DIM)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 514)))

    def draw_select(self):
        self.draw_panel("Choose a level", ACCENT_START)
        hovered = self.button_at(pygame.mouse.get_pos())
        t = pygame.time.get_ticks() / 1000
        for i, level in enumerate(self.levels):
            name = f"level{i}"
            card = self.select_buttons()[name]
            accent = THEME_ACCENT[level["theme"]]
            is_hover = hovered == name
            if is_hover:
                card = card.inflate(8, 8)
                self.draw_glow(card, accent, 14, 8, 140)
            pygame.draw.rect(self.screen, CARD_BG, card, border_radius=14)
            pygame.draw.rect(self.screen, accent, card, 3 if is_hover else 2, border_radius=14)

            if level.get("boss"):
                text_x = card.x + (card.w - 96) // 2
                num = self.button_font.render("Final Boss", True, accent)
                self.screen.blit(num, num.get_rect(midtop=(text_x, card.y + 22)))
                label = self.small.render(level["name"], True, WHITE if is_hover else MENU_DIM)
                self.screen.blit(label, label.get_rect(midtop=(text_x, card.y + 58)))
                mood = "talk" if is_hover else "idle"
                self.draw_moon_face((card.right - 54, card.centery), 38, t, mood, -0.6)
                continue

            num = self.button_font.render(f"Level {i + 1}", True, accent)
            self.screen.blit(num, num.get_rect(midtop=(card.centerx, card.y + 12)))
            label = self.tiny.render(level["name"], True, WHITE if is_hover else MENU_DIM)
            self.screen.blit(label, label.get_rect(midtop=(card.centerx, card.y + 48)))
            swatch = pygame.Rect(card.x + 12, card.bottom - 34, card.w - 24, 22)
            self.screen.set_clip(card.inflate(-6, -6))
            self.draw_floor(swatch, 1000 + i * 37, t, level["theme"])
            self.screen.set_clip(None)

        self.draw_button(self.select_buttons()["back"], "Back", "levels", hovered == "back")

    def draw_panel(self, title, accent):
        self.draw_background()

        panel = pygame.Rect(80, 60, WIDTH - 160, HEIGHT - 120)
        self.draw_glow(panel, accent, 22, 12, 120)

        body = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(body, (*MENU_PANEL, 235), body.get_rect(), border_radius=22)
        self.screen.blit(body, panel)
        pygame.draw.rect(self.screen, accent, panel, 2, border_radius=22)

        t = pygame.time.get_ticks() / 1000
        title_y = 128 + int(4 * math.sin(t * 2))
        halo = self.title_font.render(title, True, accent)
        halo.set_alpha(80)
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            self.screen.blit(halo, halo.get_rect(center=(WIDTH // 2 + dx, title_y + dy)))
        title_s = self.title_font.render(title, True, WHITE)
        self.screen.blit(title_s, title_s.get_rect(center=(WIDTH // 2, title_y)))

        pygame.draw.line(self.screen, accent, (WIDTH // 2 - 120, 178), (WIDTH // 2 + 120, 178), 2)

    def draw_start(self):
        self.draw_menu(
            TITLE,
            [
                "Beware the moon. It is watching.",
                "Move with Left / Right  (or A / D)",
                "Jump with Space  (or Up / W)",
                "Press jump again mid-air to double jump",
                "Collect glowing coins  •  Stomp red walkers",
                f"Clear 6 hills, then defeat the Moon  •  {START_LIVES} lives",
            ],
            ACCENT_START,
            "Play",
            "idle",
        )

    def draw_win(self):
        self.draw_menu(
            "Victory!",
            [
                f"Final score: {self.score}",
                "The Moon is defeated. Morning comes.",
                "Think you can beat that score?",
            ],
            ACCENT_WIN,
            "Play again",
            "dead",
        )

    def draw_over(self):
        self.draw_menu(
            "Game over",
            [
                f"Score this run: {self.score}",
                "You lost to the red junkies!",
                "Try again before they invade.",
            ],
            ACCENT_OVER,
            "Try again",
            "talk",
        )
