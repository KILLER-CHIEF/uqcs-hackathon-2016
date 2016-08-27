window.onload = function(){

    function onRowClick(tableId, callback) {
    var table = document.getElementById(tableId),
        rows = table.getElementsByTagName("tr"),
        i;
    for (i = 0; i < rows.length; i++) {
        table.rows[i].onclick = function (row) {
            return function () {
                callback(row);
            };
        }(table.rows[i]);
    }
};
 
onRowClick("games", function (row){
    var value = row.getElementsByTagName("td")[0].innerHTML;
    //document.getElementById('click-response').innerHTML = value + " clicked!";
    console.log("value>>", value);
});
    
}

