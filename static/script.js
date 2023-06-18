// Global variables boardSize and numMines
var boardSize;
var numMines;

function startGame() {
    boardSize = document.getElementById('boardSize').value;
    numMines = document.getElementById('numMines').value;
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
        // Update game board in HTML
        for (var i = 0; i < boardSize; i++) {
            for (var j = 0; j < boardSize; j++) {
                var img = document.getElementById('cell'+i+'-'+j);
                var imgValue = data.board[i][j];
                // check if imgValue is 9, if yes, use 'unrevealed' as image name
                var imgName = imgValue === 9 ? 'unrevealed' : imgValue;
                img.setAttribute('src', '/static/images/' + imgName + '.png');
            }
        }

        // Check if game is done
        if (data.done) {
            if (data.reward > 0) {
                alert('You won!');
            } else {
                alert('You lost!');
            }
        }
    });
}

function setMaxMines() {
    boardSize = document.getElementById('boardSize').value;
    var maxMines = Math.floor(boardSize * boardSize / 4);
    var minesInput = document.getElementById('numMines');
    minesInput.setAttribute('max', maxMines);
}

