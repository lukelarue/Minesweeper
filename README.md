# Minesweeper Online

This repository contains the code for a web-based version of the classic Minesweeper game, which you can play at [lukelarue.com](http://www.lukelarue.com). The game is implemented as a Flask application and deployed on Heroku.

## Directory Structure

- `legacy/` : This directory contains older versions of the code and a tkinter GUI for playing Minesweeper locally.
- `static/` : This directory contains static files used by the Flask application, including images, the JavaScript file `script.js`, and the CSS file `styles.css`.
- `templates/` : This directory contains HTML templates used by the Flask application.
- `MinesweeperEnv.py` : This file defines a gym environment for the Minesweeper game. This could be used to train a reinforcement learning agent to play the game in the future.
- `app.py` : This is the main Flask application file. It defines the routes for the web application and controls the game logic.
- `Procfile` : This file is used by Heroku to start the web application.
- `requirements.txt` : This file lists the Python dependencies that need to be installed for the application to run.
- `.gitignore` : This file tells Git which files and directories to ignore when committing changes to the repository.

## Running the Application Locally

To run the application on your local machine, follow these steps:

1. Clone the repository: `git clone https://github.com/<your-username>/minesweeper.git`
2. Navigate to the project directory: `cd minesweeper`
3. Install the dependencies: `pip install -r requirements.txt`
4. Install redis and set environment variables found in app.py
5. Start the Flask application: `python app.py`

The application will be available at `localhost:5000` in your web browser.

## License

This project is licensed under the [MIT License](LICENSE.md).

