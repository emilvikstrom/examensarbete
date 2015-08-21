jQuery(function(){
		var currentDataForTemplate = null;

		jQuery("#jstree")
			.jstree(
				{

				"checkbox": {
					"visible" : true,
					"whole_node" : false,
					"three_state" : true 

				},
				"plugins" : ["wholerow","checkbox" ]
			}).on("changed.jstree", function(e, data){
				var MIBnode = data.node.id;
				var MIBclass = data.node.li_attr.class;
				var selct = jQuery('#jstree').jstree('get_selected');
				var selectedLeafs = getLeafsFromSelected(data, data.selected);
				
				currentDataForTemplate = assembleJSON(selectedLeafs);
				
				//Making JSONString
				var jsonString = JSON.stringify(currentDataForTemplate);
				console.log(jsonString);
				//Setting hidden field to the string
				jQuery("#dataField").val(jsonString);
				var hiddenString = jQuery("#dataField").val();
				console.log(hiddenString);

				if( MIBclass === "module" ){
					getModule(MIBnode);
				}
				else if(MIBclass === "node"){
					var module = data.node.li_attr["data-root"];
					getNode(module, MIBnode);
				}
			
		});

});

var assembleJSON = function(listOfLeafs){
	if ( listOfLeafs instanceof Array ){
		var JSONarr = [];
		jQuery.each(listOfLeafs, function( index, nodename ){
			var nodeInfo = getNodeInfo(nodename);
			var moduleName = nodeInfo.li_attr["data-root"];
			var tmpDict = {
				"moduleName" : moduleName,
				"node" : nodename
			};
			JSONarr.push(tmpDict);
		});
		return JSONarr;
	}
	return null;
}

var getNodeInfo = function(nodeName){
	return jQuery.jstree.reference("#jstree").get_node(nodeName);
}

var getLeafsFromSelected = function(data, selected){
	if( selected instanceof Array ){
		var leafNodes = [];
		jQuery.each(selected, function( index, value){
			if(data.instance.is_leaf(value)){
				leafNodes.push(value);
			}
		});
		return leafNodes;
	}
	return null;
}
