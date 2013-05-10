var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var makeurl=function(node) {
	if (node.id=='0gen') {
	  return("http://www.gencat.cat/generalitat/cat/guia/estructura.htm");	
	} else {
	  return("http://www10.gencat.cat/sac/AppJava/organisme_fitxa.jsp?codi="+node.id);	
	}
}

var makeshort=function(txt) {
		txt=txt.replace(/Dept\. d(e la |'|e )/,"");
		txt=txt.replace(/Secr\. d(e la |'|e )/,"");		
		var s=txt.split(" ");
		if (s.length>3) {
			return (s[0]+" "+s[1]+ " " +s[2]+" "+s[3].substr(0,4)+"...");
		} else {
			return txt;
		}
}

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};


function init(){
    //init data
    var json = window.data;
    //end
    var infovis = document.getElementById('infovis');
    var w = infovis.offsetWidth - 50, h = infovis.offsetHeight - 50;
    
    //init Hypertree
    var ht = new $jit.Hypertree({
      //id of the visualization container
      injectInto: 'infovis',
      //canvas width and height
      width: w,
      height: h,
      //Change node and edge styles such as
      //color, width and dimensions.
      Node: {
          dim: 12,
          color: "#008"
      },
      Edge: {
          lineWidth: 2,
          color: "#088"
      },
      onBeforeCompute: function(node){
          Log.write("centrant");
      },
      Tips: {
        enable: true,
        type: 'HTML',
        offsetX: 10,
        offsetY: 10,
        onShow: function (tip, node)
        {
            tip.innerHTML = node.name+"<br/> Resp.:"+(node.data["item - resp"] ? node.data["item - resp"] : '-');
        }
	  },
      //Attach event handlers and add text to the
      //labels. This method is only triggered on label
      //creation
      onCreateLabel: function(domElement, node){
          domElement.innerHTML = makeshort(node.name);
          $jit.util.addEvent(domElement, 'click', function () {
              ht.onClick(node.id, {
                  onComplete: function() {
                      ht.controller.onComplete();
                  }
              });
          });
      },
      //Change node styles when labels are placed
      //or moved.
      onPlaceLabel: function(domElement, node){
          var style = domElement.style;
          style.display = '';
          style.cursor = 'pointer';
          if (node._depth <= 1) {
              style.fontSize = "0.9em";
              style.color = "#ddd";

          } else if(node._depth == 2){
              style.fontSize = "0.8em";
              style.color = "#555";

          } else {
              style.display = 'none';
          }

          var left = parseInt(style.left);
          var w = domElement.offsetWidth;
          style.left = (left - w / 2) + 'px';
      },
      
      onComplete: function(){
          Log.write("fes clic en un node per canviar la perspective");
          
          //Build the right column relations list.
          //This is done by collecting the information (stored in the data property) 
          //for all the nodes adjacent to the centered node.
          var node = ht.graph.getClosestNodeToOrigin("current");
          var html = '<h4><a target="_blank" href="'+makeurl(node)+'">' + node.name + "</a></h4><b>Relacions:</b>";
          html += "<ul>";
          node.eachAdjacency(function(adj){
              var child = adj.nodeTo;
              if (child.data) {
                  html += '<li><a target="_blank" href="'+makeurl(child)+ '">' + child.name + " " + "</a><div class=\"relation\">(resp.: " + (child.data["item - resp"] ? child.data["item - resp"] : "-") + ")</div></li>";
              }
          });
          html += "</ul>";
          $jit.id('inner-details').innerHTML = html;
      }
    });
    //load JSON data.
    ht.loadJSON(json);
    //compute positions and plot.
    ht.refresh();
    //end
    ht.controller.onComplete();
}
