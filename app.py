from flask import Flask, jsonify, render_template, request
from MinesweeperEnv import Minesweeper

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    n = int(data['boardSize'])
    m = int(data['numMines'])

    if not (4 <= n <= 25) or not (1 <= m <= n*n/4):
        return "Invalid input. Please ensure the board size is an integer between 4 and 25, and the number of mines is an integer between 1 and (board size ^ 2 / 4).", 400

    global env
    env = Minesweeper(n, m)

    _ = env.reset()

    obs_list = env.game_state.tolist()

    return jsonify({'board':obs_list})

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    action = int(data['action'])

    obs, reward, terminated, truncated, info = env.step(action)

    # Assuming the observation is a 2D numpy array
    obs_list = env.game_state.tolist()

    return jsonify({'board': obs_list, 'info': info})

if __name__ == '__main__':
    app.run()
