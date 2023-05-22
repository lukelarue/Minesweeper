from flask import Flask, render_template
from minesweeper import Game
import numpy as np

app = Flask(__name__)

# Minesweeper stuff
game = Game(16, 40)
selection_visualizer = np.arange(game.n ** 2).reshape(game.n, game.n)
start = game.initMines(136) # Start the game roughly in the middle of the board
result = game.action(136)

@app.route("/")
def home():
    print(game)
    print('hello')
    return render_template('index.html', game = game, selection_visualizer = selection_visualizer)

if __name__ == "__main__":
    app.run()