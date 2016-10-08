// player object
var player = new Object();

function sendCmd() {
	var data = document.getElementsByName("cmddata")[0].value;
	var split = data.split(":");
	player.send_command(split[0], split[1]);
	return true;
}

player.send_command = function (command, data) {
    player.ws.send(command + ':' + data);
};

player.on_command = function (command_data) {
	document.getElementsByName("cmdinfo")[0].value += "\n"+command_data+"\n";
    command = command_data.split(':')[0];
    data = command_data.split(':')[1];

	if (command == "alert") {
		alert(data);
	} else if (command == "info") {
		alert(command_data);
	} else if (command == 'redraw') {
        redrawBoard(data);
    } else if (command == 'board') {
        redrawBoard(data);
    }
};


player.init = function () {
    player.ws = new WebSocket("ws://"+location.host+"/websocket");
    player.ws.onopen = function() {
		player.send_command("join", gameId);
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
    //if ()

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
    //create_board();
}