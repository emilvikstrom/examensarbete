
//Function for retrieving a module
var getModule = function(module){
	jQuery.getJSON( "http://172.20.32.192:8080/modules/" + module, function(data){
		var items = [];
		jQuery.each( data, function(key, val) {
//			items.push("<li id='" + key + "'>" + key + "</li>" );
//			if(key === "module"){
//				console.log("Found key")
//				jQuery("#datatable tr:last" ).after(
//					"<tr><td>modulename</td><td>"+val+"</td></tr>"
//				);
//			}
		});
	
		jQuery("<ul/>", {
			"class": "my-new-list",
			html: items.join( "" )
		}).appendTo("body" );
	});
}

var getNode = function(module, node){
	//Clears table
	jQuery("#datatable").empty()
	jQuery.getJSON( "http://172.20.32.192:8080/nodes/" + module + "/" + node, function(data){
		var items = [];
		items.push("<table border='1'>");
		jQuery.each( data, function(key, val) {
			//TODO this should be a val instanceof Object check instead to generalize all objects
			//push key is right..
			//something like 
			//push col key
			//push objectprinter

			if(val instanceof Object){

				items.push("<td>" + key + "</td>" + objectPrinter(val) );

			}else{
				items.push( "<tr><td>" + key + "</td><td>" + val + "</td></tr>" );
			}
		});
		items.push("</table>");
		jQuery("#datatable").append(items.join( "" ));	

	});
}

/*
 * TODO
 * Create an object printer that puts all objects as tables inside a field
 * Thats is what creates bugs right now
 *
 * NOTE Think it's done 
 */


var objectPrinter = function(obj){
	var retArr = [];
	retArr.push("<td><table border='1'><tr>");

	//Code goes here
	jQuery.each( obj, function(key, val){
		if( val instanceof Object){
			retArr.push("<td>" + key + "</td>" + objectPrinter(val) );
		}else{
			retArr.push("<td>" + key + "</td><td>" + val + "</td>");
		}
	});

	retArr.push("</tr></table></td>");
	return retArr.join( "" );
}

