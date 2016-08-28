// player object
var player = new Object();

player.send_command = function (command) {
    player.ws.send_command(command);
};

player.on_command = funciton () {

};



player.init = function () {
    player.ws = new WebSocket("ws://localhost:8888/websocket");
    player.ws.onopen = function() {
       player.send("join:{{joinGameId}}");
    };

    player.ws.onmessage = function (e) {
       player.on_command(e.data);
    };
};




// create the board
function create_board() {

}


function place_piece(argument) {
    
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