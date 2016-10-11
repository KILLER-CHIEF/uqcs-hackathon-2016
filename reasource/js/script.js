// player object
var player = new Object();

var playerSymbol = undefined;

function sendCmd() {
	var raw_data = document.getElementsByName("cmddata")[0].value;
	var firstColonIndex = raw_data.indexOf(':')
    var command = raw_data.substring(0, firstColonIndex);
    var data = raw_data.substring(firstColonIndex+1);
	player.send_command(command, data);
	return true;
}

player.send_command = function (command, data = "") {
    player.ws.send(command + ':' + data);
};

function addChat(text) {
	document.getElementById("chatbox").value += text + "\n";
}

player.on_command = function (command_data) {
	var firstColonIndex = command_data.indexOf(':')
    var command = command_data.substring(0, firstColonIndex);
    var data = command_data.substring(firstColonIndex+1);

	if (command == "alert") {
		alert(data);
	} else if (command == "info") {
		//alert(command_data);
		document.getElementById("info").value = data;
	} else if (command == 'youare') {
        playerSymbol = data;
    } else if (command == 'joiner') {
        addChat(">Player "+data+" has joined the game!");
    } else if (command == 'lost') {
		var row = document.getElementById("player"+data);
        row.style.backgroundColor = "#FF0000";
		getCellOfTypeInRow(row, "A").innerHTML = "D";
    } else if (command == 'gamelog') {
        addChat(">"+data);
    } else if (command == 'chat') {
        addChat(data);
    } else if (command == 'players') {
        redrawPlayers(data);
    } else if (command == "joinend") {
		document.getElementById("info").value = data;
	} else if (command == 'redraw') {
        redrawBoard(data);
    } else if (command == 'board') {
        redrawBoard(data);
    } else if (command == 'uhost') {
		alert(data);
        unlockLobbyControls();
	} else if (command == 'gamebegin') {
		addChat(">The game has now begun!");
		document.getElementById("status").innerHTML = "In-Game";
		document.getElementById("btnStartGame").style.display = "none";
		//TODO: Set Status to ingame.
		//enable things
    } else if (command == 'invalidmove') {
		document.getElementById("info").value = "Invalid Move!";
		player.send_command("board");
    } else if (command == 'turn') {
		var playerRows = document.getElementById("players").getElementsByTagName("tr");
		for (var i = 0; i < playerRows.length; i++) {
			var cellA = getCellOfTypeInRow(playerRows[i], "A");
			if (cellA.innerHTML.includes("&gt;")) {
				cellA.innerHTML = cellA.innerHTML.replace("&gt;", "");
				cellA.style.backgroundColor = "";
			}
		}
		var row = document.getElementById("player"+data);
		var cellA = getCellOfTypeInRow(row, "A");
		cellA.innerHTML = ">";
		cellA.style.backgroundColor = "#00FF00";
		if (data == playerSymbol) {
			document.getElementById("info").value = "Your Turn.";
			document.getElementById("btnPlaceStone").style.display = "";
		} else {
			document.getElementById("info").value = "Player "+data+"'s Turn.";
			document.getElementById("btnPlaceStone").style.display = "none";
		}
	} else if (command == 'gameover') {
		document.getElementById("info").value = "Player "+data+" has won the game!";
		document.getElementById("status").innerHTML = "Post-Game";
		//TODO: Set Status to game over.
		//disable things.
    } else if (command == 'state') {
		document.getElementById("status").innerHTML = data.split(",")[1];
    } else {
		document.getElementsByName("cmdinfo")[0].value += ">>>";
	}
	document.getElementsByName("cmdinfo")[0].value += command_data+"\n";
};


player.init = function () {
	//location.host
    player.ws = new WebSocket("ws://"+websocketHostAddr+"/websocket");
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

window.onload = function(){
    //create_board();
}