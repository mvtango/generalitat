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

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};

window.nodeindex={};

var makeshort=function(a) {
	a=a.replace(/Departament /,"D ",a);
	a=a.replace(/Secretaria General /,"SG ",a);
	a=a.replace(/Direcció General /,"DG ",a);
	a=a.replace(/Secretaria /,"S ",a);
	a=a.replace(/General /,"Gral. ",a);
	a=a.replace(/Generalitat de Catalunya /,"Generalitat ",a);
	a=a.replace(/Territorial del Govern de la Generalitat /,"",a);
	a=a.replace(/Govern de la Generalitat /,"Govern ",a);
	return(a);
}
	

function init(){
    //init data
    var json = window.data;
    //end
    //init Spacetree
    //Create a new ST instance
    var st = new $jit.ST({
        //id of viz container 
        injectInto: 'infovis',
        //set duration for the animation
        duration: 400,
        //set animation transition type
        transition: $jit.Trans.Quart.easeInOut,
        //set distance between node and its children
        levelDistance: 30,
        //enable panning
        Navigation: {
          enable:true,
          panning:false
        },
        //set node and edge styles
        //set overridable=true for styling individual
        //nodes or edges
        Node: {
            height: 24,
            width: 84,
            type: 'rectangle',
            color: '#aaa',
            overridable: true
        },
        
        Edge: {
            type: 'bezier',
            overridable: true
        },
        
        onBeforeCompute: function(node){
            Log.write("cargant " + node.name);
        },
        
        onAfterCompute: function(){
            Log.write("clic para canviar a perspectiva");
        },
		Tips: {
			enable: true,
			type: 'HTML',
			offsetX: 10,
			offsetY: 10,
			onShow: function (tip, node)
			{
				tip.innerHTML = node.name+"<br/>ID:"+node.data["id"] + "<br />Resp.:"+(node.data["resp"] ? node.data["resp"] : '-');
			}

		},
        //This method is called on DOM label creation.
        //Use this method to add event handlers and styles to
        //your node.
        onCreateLabel: function(label, node){
            label.id = node.id;            
            label.innerHTML = makeshort(node.name);
            label.onclick = function(){
            	//if(normal.checked) {
            	st.onClick(node.id);
            	make_info(node.id);
            	//} else {
                // st.setRoot(node.id, 'animate');
            	//}
            };
            //set label styles
            var style = label.style;
            style.width = 80 + 'px';
            style.height = 20 + 'px';            
            style.cursor = 'pointer';
            style.color = '#222';
            style.fontFamily = 'Tahoma, Arial, Sans';
            style.fontSize = '0.7em';
            style.textAlign= 'center';
            style.padding = '2px';
            // style.border ="1px solid #e0e0e0";
            style.overflow= 'hidden';
            //style.backgroundColor= '#f0f0f0';
        },
        
        //This method is called right before plotting
        //a node. It's useful for changing an individual node
        //style properties before plotting it.
        //The data properties prefixed with a dollar
        //sign will override the global node style properties.
        onBeforePlotNode: function(node){
            //add some color to the nodes in the path between the
            //root node and the selected node.
            window.nodeindex[node.id]=node;
            if (node.selected) {
                node.data.$color = "#ff7";
            }
            else {
                delete node.data.$color;
                //if the node belongs to the last plotted level
                if(!node.anySubnode("exist")) {
                    //count children number
                    var count = 0;
                    node.eachSubnode(function(n) { count++; });
                    //assign a node color based on
                    //how many children it has
                    if (count>1) {
						node.data.$color='#daa';
					} else {
						node.data.$color='#aaa';
					}
					 // node.data.$height=(1+count)*5;
                    //node.data.$color = ['#aaa', '#baa', '#caa', '#daa', '#eaa', '#faa','#aaa', '#baa', '#caa', '#daa', '#eaa', '#faa'][count];                    
                }
            }
        },
        
        //This method is called right before plotting
        //an edge. It's useful for changing an individual edge
        //style properties before plotting it.
        //Edge data proprties prefixed with a dollar sign will
        //override the Edge global style properties.
        onBeforePlotLine: function(adj){
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                adj.data.$color = "#eed";
                adj.data.$lineWidth = 3;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });
    //load json data
    st.loadJSON(json);
    //compute node positions and layout
    st.compute();
    //optional: make a translation of the tree
    st.geom.translate(new $jit.Complex(400, 0), "current");
    //emulate a click on the root node.
    st.onClick(st.root);
    window.st=st;
    //end
    //Add event handlers to switch spacetree orientation.
    //var top = $jit.id('r-top'), 
    //    left = $jit.id('r-left'), 
    //    bottom = $jit.id('r-bottom'), 
    //   right = $jit.id('r-right'),
    //    normal = $jit.id('s-normal');
        
    
    function changeHandler() {
        if(this.checked) {
            top.disabled = bottom.disabled = right.disabled = left.disabled = true;
            st.switchPosition(this.value, "animate", {
                onComplete: function(){
                    top.disabled = bottom.disabled = right.disabled = left.disabled = false;
                }
            });
        }
    };
    
    //top.onchange = left.onchange = bottom.onchange = right.onchange = changeHandler;
    //end

	window.make_info=function(nid) {
		$jit.id("info").innerHTML='<a target=_blank href="http://www10.gencat.cat/sac/AppJava/organisme_fitxa.jsp?codi='+nid+'">més informació</a> (#'+nid + ' en gencat.cat)';
	}
	
	window.go=function(a) {
		st.onClick(a);
		make_info(a);
	};
}
