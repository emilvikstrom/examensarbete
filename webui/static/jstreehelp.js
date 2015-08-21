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

				if( MIBclass === "module" ){
					getModule(MIBnode);
				}
				else if(MIBclass === "node"){
					var module = data.node.li_attr["data-root"];
					getNode(module, MIBnode);
				}
			
		});
	jQuery("#sendtemplate").click(function(){

		if(currentDataForTemplate != null){
			var templatename = jQuery("#templatename").val();
			console.log(templatename);
			var postData = {
				"templateName" : templatename,
				"nodes" : currentDataForTemplate
			};
			jQuery.post(
				'./template',
				JSON.stringify(postData),
				function(){
					console.log("Sent the message")
				}
			);
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
