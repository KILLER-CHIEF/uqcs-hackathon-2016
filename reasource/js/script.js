// player object
var player = new Object();

player.send_command = function (command, data) {
    player.ws.send(command + ':' + data);
};

player.on_command = function (command_data) {
    command = command_data.split(':')[0];
    data = command_data.split(':')[1];

    if (command == 'redraw') {
        redraw_board(data);
    } else if (command == 'board') {
        create_board(data);
    } 
};


player.init = function () {
    player.ws = new WebSocket("ws://localhost:8888/websocket");
    player.ws.onopen = function() {
       player.send_command("join","{{joinGameId}}");
    };

    player.ws.onmessage = function (e) {
       player.on_command(e.data);
    };
};




// create the board
function create_board(data) {
    var board_data = data.split(',');
    var width = board_data[0];
    var height = board_data[1];
    var board_content = board_data[2];
    var board = $('#board');

    // handle table deconstruction
    if ()

    var table = $('table');
    table.attr('id', 'game-table');
    for (var i = 0 - 1; i <= height; i++) {
        var tr = $('tr');
        table.add(tr);
        for (var j = 0 - 1; j <= width; i++) {
            var td = $('td')
            tr.add(td);
            td.text(board_content[i*width+j]);
            td.attr("id","row"+i+"col"+j);
            
        }
        
    }
    board.add(table);
}


function place_piece(x, y) {
    player.send_command("move", x.toString() + ' ' + y.toString());
    player.send_command("get_board", "");
}

function redraw_board(board) {
    // use the "x  o\nxoo \n" to redraw the board
}

// return the board 
/* eg of return

"x  o\nxoo \n"



*/
function get_board() {

}


window.onload = function(){
<<<<<<< HEAD
    create_board();
=======
>>>>>>> d80f413e036c5651562e489c60d0dfb42f442798

}