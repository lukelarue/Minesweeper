function displayBoard(board) {
    var boardString = board.map(row => row.join(' ')).join('\n');
    document.getElementById('board').textContent = boardString;
}

var gameId;

document.getElementById('start').addEventListener('click', function() {
    fetch('/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ length: 10, mines: 10 })
    })
    .then(response => response.json())
    .then(data => {
        gameId = data.game_id;
        displayBoard(data.board);
        var totalTiles = data.board.length * data.board[0].length;
        document.getElementById('move-input').max = totalTiles - 1;
    });
});

document.getElementById('move-form').addEventListener('submit', function(e) {
    e.preventDefault(); 
    var move = +document.getElementById('move-input').value;
    fetch('/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_id: gameId, move: move })
    })
    .then(response => response.json())
    .then(data => {
        displayBoard(data);
    });
});
