window.onload = function(){
var width =800;
var height = 800;
var gridWidth = 16;
var gridHeight = 24;

var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");
canvas.addEventListener('click', handleClick);
    function handleClick(e) {
		ctx.fillStyle = "black";
      
        ctx.fillRect(Math.floor(e.offsetX/(width/gridWidth))*(width/gridWidth), 
                   Math.floor(e.offsetY/(height/gridHeight))*(height/gridHeight),
                  (width/gridWidth), (height/gridHeight));
        console.log(e.offsetX);
        console.log(e.offsetY);
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