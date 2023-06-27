// Define game variables globally
var boardSize;
var numMines;
var isGameOver = false;
var flaggedCells = [];

// Function to start a new game
function startGame() {
    // Reset game state
    isGameOver = false;

    // Get board size and mine count from user input
    boardSize = parseInt(document.getElementById('boardSize').value);
    numMines = document.getElementById('numMines').value;
    document.getElementById('currentSettings').innerText = `size ${boardSize} minesweeper board with ${numMines} mines`;

    // Initialize flagged cell array
    flaggedCells = Array(boardSize).fill().map(() => Array(boardSize).fill(false));

    // Reset Flags Used and previous victory condition
    document.getElementById('flagsUsed').textContent = 'Flags used: ' + countFlags(flaggedCells);
    gameResult.innerHTML = '&nbsp'

    // Post request to '/start' endpoint to start the game on the server
    fetch('/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            boardSize: boardSize,
            numMines: numMines
        })
    })
    .then(response => response.json())
    .then(data => {
        // Generate game board in HTML dynamically
        var gameBoard = document.getElementById('gameBoard');
        gameBoard.innerHTML = ''; // Clear any existing board
        for (var i = 0; i < boardSize; i++) {
            var row = document.createElement('tr');
            for (var j = 0; j < boardSize; j++) {
                var cell = document.createElement('td');
                cell.setAttribute('onclick', 'makeMove(' + i + ', ' + j + ')');
                cell.setAttribute('oncontextmenu', 'flagCell(event, ' + i + ', ' + j + ')');
                var img = document.createElement('img');
                img.setAttribute('id', 'cell'+i+'-'+j);
                img.setAttribute('src', '/static/images/unrevealed.png');
                cell.appendChild(img);
                row.appendChild(cell);
            }
            gameBoard.appendChild(row);
        }
    });
}

// Function to make a move on the board
function makeMove(row, col) {
    // If the game is over or the cell is flagged, ignore the click
    if (isGameOver || flaggedCells[row][col]) {
        return;
    }    
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: row * boardSize + col
        })
    })
    .then(response => response.json())
    .then(data => {
        // If game has ended, data.actual_board will be the complete board.
        var board = (data.info.result === 'win' || data.info.result === 'lose') ? data.actual_board : data.board;
        for (var i = 0; i < boardSize; i++) {
            for (var j = 0; j < boardSize; j++) {
                var img = document.getElementById('cell'+i+'-'+j);
                var imgValue = board[i][j];
                var imgName = 'unrevealed';
                if (imgValue === -1) {
                    imgName = 'bomb';
                } else if (imgValue >= 0 && imgValue <= 8) {
                    imgName = imgValue.toString();
                }
        
                // If the cell is flagged, keep displaying the flag image
                if (!flaggedCells[i][j]) {
                    img.setAttribute('src', '/static/images/' + imgName + '.png');
                }
        
                if (data.info.result === 'win' || data.info.result === 'lose') {
                    img.classList.add('game-over');  // Grey out tiles if the game has ended.
                }
            }
        }

        if (data.info.result === 'lose') {
            // Show a 'boom' image at the location of the last click
            var img = document.getElementById('cell'+row+'-'+col);
            img.setAttribute('src', '/static/images/boom.png');
        }

        // Update flags counter
        document.getElementById('flagsUsed').textContent = 'Flags used: ' + countFlags(flaggedCells);
        
        var gameResult = document.getElementById('gameResult');
        gameResult.innerHTML = '';

        // Update game status message based on the result from server
        switch (data.info.result) {
            case 'win':
                gameResult.style.color = 'green';
                gameResult.innerText = 'Victory!';
                break;
            case 'lose':
                gameResult.style.color = 'red';
                gameResult.innerText = 'Lost!';
                break;
            case 'invalid action':
                gameResult.style.color = 'orange';
                gameResult.innerText = 'Invalid action!';
                break;
            default:
                gameResult.innerHTML = '&nbsp';  // no message for "continue"
                break;
        }

        // Update game over state if win or loss is detected
        if (data.info.result === 'win' || data.info.result === 'lose') {
            isGameOver = true;
        }
    });
}

// Function to flag a cell
function flagCell(event, row, col) {
    // Prevent default context menu
    event.preventDefault();

    var cellImg = document.getElementById('cell'+row+'-'+col);

    // Toggle flagged state and image of cell
    if (cellImg.src.includes('flag')) {
        cellImg.src = '/static/images/unrevealed.png';
        flaggedCells[row][col] = false;
    } else if (cellImg.src.includes('unrevealed')) {
        cellImg.src = '/static/images/flag.png';
        flaggedCells[row][col] = true;
    }

    // Update flags counter
    document.getElementById('flagsUsed').textContent = 'Flags used: ' + countFlags(flaggedCells);
}

// Function to set max mines based on board size
function setMaxMines() {
    boardSize = parseInt(document.getElementById('boardSize').value);
    var maxMines = Math.floor(boardSize * boardSize - 10);
    var minesInput = document.getElementById('numMines');
    minesInput.setAttribute('max', maxMines);
}

// Function to count total flags used
function countFlags(flaggedCells) {
    return flaggedCells.reduce(function(sum, row) {
        return sum + row.reduce(function(sum, flagged) {
            return sum + (flagged ? 1 : 0);
        }, 0);
    }, 0);
}

// Add a CSS class to an element
function addCssClass(elem, cssClass) {
    var currentClass = elem.className;
    elem.className = currentClass ? currentClass + ' ' + cssClass : cssClass;
}
