import numpy as np

class Game:
    '''
    Game of Minesweeper
    '''

    def __init__(self, n, m):
        '''
        Initialize the board

        n (int) - dimensions of board square
        m (int) - number of mines on the board
        board (nxn array) - the actual board
        game_state (nxn array) - the state of the game player sees during play

        -1 is a mine
        9 is an uncovered spot on player board
        '''
        self.n = n
        self.m = m
        self.board = np.zeros((self.n, self.n), dtype=int)
        self.game_state = np.ones((self.n, self.n), dtype=int) * 9
        self.board_setup_required=True # board is initialized once the first click is given
    
    def step(self, click):
        '''
        *To replace self.action()
        Initialize board if just beginning
        Execute whats happens after someone clicks - click is given as the index integer
        Return 1 if you hit a mine, 0 otherwise, 2 if win
        '''
        if self.board_setup_required:
            self.initMines(click)
            self.board_setup_required = False
        
        row, col = self.rowcol(click)
        
        # return 3 if you already clicked there
        if(click in self.selected_safespots):
            return 3

        # die if u hit the mine --- 0 is inplay, 1 is die, 2 is game win, 3 is you already clicked there
        if (self.board[row][col] == -1):
            return 1

        self.selected_safespots.add(click)
        if self.selected_safespots == self.safespots: # you won!
            return 2

        # just show the one you clicked if there is a mine nearby
        if (self.board[row][col] > 0):
            self.game_state[row][col] = self.board[row][col]
            return 0

        # show all blank spaces adjacent if you clicked a 0
        if (self.board[row][col] == 0):
            self.showAdjacentNumbers(row, col, set())
            return 0



    def rowcol(self, num):
        '''
        Convert number index to row and column index
        '''
        row = num // self.n
        col = int(np.round(((num / self.n) - row) * self.n))
        return row, col

    def index(self, row, col):
        '''
        Changes row and column to number index
        '''
        return row * self.n + col

    def initMines(self, firstClick):
        '''
        Initiates mines either before or after the first click

        safespots (set containing all elements in range n**2 without the mines)
        selected_safespots (set that is updated when a safespot is selected)
        '''
        
        def fillnumbers(row, col):
            '''
            Adds 1 to all squares around the mine if they should be added
            '''
            for r in [row - 1, row, row + 1]:
                for c in [col - 1, col, col + 1]:
                    if r >= 0 and r < self.n and c >= 0 and c < self.n and not (r == row and c == col):
                        if (self.board[r][c] != -1):
                            self.board[r][c] += 1

        def createBoard():
            # create board based on mines
            for mine in self.mines:
                row, col = self.rowcol(mine)
                self.board[row, col] = -1
            for row in range(self.n):
                for col in range(self.n):
                    if (self.board[row][col] == -1):
                        fillnumbers(row, col)

            # create master list of all safespots and create updated list of already selected safespots
            self.safespots = set(np.delete(np.array(range(self.n ** 2)), self.mines))
            self.selected_safespots = set()

        row, col = self.rowcol(firstClick)
        # create list of all spots in a 3x3 grid around the first click - these cannot contain mines
        nomines = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if (row + i >= 0 and row + i < self.n and col + j >= 0 and col + j < self.n):
                    nomines.append(self.index(row + i, col + j))

        # create an array of all spots that could contain mines - spots in a 3x3 grid around the first click are removed
        potentialSpots = np.delete(np.array(range(self.n ** 2)), nomines)

        # randomly choose spots for the mines from the potential spots
        self.mines = np.random.choice(potentialSpots, self.m, replace=False)
        createBoard()

    def showAdjacentNumbers(self, row, col, visited, start_flag=True):
        '''
        shows all adjacent zeros until they hit a number in the game_state - recursive search
        '''
        if (start_flag):
            visited = set()
        start_flag = False

        # don't revisit the same tile
        if (row, col) in visited:
            return
        visited.add((row, col))

        # stop searching if you go out of bounds or hit a mine
        if (row < 0 or row >= self.n or col < 0 or col >= self.n):
            return
        if (self.board[row][col] == -1):
            return


        # show the zero in the game_state and continue searching all around
        elif (self.board[row][col] == 0):
            self.game_state[row][col] = 0
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if not (j == 0 and i == 0):
                        self.showAdjacentNumbers(row + i, col + j, visited, start_flag)
        # show the number and discontinue searching if you hit a number
        else:
            self.game_state[row][col] = self.board[row][col]

        self.selected_safespots.add(self.index(row, col))

    def action(self, click):
        '''
        Execute whats happens after someone clicks - click is given as the index integer
        Return 1 if you hit a mine, 0 otherwise, 2 if win
        '''
        row, col = self.rowcol(click)
        
        # return 3 if you already clicked there
        if(click in self.selected_safespots):
            return 3

        # die if u hit the mine --- 0 is inplay, 1 is die, 2 is game win, 3 is you already clicked there
        if (self.board[row][col] == -1):
            return 1

        self.selected_safespots.add(click)
        if self.selected_safespots == self.safespots:
            return 2

        # just show the one you clicked if there is a mine nearby
        if (self.board[row][col] > 0):
            self.game_state[row][col] = self.board[row][col]
            return 0

        # show all blank spaces adjacent if you clicked a 0
        if (self.board[row][col] == 0):
            self.showAdjacentNumbers(row, col, set())
            return 0

    def run_click(self, click):  # called once game is initialized to run plays

        # get selected_safespots before and after and return the index, value of after from before
        previous_safespots = self.selected_safespots.copy()
        result = self.action(click)
        if (result == 1): 
            return 'loss'
        else:
            return self.selected_safespots - previous_safespots
        

    def play(self, firstClick):
        '''
        Executes human gameplay
        '''

        def select_action():
            '''
            Prints the board and asks the player to select an action
            '''

            print('Please click on a tile')

            action = int(input('index: '))
            return action

        start = self.initMines(firstClick)
        result = self.action(firstClick)
        if (self.selected_safespots == self.safespots):
            self.victory()
            return

        print('Number of mines: ' + str(self.m))
        # print selection information
        print(np.arange(self.n ** 2).reshape(self.n, self.n))
        print()
        print("Begin")

        # keep playing while result == 0, lose game if result == 1, stop playing if you have selected all safespots
        while (result == 0 or result == 3):
            print(self.game_state)

            if (self.selected_safespots == self.safespots):
                self.victory()
                return
            click = select_action()
            result = self.action(click)
        
        if result == 2:
            self.victory()
            return

        if result == 1:
            self.loser()
            return
        else:
            print('error: result should be 1 or 2')
