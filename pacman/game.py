import math
from pathlib import Path

import pygame
from .display import Display, YELLOW, WHITE
from .highscores import HighScoreStore
from .maze import load_maze, MazeError
from .player import Player
from .level import Level


STATE_MENU = "menu"
STATE_GAME = "game"
STATE_HIGHSCORES = "highscores"
STATE_INSTRUCTIONS = "instructions"
STATE_PAUSE = "pause"
STATE_NAME = "name"
MENU_ITEMS = ("Start Game", "View Highscores", "Instructions", "Exit")
PAUSE_ITEMS = ("Resume", "Return to Main Menu")


class Game:
    def __init__(self, config, warnings):
        pygame.init()
        pygame.key.set_repeat(400, 50)
        pygame.display.set_caption("Pac-Man")

        self.config = config
        self.warnings = warnings
        self.audio_enabled = True
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except pygame.error as exc:
            self.audio_enabled = False
            self.warnings.insert(0, f"Audio disabled: {exc}")
        self.music_track = None
        self.move_sound = None
        self.select_sound = None
        if self.audio_enabled:
            audio_dir = Path(__file__).resolve().parent.parent
            self.move_sound = pygame.mixer.Sound(str(audio_dir / "menu_move.wav"))
            self.select_sound = pygame.mixer.Sound(str(audio_dir / "menu_select.wav"))
            self.move_sound.set_volume(0.7)
            self.select_sound.set_volume(0.7)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU
        self.level_index = 0
        self.score = 0
        self.lives = config["lives"]
        self.level_time_remaining = config["level_max_time"]
        self.menu_selection = 0
        self.pause_selection = 0
        self.name = ""
        self.result = ""
        self.error_message = ""
        self.cheat_invincible = False
        self.highscores = HighScoreStore(config["highscore_filename"])

        level = config["levels"][0]
        self.tile_size = min(80, max(24, 1000 // level["width"], 700 // level["height"]))
        self.display = Display(
            level["width"] * self.tile_size,
            level["height"] * self.tile_size,
            self.tile_size,
        )
        self.maze = None
        self.level = None
        self.player = None

    def start_game(self):
        self.level_index = 0
        self.score = 0
        self.lives = self.config["lives"]
        self.cheat_invincible = False
        if self.load_level():
            self.state = STATE_GAME

    def load_level(self) -> bool:
        level = self.config["levels"][self.level_index]
        try:
            maze, entry, _ = load_maze(
                level["width"], level["height"], level["seed"]
            )
            self.level = Level(maze)
            self.player = Player(*self.level.player_spawn,
                                 self.tile_size / 0.30)
        except MazeError as exc:
            self.error_message = str(exc)
            self.state = STATE_MENU
            return False
        self.maze = maze
        self.tile_size = min(
            80,
            max(
                24,
                1000 // level["width"],
                700 // level["height"],
            ),
        )
        self.display.set_logical_size(
            level["width"] * self.tile_size,
            level["height"] * self.tile_size,
            self.tile_size,
        )
        self.error_message = ""
        self.level_time_remaining = self.config["level_max_time"]
        return True

    def end_game(self, result):
        self.result = result
        self.name = ""
        self.state = STATE_NAME

    def play_ui_sound(self, sound):
        if sound is not None:
            sound.play()

    def update_music(self):
        if not self.audio_enabled:
            return
        track = "ingame_music.ogg" if self.state == STATE_GAME else "background_music.ogg"
        if track == self.music_track:
            return
        path = Path(__file__).resolve().parent.parent / track
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0.45)
        pygame.mixer.music.play(-1)
        self.music_track = track

    def handle_menu(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_selection = (self.menu_selection - 1) % len(MENU_ITEMS)
            self.play_ui_sound(self.move_sound)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_selection = (self.menu_selection + 1) % len(MENU_ITEMS)
            self.play_ui_sound(self.move_sound)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.play_ui_sound(self.select_sound)
            if self.menu_selection == 0:
                self.start_game()
            elif self.menu_selection == 1:
                self.state = STATE_HIGHSCORES
            elif self.menu_selection == 2:
                self.state = STATE_INSTRUCTIONS
            else:
                self.running = False
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_game(self, event):
        if event.type == pygame.KEYDOWN:
            self.player.set_direction(event.key)
            if event.key == pygame.K_ESCAPE:
                self.pause_selection = 0
                self.state = STATE_PAUSE
            if self.config["cheat_mode"]:
                if event.key == pygame.K_F1:
                    self.cheat_invincible = not self.cheat_invincible
                elif event.key == pygame.K_F2:
                    self.end_game("WIN")
                elif event.key == pygame.K_F3:
                    self.end_game("LOSE")

    def handle_pause(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.state = STATE_GAME
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.pause_selection = (self.pause_selection - 1) % len(PAUSE_ITEMS)
            self.play_ui_sound(self.move_sound)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pause_selection = (self.pause_selection + 1) % len(PAUSE_ITEMS)
            self.play_ui_sound(self.move_sound)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.play_ui_sound(self.select_sound)
            if self.pause_selection == 0:
                self.state = STATE_GAME
            else:
                self.state = STATE_MENU
                self.menu_selection = 0

    def handle_name(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RETURN:
            self.play_ui_sound(self.select_sound)
            if self.name.strip():
                self.highscores.add(self.name.strip(), self.score)
            self.state = STATE_MENU
        elif event.key == pygame.K_BACKSPACE:
            self.name = self.name[:-1]
        elif (event.unicode.isascii() and event.unicode.isalnum()) or event.unicode == " ":
            if len(self.name) < 10:
                self.name += event.unicode

    def draw_menu(self):
        self.display.clear()
        self.display.draw_text("PAC-MAN", 110, self.display.large_font, YELLOW)
        for index, item in enumerate(MENU_ITEMS):
            selected = index == self.menu_selection
            label = f"> {item} <" if selected else item
            self.display.draw_text(
                label,
                230 + index * 52,
                self.display.font,
                YELLOW if selected else WHITE,
            )
        self.display.draw_text(
            "UP/DOWN: Select   ENTER: Confirm   ESC: Exit",
            460,
            self.display.small_font,
        )
        if self.error_message:
            self.display.draw_text(self.error_message, self.display.height - 70,
                                   self.display.small_font)
        for warning in self.warnings[:2]:
            self.display.draw_text(warning, self.display.height - 40,
                                   self.display.small_font)

    def draw_highscores(self):
        self.display.clear()
        self.display.draw_text("HIGHSCORES", 100, self.display.large_font, YELLOW)
        scores = self.highscores.load()
        if not scores:
            self.display.draw_text("No scores yet", 190)
        else:
            for index, item in enumerate(scores, start=1):
                self.display.draw_text(
                    f"{index:2}. {item['name']:<10} {item['score']}",
                    150 + index * 34,
                    self.display.small_font,
                )
        self.display.draw_text("Press ESC to return", self.display.height - 50,
                               self.display.small_font)

    def draw_instructions(self):
        self.display.clear()
        self.display.draw_text("INSTRUCTIONS", 100, self.display.large_font, YELLOW)
        lines = (
            "Arrow keys: move Pac-Man",
            "Collect gums and super gums",
            "Avoid the ghosts and clear the maze",
            "Press ESC during a game to pause",
        )
        for index, line in enumerate(lines):
            self.display.draw_text(line, 210 + index * 48, self.display.small_font)
        self.display.draw_text("Press ESC to return", self.display.height - 50,
                               self.display.small_font)

    def draw_pause(self):
        self.display.clear()
        self.display.draw_text("PAUSED", 150, self.display.large_font, YELLOW)
        for index, item in enumerate(PAUSE_ITEMS):
            selected = index == self.pause_selection
            label = f"> {item} <" if selected else item
            self.display.draw_text(
                label,
                270 + index * 60,
                self.display.font,
                YELLOW if selected else WHITE,
            )
        self.display.draw_text("ESC resumes", self.display.height - 50,
                               self.display.small_font)

    def draw_game(self):
        self.display.clear()
        self.display.draw_maze(self.maze)
        self.display.draw_ghosts(self.level.ghost_spawn)
        self.display.draw_pacgums(self.level.pacgums)
        self.display.draw_super_pacgums(self.level.super_pacgums)
        self.display.draw_player(self.player)
        self.display.draw_hud(
            f"Score: {self.score}  Lives: {self.lives}  "
            f"Level: {self.level_index + 1}  "
            f"Time: {math.ceil(self.level_time_remaining)}"
        )

    def draw_name(self):
        self.display.clear()
        self.display.draw_text(
            "VICTORY!" if self.result == "WIN" else "GAME OVER",
            180,
            self.display.large_font,
            YELLOW,
        )
        if self.result == "WIN":
            self.display.draw_text("Congratulations!", 240)
        self.display.draw_text(f"Score: {self.score}", 260)
        self.display.draw_text("Enter name (letters, numbers, spaces)", 320,
                               self.display.small_font)
        self.display.draw_text(self.name + "_", 390)
        self.display.draw_text("Press ENTER to save", 450,
                               self.display.small_font)

    def run(self):
        while self.running:
            frame_time = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.display.resize(event.w, event.h)
                elif self.state == STATE_MENU:
                    self.handle_menu(event)
                elif self.state == STATE_GAME:
                    self.handle_game(event)
                elif self.state == STATE_PAUSE:
                    self.handle_pause(event)
                elif self.state in (STATE_HIGHSCORES, STATE_INSTRUCTIONS):
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = STATE_MENU
                elif self.state == STATE_NAME:
                    self.handle_name(event)

            self.update_music()

            if self.state == STATE_GAME:
                self.level_time_remaining = max(
                    0, self.level_time_remaining - frame_time / 1000
                )
                if self.level_time_remaining == 0 or self.lives <= 0:
                    self.end_game("LOSE")
                else:
                    self.player.update(
                        frame_time, self.maze,
                        len(self.maze[0]), len(self.maze),
                        self.tile_size,
                    )

            if self.state == STATE_GAME:
                self.draw_game()
            elif self.state == STATE_PAUSE:
                self.draw_pause()
            elif self.state == STATE_HIGHSCORES:
                self.draw_highscores()
            elif self.state == STATE_INSTRUCTIONS:
                self.draw_instructions()
            elif self.state == STATE_NAME:
                self.draw_name()
            else:
                self.draw_menu()
            self.display.present()
        pygame.quit()
