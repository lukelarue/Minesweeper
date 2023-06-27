from flask import Flask, jsonify, render_template, request, session
from MinesweeperEnv import Minesweeper
import redis 
import pickle 
import uuid
import os

# Create the Flask application
app = Flask(__name__)

# Setup configurations for the Flask application
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set the secret key for the session
app.config['DEBUG'] = os.getenv('FLASK_DEBUG') == 'True'  # Set debug mode based on environment variable

# Establish connection to Redis
r = redis.from_url(os.getenv("REDIS_URL"))

@app.route('/')
def home():
    # Check if a UUID exists for the current session, if not generate one
    if 'uuid' not in session:
        session['uuid'] = str(uuid.uuid4())
    # Render the main page of the application
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    # Get the data from the incoming request
    data = request.get_json()
    n = int(data['boardSize'])
    m = int(data['numMines'])

    # Validate the board size and number of mines received in the request
    if not (4 <= n <= 25) or not (1 <= m <= n*n - 10):
        return "Invalid input. Please ensure the board size is an integer between 4 and 25, and the number of mines is an integer between 1 and (board size ^ 2 - 10).", 400

    # Create an instance of the Minesweeper game with the received board size and number of mines
    env = Minesweeper(n, m)
    _ = env.reset()

    # Serialize the game instance using pickle and store it in Redis with a 2 hour expiration time
    pickled_env = pickle.dumps(env)
    r.set('env_' + session['uuid'], pickled_env, 60 * 60 * 2)

    # Return an empty JSON as response
    return jsonify({})

@app.route('/move', methods=['POST'])
def move():
    # Get the action from the incoming request
    data = request.get_json()
    action = int(data['action'])

    # Retrieve the serialized game instance from Redis using the session's UUID
    pickled_env = r.get('env_' + session['uuid'])
    if pickled_env is None:
        return "Game not started or game was deleted 2 hours after last move. Please start the game first", 400
    # Deserialize the game instance
    env = pickle.loads(pickled_env)

    # Make a move in the game
    obs, reward, terminated, truncated, info = env.step(action)

    # Serialize the updated game instance and store it back in Redis with a 2 hour expiration time
    pickled_env = pickle.dumps(env)
    r.set('env_' + session['uuid'], pickled_env, 60 * 60 * 2)

    # Get the current state of the game board and convert it into a list
    obs_list = env.game_state.tolist()

    response_data = {'board': obs_list, 'info': info}

    # If the game has ended, include the actual board in the response.
    if info['result'] in ['win', 'lose']:
        response_data['actual_board'] = env.board.tolist()

    # Return the current game board and game info as response
    return jsonify(response_data)

# Run the Flask application
if __name__ == '__main__':
    app.run()
