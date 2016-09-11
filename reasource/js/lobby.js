window.onload = function() {
	var value = 0;
	
	function onRowClick(tableId, callback) {
		var table = document.getElementById(tableId),
			rows = table.getElementsByTagName("tr"),
			i;
		for (i = 1; i < rows.length; i++) {
			table.rows[i].onclick = function (row) {
				return function () {
					callback(row);
				};
			}(table.rows[i]);
		}
	};
 
	onRowClick("games", function (row) {
		var rows = document.getElementById("games").getElementsByTagName("tr"), i;
		for (i = 1; i < rows.length; i++) {
			rows[i].style.backgroundColor = "";
		}
		row.style.backgroundColor = "#55BBFF";
		join.classList = "btn btn-lg btn-success";
		value = row.getElementsByTagName("td")[0].innerHTML;
	});
	
	var join = document.getElementById("join");
	join.addEventListener('click', handleClick);
	
	function handleClick() {
		if (value > 0) {
			window.location = "game?gameid="+value;
		}
	}
}

