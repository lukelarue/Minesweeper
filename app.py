from flask import Flask, jsonify, request, render_template
from Legacy.minesweeper import Game  # Your Minesweeper module
import uuid
import numpy as np

app = Flask(__name__)

games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    length = data['length']
    mines = data['mines']
    game_id = str(uuid.uuid4())
    games[game_id] = Game(length, mines)
    first_random_selection = np.random.randint(0,length**2)
    games[game_id].initMines(first_random_selection)
    _ = games[game_id].action(first_random_selection)
    
    return jsonify(game_id=game_id, board=games[game_id].game_state.tolist())

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    game_id = data['game_id']
    move = data['move']
    game = games[game_id]
    _ = game.action(move)

    return jsonify(game.game_state.tolist())

if __name__ == '__main__':
    app.run(host='0.0.0.0')

