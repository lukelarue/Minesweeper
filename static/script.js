function makeMove(row, col) {
    var action = row * 8 + col; // Assuming 8x8 board
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        // Update game board
        for (var i = 0; i < 8; i++) { // Assuming 8x8 board
            for (var j = 0; j < 8; j++) {
                document.getElementById('gameBoard').rows[i].cells[j].innerHTML =
                    '<img src="' + data.board[i][j] + '.png">';
            }
        }
    });
}
