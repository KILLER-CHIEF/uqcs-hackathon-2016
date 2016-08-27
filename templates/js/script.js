window.onload = function(){
var width =800;
var height = 800;

var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");
canvas.addEventListener('click', handleClick);
    function handleClick(e) {
		ctx.fillStyle = "black";
      
        ctx.fillRect(Math.floor(e.offsetX/180)*200, 
                   Math.floor(e.offsetY/180)*200,
                   200, 200);
	}
function drawBoard(){
for (var x = 0; x <= width; x += 200) {
    ctx.moveTo(x,0);
    ctx.lineTo( x, height);
}


for (var x = 0; x <= height; x += 200) {
    ctx.moveTo(0, x);
    ctx.lineTo(width,x);
}

ctx.strokeStyle = "black";
ctx.stroke();
}

drawBoard();
}