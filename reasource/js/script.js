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
    } else if (command == 'create') {
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
var width =800;
var height = 800;
var gridWidth = 8;
var gridHeight = 16;

var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");
canvas.addEventListener('click', handleClick);
    function handleClick(e) {
        ctx.font="50px Verdana";
		ctx.fillText("A",Math.floor(e.offsetX/(width/gridWidth))*(width/gridWidth),(Math.floor(e.offsetY/(height/gridHeight))*(height/gridHeight))+(height/gridHeight),(width/gridWidth));
      
        //ctx.fillRect(Math.floor(e.offsetX/(width/gridWidth))*(width/gridWidth), 
                  // Math.floor(e.offsetY/(height/gridHeight))*(height/gridHeight),
                  //(width/gridWidth), (height/gridHeight));
        console.log(Math.floor(e.offsetX/(width/gridWidth)));
        console.log(Math.floor(e.offsetY/(height/gridHeight)));
        //console.log(e.offsetY);
	}
function drawBoard(){
for (var x = 0; x <= width; x += (width/gridWidth)) {
    ctx.moveTo(x,0);
    ctx.lineTo( x, height);
}


for (var x = 0; x <= height; x += (height/gridHeight)) {
    ctx.moveTo(0, x);
    ctx.lineTo(width,x);
}

ctx.strokeStyle = "black";
ctx.stroke();
}

drawBoard();
}