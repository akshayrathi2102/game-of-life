#!/usr/bin/env python3

import numpy as np
import curses
import json
from curses import textpad


class GameOfLife:
    def __init__(self):
        self.SCREEN_WIDTH = 0  # total width of the available screen
        self.SCREEN_HEIGHT = 0  # total height of the available screen
        self.ROWS = 0  # number of rows in the board
        self.COLS = 0  # number of columns in the board
        self.board = np.zeros((10, 10), dtype=int)
        self.LEFT_MARGIN = 2
        self.RIGHT_MARGIN = 13
        self.TOP_MARGIN = 3
        self.BOTTOM_MARGIN = 2
        self.OPTIONS = {
            ord("0"): "Block",
            ord("1"): "Beehive",
            ord("2"): "Loaf",
            ord("3"): "Boat",
            ord("4"): "Tub",
            ord("5"): "Blinker",
            ord("6"): "Toad",
            ord("7"): "Beacon",
            ord("8"): "Glider",
            ord("9"): "Saved",
            ord("r"): "Random",
        }
        self.CONFIG = {}  # all configurations

    def set_screen(self, stdscr):
        """
        Set the values of screen height and width.
        Also set values for number of rows and columns for board.

        Parameters:
            stdscr: Window object
        """
        self.SCREEN_HEIGHT, self.SCREEN_WIDTH = stdscr.getmaxyx()
        self.ROWS = self.SCREEN_HEIGHT - self.TOP_MARGIN - self.BOTTOM_MARGIN - 1
        self.COLS = self.SCREEN_WIDTH - self.LEFT_MARGIN - self.RIGHT_MARGIN - 1

    def load_config(self):
        """
        Loads the various configurations from the configuration file in 'CONFIG'.
        """
        with open("config.json") as config_file:
            self.CONFIG = json.load(config_file)

    def save_config(self):
        """
        Adds the present state in the CONFIG json object and
        then writes it in the configuration file.
        """
        self.CONFIG["Saved"] = self.board.tolist()
        with open("config.json", "w") as config_file:
            json.dump(self.CONFIG, config_file)

    def populate_board(self, option):
        """
        Populates the board according to given parameters using the CONFIG object.

        Parameters:
            option (string): Configuration which needs to be written on the board.
        """
        self.load_config()

        self.board = np.zeros((self.ROWS, self.COLS), dtype=int)
        if option == "Random":
            self.board = np.random.randint(0, 2, (self.ROWS, self.COLS))

        else:
            self.board[
                0 : len(self.CONFIG[option]), 0 : len(self.CONFIG[option][0])
            ] = self.CONFIG[option]

    def count_alive_neighbours(self, r, c):
        """
        Counts the number of alive neighbour of a cell in the board.
        Wraps around the board if neighbours go out of bound.

        Parameters:
            r (int): row number of the cell
            c (int): column number of the cell

        Returns:
            int : number of neighbouring cells of cell(r, c) that have 1 in them.
        """
        alive_neighbours = 0
        for x in range(r - 1, r + 2):
            for y in range(c - 1, c + 2):
                x = (x + self.ROWS) % self.ROWS
                y = (y + self.COLS) % self.COLS
                alive_neighbours += self.board[x, y]

        return alive_neighbours - self.board[r, c]

    def update_board(self):
        """
        Updates the board to the next generation.
        Changes the value of each cell based on its alive neighbours.
        """
        new_board = np.zeros(self.board.shape, dtype=int)
        for r, c in np.ndindex(self.board.shape):
            alive_neighbours = self.count_alive_neighbours(r, c)

            if self.board[r, c] == 1:
                if alive_neighbours <= 3 and alive_neighbours >= 2:
                    new_board[r, c] = 1

            elif self.board[r, c] == 0:
                if alive_neighbours == 3:
                    new_board[r, c] = 1

        self.board = new_board

    def draw_board(self, stdscr):
        """
        Draws the game board on the screen.
        Prints the state of each cell on the screen.

        Parameters:
            stdscr: Window object
        """
        for r, c in np.ndindex(self.board.shape):
            if self.board[r][c] == 1:
                stdscr.addstr(r + self.TOP_MARGIN + 1, c + self.LEFT_MARGIN + 1, "█")

            else:
                stdscr.addstr(r + self.TOP_MARGIN + 1, c + self.LEFT_MARGIN + 1, " ")

        stdscr.refresh()

    def print_box(self, stdscr):
        """
        Prints the outer box of the board on the screen.
        """
        textpad.rectangle(
            stdscr,
            self.TOP_MARGIN,
            self.LEFT_MARGIN,
            self.TOP_MARGIN + self.ROWS + 1,
            self.LEFT_MARGIN + self.COLS + 1,
        )
        stdscr.refresh()

    def game_loop(self, stdscr):
        """
        Main game loop.
        Enter key takes to next generation.
        keys[0-9] or r sets the board to the corresponding configuration.
        s saves the state.
        q quits the game.

        Parameters:
            stdscr: window object
        """
        while True:
            key = stdscr.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                self.update_board()
                self.draw_board(stdscr)

            elif key == ord("s") or key == ord("S"):
                self.save_config()

            elif key in [ord(str(x)) for x in range(10)] or key == ord("r"):
                self.populate_board(self.OPTIONS[key])
                self.draw_board(stdscr)

            elif key == ord("q") or key == ord("Q"):
                break

    def print_side_menu(self, stdscr):
        """
        Prints the side menu on the .

        Parameters:
            stdscr: window object
        """
        stdscr.addstr(4, self.SCREEN_WIDTH - 11, "Options: ")
        for i in range(10):
            stdscr.addstr(
                6 + i,
                self.SCREEN_WIDTH - 11,
                str(i) + ": " + str(self.OPTIONS[ord(str(i))]),
            )
        stdscr.addstr(16, self.SCREEN_WIDTH - 11, "r: " + str(self.OPTIONS[ord("r")]))

    def print_down_menu(self, stdscr):
        """
        Prints the down menu on the screen.

        Parameters:
            stdscr: window object
        """
        stdscr.addstr(self.SCREEN_HEIGHT - 1, 3, "q: quit")
        stdscr.addstr(self.SCREEN_HEIGHT - 1, self.COLS // 2 - 6, "Enter: Next state")
        stdscr.addstr(self.SCREEN_HEIGHT - 1, self.COLS - 5, "s: Save")

    def print_menu(self, stdscr):
        """
        Prints the whole menu by calling print_down_menu() and print_side_menu().

        Parameters:
            stdscr: window object
        """
        self.print_side_menu(stdscr)
        self.print_down_menu(stdscr)

    def print_title(self, stdscr):
        """
        Prints the title of the game.

        Parameters:
            stdscr: window object
        """
        ascii_banner = "GAME OF LIFE \U0001F600"
        stdscr.addstr(1, self.SCREEN_WIDTH // 2 - len(ascii_banner) // 2, ascii_banner)

    def game_controller(self, stdscr):
        """
        Main controller of game.
        Sets up the whole game and draws everything.
        Then populates the board based on user input and finally calls
        the game loop.

        Parameters:
            stdscr: window object
        """
        self.set_screen(stdscr)
        curses.curs_set(0)
        self.print_title(stdscr)
        self.print_box(stdscr)
        self.print_menu(stdscr)
        key = stdscr.getch()
        self.populate_board(self.OPTIONS[key])
        self.draw_board(stdscr)
        self.game_loop(stdscr)

    def init_game(self):
        """
        Initialises the game.
        """
        curses.wrapper(self.game_controller)
