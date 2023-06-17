import tkinter as tk
import minesweeper as ms
from PIL import ImageTk, Image
import numpy as np

class Minesweeper_board:
    def __init__(self, game):
        self.window = tk.Tk()
        self.window.title('Minesweeper')
        self.game = game
        self.board = self.game.board
        self.flags_remaining = self.game.m
        self.n = self.board.shape[0]
        self.initialize_menu()
        self.initialize_images()
        self.create_tiles()

    def initialize_menu(self):
        # create title label and mines remaining label
        self.title = tk.Label(self.window, text='{}x{}\n{} mines'.format(self.n, self.n, self.game.m))
        self.mines_remaining = tk.Label(self.window, text = 'N/A')

        self.title.grid(row=0, column=0, columnspan=3, sticky='W')
        self.mines_remaining.grid(row=0, column=self.n-1)

        #create restart button
        self.restart_image = ImageTk.PhotoImage(Image.open(r'images\reset.png').resize((48, 48), Image.ANTIALIAS))
        self.restart_button = tk.Button(self.window, image = self.restart_image, command = self.reset)

        self.restart_button.grid(row = 0, column = self.n // 2 - 1)

        #create flag, continue, loss, win labels
        self.flag_img = ImageTk.PhotoImage(Image.open(r'images\flag.png').resize((48, 48), Image.ANTIALIAS))
        self.flag_label = tk.Label(self.window, image=self.flag_img, relief = tk.SUNKEN)

        self.continue_img = ImageTk.PhotoImage(Image.open(r'images\continue.png').resize((48, 48), Image.ANTIALIAS))
        self.continue_label = tk.Label(self.window, image=self.continue_img)

        self.lose_img= ImageTk.PhotoImage(Image.open(r'images\lose.png').resize((48, 48), Image.ANTIALIAS))
        self.win_img = ImageTk.PhotoImage(Image.open(r'images\win.png').resize((48, 48), Image.ANTIALIAS))

        self.continue_label.grid(row = 0, column = self.n//2)
        self.flag_label.grid(row = 0, column = self.n-2)

    def initialize_images(self):
        self.images = {}
        for num in range(9):
            self.images[str(num)] = ImageTk.PhotoImage(Image.open(r'images\{}.png'.format(str(num))).resize((48, 48), Image.ANTIALIAS))
        self.images['bomb'] = ImageTk.PhotoImage(Image.open(r'images\bomb.png').resize((48, 48), Image.ANTIALIAS))
        self.images['facingDown'] = ImageTk.PhotoImage(Image.open(r'images\facingDown.png').resize((48, 48), Image.ANTIALIAS))
        self.images['boom'] = ImageTk.PhotoImage(Image.open(r'images\boom.png').resize((48, 48), Image.ANTIALIAS))


    def reset(self): # don't use too often - uses up memory quickly
        self.game.__init__(self.game.n, self.game.m)
        self.board = self.game.board
        self.flags_remaining = self.game.m
        self.create_tiles()
        self.initialize_menu()


    def rowcol(self, num):
        """
        Changes index number to row and column index
        """
        row = num // self.n
        col = int(np.round(((num/self.n) - row) * self.n))
        return row, col

    def create_tiles(self):
        """
        Creates blank Tiles to fill the board with initializing button commands
        """
        self.tiles = np.empty_like(self.board, dtype = 'object')
        for i in range(self.n**2):
            row, col = self.rowcol(i)
            self.tiles[row][col] = Tile(self.game, self, self.window, self.n, i)

    def fill_tiles(self):
        """
        Called once the board is created - fills the values for each Tile and changes the button action to normal state
        """
        self.mines_remaining.config(text = str(self.flags_remaining), fg = 'green') # initiate the number of mines the flag has

        for i, value in enumerate(self.board.flatten()):
            row, col = self.rowcol(i)
            self.tiles[row][col].get_images(value)
            self.tiles[row][col].button.config(command = self.tiles[row][col].gameplay_click)
            self.tiles[row][col].button.bind('<Button-3>', self.tiles[row][col].right_click)  # bind right mouse click

    def end_game(self, condition):
        for tile in self.tiles.flatten():
            tile.button.config(state=tk.DISABLED, image=tile.value_img)
        if(condition == 'win'):
            self.continue_label.config(image = self.win_img)
        if(condition == 'loss'):
            self.continue_label.config(image = self.lose_img)



class Tile:
    def __init__(self, game, tk_board, window, n, idx):
        self.flagged = False
        self.game = game
        self.tk_board = tk_board
        self.window = window
        self.n = n
        self.idx = idx
        self.row = self.idx // self.n
        self.col = self.idx % self.n
        self.board_row = self.row + 1
        self.create_button()

    def get_images(self, value):
        """
        Sets the value and value_img
        """
        self.value = value

        if (self.value == -1):
            imgvalue = 'bomb'
        else:
            imgvalue = str(self.value)
        self.value_img = self.tk_board.images[imgvalue]
        self.value_label = tk.Label(self.window, image = self.value_img) # overlaps the button once the button is clicked

    def right_click(self, event):
        if(self.flagged):
            self.button.config(image = self.uncovered_img)
            self.flagged = False
            self.tk_board.flags_remaining += 1
            self.tk_board.mines_remaining.config(text = str(self.tk_board.flags_remaining))
        else:
            self.button.config(image = self.tk_board.flag_img)
            self.flagged = True
            self.tk_board.flags_remaining -= 1
            self.tk_board.mines_remaining.config(text = str(self.tk_board.flags_remaining))

        if(self.tk_board.flags_remaining == 0):
            self.tk_board.mines_remaining.config(fg = 'black')
        if(self.tk_board.flags_remaining < 0):
            self.tk_board.mines_remaining.config(fg = 'red')
        if(self.tk_board.flags_remaining > 0):
            self.tk_board.mines_remaining.config(fg = 'green')


    def gameplay_click(self):
        """
        Executes gameplay function when a tile is clicked
        """

        result = self.game.run_click(self.idx)
        if(result == 'loss'):
            self.boom_img = self.tk_board.images['boom'] # crate the boom image to show which tile you lost on
            self.tk_board.end_game('loss')
            self.button.config(image = self.boom_img)
            return

        # If you did not click a mine, show all the tiles that were shown
        for i in list(result):
            self.tk_board.tiles.flatten()[i].show_value_img()

        if(self.game.selected_safespots == self.game.safespots):
            self.tk_board.end_game('win')


    def show_value_img(self):
        """
        Disables the button and places the value label over the button
        """
        self.button.config(state = tk.DISABLED)
        self.value_label.grid(row = self.board_row, column = self.col)


    def initializing_click(self):
        """
        Initializes the mines using the first click, fills the board's tiles,
        shows the image of the clicked and surrounding tiles
        """
        self.game.initMines(self.idx)
        self.tk_board.fill_tiles()
        self.show_value_img()
        self.gameplay_click()


    def create_button(self):
        """
        Create button object, pack it
        """
        self.uncovered_img = self.tk_board.images['facingDown']
        self.button = tk.Button(self.window, image=self.uncovered_img, command = self.initializing_click)
        self.button.grid(row=self.board_row, column=self.col)

def play_minesweeper(n, m):
    game = ms.Game(n, m)
    minesweeper_board = Minesweeper_board(game)
    minesweeper_board.window.mainloop()

if __name__ == '__main__':
    play_minesweeper(15, 120)