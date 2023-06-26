from flask import Flask, jsonify, render_template, request, session
from MinesweeperEnv import Minesweeper
import redis 
import pickle 
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# connect to Redis - Local
#r = redis.Redis(host='localhost', port=6379, db=0)

# connect to Redis - Heroku
r = redis.from_url(os.getenv("REDIS_URL"))

@app.route('/')
def home():
    # Assign a UUID for each session if it doesn't exist
    if 'uuid' not in session:
        session['uuid'] = str(uuid.uuid4())
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

    # pickle the environment and store in Redis
    pickled_env = pickle.dumps(env)
    r.set('env_' + session['uuid'], pickled_env)

    obs_list = env.game_state.tolist()

    return jsonify({'board':obs_list})

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    action = int(data['action'])

    # retrieve and unpickle the environment from Redis
    pickled_env = r.get('env_' + session['uuid'])
    if pickled_env is None:
        return "Game not started. Please start the game first", 400
    env = pickle.loads(pickled_env)

    obs, reward, terminated, truncated, info = env.step(action)

    # pickle the environment and store back in Redis
    pickled_env = pickle.dumps(env)
    r.set('env_' + session['uuid'], pickled_env)

    # Assuming the observation is a 2D numpy array
    obs_list = env.game_state.tolist()

    return jsonify({'board': obs_list, 'info': info})

if __name__ == '__main__':
    app.run()
