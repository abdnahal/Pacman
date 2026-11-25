import pygame
from .display import Display, YELLOW, WHITE
from .highscores import HighScoreStore
from .maze import load_maze, MazeError
from .player import Player
from .level import Level


STATE_MENU = "menu"
STATE_GAME = "game"
STATE_NAME = "name"


class Game:
    def __init__(self, config, warnings):
        pygame.init()
        pygame.key.set_repeat(400, 50)
        pygame.display.set_caption("Pac-Man")

        self.config = config
        self.warnings = warnings
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU
        self.level_index = 0
        self.score = 0
        self.lives = config["lives"]
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
        return True

    def end_game(self, result):
        self.result = result
        self.name = ""
        self.state = STATE_NAME

    def handle_menu(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_s, pygame.K_SPACE):
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def handle_game(self, event):
        if event.type == pygame.KEYDOWN:
            self.player.set_direction(event.key)
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            if self.config["cheat_mode"]:
                if event.key == pygame.K_F1:
                    self.cheat_invincible = not self.cheat_invincible
                elif event.key == pygame.K_F2:
                    self.end_game("WIN")
                elif event.key == pygame.K_F3:
                    self.end_game("LOSE")

    def handle_name(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RETURN:
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
        self.display.draw_text("Press ENTER or S to Start", 180)
        self.display.draw_text("HIGHSCORES", 250, self.display.font)
        scores = self.highscores.load()
        if not scores:
            self.display.draw_text("No scores yet", 300, self.display.small_font)
        else:
            for index, item in enumerate(scores, start=1):
                self.display.draw_text(
                    f"{index:2}. {item['name']:<10}  {item['score']}",
                    290 + index * 34,
                    self.display.small_font,
                    center=False,
                )
        if self.error_message:
            self.display.draw_text(self.error_message, self.display.height - 70,
                                   self.display.small_font)
        for warning in self.warnings[:2]:
            self.display.draw_text(warning, self.display.height - 40,
                                   self.display.small_font)

    def draw_game(self):
        self.display.clear()
        self.display.draw_maze(self.maze)
        self.display.draw_player(self.player)

    def draw_name(self):
        self.display.clear()
        self.display.draw_text(
            f"GAME {self.result}", 180, self.display.large_font,
            YELLOW,
        )
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
                elif self.state == STATE_NAME:
                    self.handle_name(event)

            if self.state == STATE_GAME:
                self.player.update(
                    frame_time, self.maze,
                    len(self.maze[0]), len(self.maze),
                    self.tile_size,
                )
                self.draw_game()
            elif self.state == STATE_NAME:
                self.draw_name()
            else:
                self.draw_menu()
            self.display.present()
        pygame.quit()
