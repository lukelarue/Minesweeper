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

    global env
    env = Minesweeper(n, m)

    _ = env.reset()

    # Assuming the observation is a 2D numpy array
    obs_list = env.game_state.tolist()

    return jsonify({'board': obs_list})

@app.route('/move', methods=['POST'])
def move():
    print(request)
    data = request.get_json()
    print(data)
    action = int(data['action'])

    obs, reward, terminated, truncated, info = env.step(action)

    # Assuming the observation is a 2D numpy array
    obs_list = env.game_state.tolist()

    return jsonify({'board': obs_list, 'reward': reward, 'terminated': terminated})

if __name__ == '__main__':
    app.run(debug=True)
