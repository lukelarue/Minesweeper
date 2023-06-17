import numpy as np
import gymnasium as gym



class Minesweeper(gym.Env):

    def __init__(self, n, m, seed=None):
        """
        Initialize the Minesweeper environment.
        
        This function sets up the game board and the observation and action spaces for the Minesweeper game. If a seed 
        is provided, it will be used to control the randomness when placing the mines on the board, allowing for the 
        reproduction of specific game conditions.

        Parameters:
        n (int): The dimensions of the board. The board will be a square of size n x n.
        m (int): The number of mines on the board.
        seed (int, optional): An optional seed for the random number generator used to place the mines. If provided,
                              this seed allows for the reproduction of specific game conditions.
        
        The function also initializes two internal state variables:
        
        board (n x n array): The actual board state, unknown to the agent. Each cell in the board can be one of the 
                            following:
                            - 0 to 8: The number of mines in the surrounding cells
                            - -1: Indicates a mine
                            
        game_state (n x n array): The game state as seen by the player during play. Each cell in the game state can be 
                                one of the following:
                                - 0 to 8: The number of mines in the surrounding cells (only for revealed cells)
                                - 9: Indicates a covered cell
                                
        The function also initializes the action and observation spaces. The action space is a discrete space with n * n 
        possible actions, corresponding to the n * n cells on the board. The observation space is a 10-channel binary image 
        of shape 10 x n x n, where each channel corresponds to one of the 10 possible states for each cell.
        """
        self.n = n
        self.m = m
        self.board = np.zeros((self.n, self.n), dtype=int) # internal state - unknown to agent
        self.game_state = np.ones((self.n, self.n), dtype=int) * 9
        self.game_not_initialized = True
        self.np_random = np.random.default_rng(seed)

        self.action_space = gym.spaces.Discrete(self.n * self.n)
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(10, self.n, self.n), dtype=np.uint8)


    def _convertActionToCoordinates(self, action):
        """
        Convert a one-dimensional action index to its corresponding two-dimensional grid coordinates.

        This method takes an action, defined as an integer index within the range of total cells on the 
        Minesweeper board, and converts it into a corresponding (row, column) pair representing the cell's 
        location on the two-dimensional grid.

        Parameters:
        action (int): The action to be converted, represented as an integer index.

        Returns:
        tuple: A tuple containing the (row, column) coordinates corresponding to the action.
        """
        row = action // self.n
        col = action % self.n
        return row, col

    def _convertCoordinatesToAction(self, row, col):
        """
        Convert a two-dimensional grid coordinate to its corresponding one-dimensional action index.

        This method takes a pair of (row, column) coordinates, representing a cell's location on the 
        two-dimensional Minesweeper grid, and converts it into a corresponding action. The action is defined 
        as an integer index within the range of total cells on the Minesweeper board.

        Parameters:
        row (int): The row coordinate to be converted.
        col (int): The column coordinate to be converted.

        Returns:
        int: The action corresponding to the (row, column) coordinates.
        """
        return row * self.n + col           

    def _setupGameBoard(self, action):
        """
        Initializes the Minesweeper game board with the appropriate configuration of mines and safe tiles.

        This method first calculates potential mine locations excluding a 3x3 grid centered at the initial
        action's coordinates, as this area cannot contain mines. Mines are then randomly placed in these potential
        locations using a seeded random number generator (if a seed was provided when creating the environment).
        The numbers on the board are updated based on the number of adjacent mines for each cell.

        Parameters:
        action (int): The initial action to be taken on the game board.

        Note: 
        This method modifies the object's state in-place. The Minesweeper game board (`self.board`), the 
        set of mine locations (`self.mines`), the set of safe tiles (`self.safe_tiles`), and the set of 
        revealed tiles (`self.revealed_tiles`) are updated.
        """
        row, col = self._convertActionToCoordinates(action)
        invalid_mine_locations = [self._convertCoordinatesToAction(row + i, col + j) # 3x3 grid surrounding the initial action can not contain mines
                    for i in [-1, 0, 1] 
                    for j in [-1, 0, 1] 
                    if (0 <= row + i < self.n) and (0 <= col + j < self.n)]
        potential_mine_locations = np.delete(np.array(range(self.n ** 2)), invalid_mine_locations)
        self.mines = self.np_random.choice(potential_mine_locations, self.m, replace=False)

        #Create board            
        for mine in self.mines:
            row, col = self._convertActionToCoordinates(mine)
            self.board[row, col] = -1
            
            # Determine coordinates of 8 neighboring cells
            neighbors = [(i, j) 
                        for i in [row - 1, row, row + 1] 
                        for j in [col - 1, col, col + 1] 
                        if (0 <= i < self.n) and (0 <= j < self.n) and not (i == row and j == col)]
            
            # Add 1 to all valid neighbors
            for i, j in neighbors:
                if (self.board[i, j] != -1):
                    self.board[i, j] += 1
        
        # create master list of all safe tiles and create a set that will be updated with the agent's revealed tiles as the game progresses
        self.safe_tiles = set(np.delete(np.array(range(self.n ** 2)), self.mines))
        self.revealed_tiles = set()

    def _revealSafeTiles(self, row, col):
        """
        Perform a recursive search to reveal all adjacent safe tiles on the Minesweeper board.

        This method starts from the specified tile (defined by row and col), and recursively reveals all 
        connected tiles that contain a zero, effectively uncovering an entire safe zone on the board. The 
        search stops when it hits a numbered tile or a boundary of the board. Numbered tiles are also revealed, 
        but the function does not search beyond them. 

        The method modifies the game state in place, updating the 'game_state' to reflect the revealed tiles 
        and adding the safe tiles to the 'revealed_tiles' set.

        Parameters:
        row (int): The row index of the starting tile.
        col (int): The column index of the starting tile.

        Note: 
        This method modifies the object's state in-place. The Minesweeper game state (`self.game_state`) and 
        the set of revealed tiles (`self.revealed_tiles`) are updated.
        """
        visited = set()
        safespots = set()

        def search(r, c):
            if not (0 <= r < self.n and 0 <= c < self.n) or (r, c) in visited or self.board[r][c] == -1:
                return

            visited.add((r, c))
            safespots.add(self._convertCoordinatesToAction(r, c))

            if self.board[r][c] == 0:
                self.game_state[r][c] = 0
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        if not (j == 0 and i == 0):
                            search(r + i, c + j)
            else:
                self.game_state[r][c] = self.board[r][c]

        search(row, col)

        self.revealed_tiles = self.revealed_tiles | safespots

    def _convert_state(self):
        """
        Convert the game state into a more detailed representation for agent.

        The original game state is a single (n x n) array where each cell 
        holds a value representing the number of adjacent mines (0-8) or 
        a special value (9) if the cell is uncovered. 

        This function converts the game state into 10 separate (n x n) 
        binary mask arrays where each array represents one possible cell 
        state: having 0-8 adjacent mines or being uncovered. 
        
        This expanded state representation can make it easier for a learning 
        agent to interpret the game state without needing to extract 
        individual bits of information from cell values.

        Returns:
        numpy.ndarray: A 3D numpy array of shape (10, n, n) containing the 
                    binary mask arrays for the different cell states.
        """
        state_representation = np.zeros((10, self.n, self.n))
        for i in range(10):
            state_representation[i] = np.where(self.game_state == i, 1, 0)
        return state_representation


    def step(self, action):
        """
        Executes a step in the Minesweeper game by taking the given action.

        The action corresponds to the selection of a tile on the Minesweeper board. If the game is not 
        yet initialized, this method will set up the game board before processing the action. Invalid actions 
        (like choosing an already revealed tile) are handled and do not result in a change in the game state. 
        If a mine is hit, the game ends. If a safe tile is uncovered, the game continues and the agent is rewarded.

        Parameters:
        action (int): The action to be taken, represented as a linear index of a tile on the board.

        Returns:
        tuple: A 5-element tuple containing:
            - game_state (numpy.ndarray): The current game state after taking the action.
            - reward (int): The reward received for taking the action. Rewards are:
                - -100 for hitting a mine,
                - 100 for uncovering all safe tiles,
                - 1 for uncovering a safe tile,
                - 0 for taking an invalid action.
            - terminated (bool): A boolean flag indicating if the game has ended (either by hitting a mine or uncovering all safe tiles).
            - False (bool): A placeholder value for truncation. Always False in the implementation.
            - {}: A placeholder for extra information. Always an empty dictionary in this implementation.
        """
        
        if self.game_not_initialized:
            self._setupGameBoard(action)
            self.game_not_initialized = False
        
        if action in self.revealed_tiles: # do nothing as this is an invalid action - this tile has already been revealed
            reward = 0
            terminated = False
            return self._convert_state(), reward, terminated, False, {}
        
        row, col = self._convertActionToCoordinates(action)

        if (self.board[row][col] == -1): # hit a mine and lose
            reward = -100
            terminated = True
        
        else: # not hit a mine
            self._revealSafeTiles(row, col)

            if(self.revealed_tiles == self.safe_tiles): # all safe tiles has been uncovered - victory!
                reward = 100
                terminated = True
            else: # more tile(s) are uncovered and the game continues
                reward = 1
                terminated = False
        
        return self._convert_state(), reward, terminated, False, {}
    
    def reset(self, seed = None):
        """
        Reset the environment to its initial state.
        
        This method resets the Minesweeper game board to its initial state, ready to start a new episode. 
        It also resets the related state variables and returns the initial observation.

        It also creates a new random number generator with an optional seed. If a seed is 
        provided, the environment will be deterministic, meaning it will generate the same 
        sequences given the same seed.

        Parameters:
        seed (int, optional): The seed for the random number generator. Default is None, 
        which results in a non-deterministic environment.
        
        Returns:
        numpy.ndarray: The initial observation after resetting the game. The initial observation is a 3D numpy array 
        of shape (10, n, n) representing the game state. All cells are covered at the start, so the last 
        channel is filled with ones and the other channels are filled with zeros.
        """
        # Reset the board
        self.board = np.zeros((self.n, self.n), dtype=int)
        
        # Reset the game state
        self.game_state = np.ones((self.n, self.n), dtype=int) * 9

        # Reset the state indicating that the game is not initialized
        self.game_not_initialized = True

        # Reset the safe and revealed tiles
        self.safe_tiles = set()
        self.revealed_tiles = set()

        # Set new seed
        self.np_random = np.random.default_rng(seed)

        # Return the initial observation
        return self._convert_state()
    
    def render(self, mode='human'):
        """
        Render the current game state. Display a grid where covered cells are represented by '#', revealed cells
        display the number of neighboring mines, and mines are represented by '*'.
        
        Parameters:
        mode (str): The mode for rendering. If it's 'human', the current game state is printed out. Other modes 
                    could be added for returning the state as a data structure.
        """
        if mode == 'human':
            rendered_board = np.full((self.n, self.n), '#', dtype=str)  # Initially fill the board with '#'.
            for row in range(self.n):
                for col in range(self.n):
                    if self.game_state[row, col] != 9:  # If a cell is not covered.
                        if self.board[row, col] == -1:  # If a cell is a mine.
                            rendered_board[row, col] = '*'
                        else:
                            rendered_board[row, col] = str(self.game_state[row, col])
            print('\n'.join([' '.join(row) for row in rendered_board]))
        else:
            raise NotImplementedError


        


        



                

