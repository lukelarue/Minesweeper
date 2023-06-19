// Global variables
var boardSize;
var numMines;
var isGameOver = false;
var flaggedCells = [];

function startGame() {
    isGameOver = false;
    boardSize = parseInt(document.getElementById('boardSize').value);
    numMines = document.getElementById('numMines').value;
    flaggedCells = Array(boardSize).fill().map(() => Array(boardSize).fill(false));
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
        // Generate game board in HTML
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

function makeMove(row, col) {
    if (isGameOver) {
        return;
    }
    if (flaggedCells[row][col]) {
        return; // If the cell is flagged, ignore the click
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
        // Update game board in HTML - board is redrawn
        for (var i = 0; i < boardSize; i++) {
            for (var j = 0; j < boardSize; j++) {
                var img = document.getElementById('cell'+i+'-'+j);
                var imgValue = data.board[i][j];
                if (flaggedCells[i][j]) {
                    img.setAttribute('src', '/static/images/flag.png');
                } else {
                    // check if imgValue is 9, if yes, use 'unrevealed' as image name
                    var imgName = imgValue === 9 ? 'unrevealed' : imgValue;
                    img.setAttribute('src', '/static/images/' + imgName + '.png');
                }
            }
        }

        document.getElementById('flagsUsed').textContent = 'Flags used: ' + countFlags(flaggedCells);
        
        var gameResult = document.getElementById('gameResult');
        gameResult.innerHTML = '';  // clear previous result message

        // Update the game status based on the "info" dictionary
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
                gameResult.innerText = '';  // for "continue", don't show any message
                break;
        }
        // Update the game over state based on the "info" dictionary
        if (data.info.result === 'win' || data.info.result === 'lose') {
            isGameOver = true;  // Set the game over state to true when a win or loss is detected
        }
    });
}

function flagCell(event, row, col) {
    event.preventDefault(); // Prevents the usual context menu from popping up
    var cellImg = document.getElementById('cell'+row+'-'+col);
    if (cellImg.src.includes('flag')) {
        cellImg.src = '/static/images/unrevealed.png';
        flaggedCells[row][col] = false;
    } else if (cellImg.src.includes('unrevealed')) {
        cellImg.src = '/static/images/flag.png';
        flaggedCells[row][col] = true;
    }
    document.getElementById('flagsUsed').textContent = 'Flags used: ' + countFlags(flaggedCells);
}


function setMaxMines() {
    boardSize = parseInt(document.getElementById('boardSize').value);
    var maxMines = Math.floor(boardSize * boardSize / 4);
    var minesInput = document.getElementById('numMines');
    minesInput.setAttribute('max', maxMines);
}

function countFlags(flaggedCells) {
    return flaggedCells.reduce(function(sum, row) {
        return sum + row.reduce(function(sum, flagged) {
            return sum + (flagged ? 1 : 0);
        }, 0);
    }, 0);
}


