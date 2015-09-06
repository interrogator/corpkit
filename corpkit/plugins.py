import mpld3
import collections
from mpld3 import plugins, utils

class HighlightLines(plugins.PluginBase):

    """A plugin to highlight lines on hover"""
    JAVASCRIPT = """
    mpld3.register_plugin("linehighlight", LineHighlightPlugin);
    LineHighlightPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    LineHighlightPlugin.prototype.constructor = LineHighlightPlugin;
    LineHighlightPlugin.prototype.requiredProps = ["line_ids"];
    LineHighlightPlugin.prototype.defaultProps = {alpha_bg:0.0, alpha_fg:1.0}
    function LineHighlightPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };
    LineHighlightPlugin.prototype.draw = function(){
      for(var i=0; i<this.props.line_ids.length; i++){
         var obj = mpld3.get_element(this.props.line_ids[i], this.fig),
             alpha_fg = this.props.alpha_fg;
             alpha_bg = this.props.alpha_bg;
         obj.elements()
             .on("mouseover.highlight", function(d, i){
                            d3.select(this).transition().duration(50)
                              .style("stroke-opacity", alpha_fg); })
             .on("mouseout.highlight", function(d, i){
                            d3.select(this).transition().duration(200)
                              .style("stroke-opacity", alpha_bg); });
      }
    };
    """
    def __init__(self, lines):
        self.lines = lines
        self.dict_ = {"type": "linehighlight",
                      "line_ids": [utils.get_id(line) for line in lines],
                      "alpha_bg": lines[0].get_alpha(),
                      "alpha_fg": 1.0}
import mpld3
from mpld3 import plugins, utils
import collections

class InteractiveLegendPlugin(plugins.PluginBase):
    """A plugin for an interactive legends. 
    
    Inspired by http://bl.ocks.org/simzou/6439398
    
    Parameters
    ----------
    plot_elements : iterable of matplotliblib elements
        the elements to associate with a given legend items
    labels : iterable of strings
        The labels for each legend element
    css : str, optional
        css to be included, for styling if desired
    ax :  matplotlib axes instance, optional
        the ax to which the legend belongs. Default is the first
        axes
    alpha_sel : float, optional
        the alpha value to apply to the plot_element(s) associated 
        with the legend item when the legend item is selected. 
        Default is 1.0
    alpha_unsel : float, optional
        the alpha value to apply to the plot_element(s) associated 
        with the legend item when the legend item is unselected. 
        Default is 0.2
        
    Examples
    --------
    
    """
    
    JAVASCRIPT = """
    mpld3.register_plugin("interactive_legend", InteractiveLegend);
    InteractiveLegend.prototype = Object.create(mpld3.Plugin.prototype);
    InteractiveLegend.prototype.constructor = InteractiveLegend;
    InteractiveLegend.prototype.requiredProps = ["element_ids", "labels"];
    InteractiveLegend.prototype.defaultProps = {"ax":null, 
                                                "alpha_sel":1.0,
                                                "alpha_unsel":0}
    function InteractiveLegend(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    InteractiveLegend.prototype.draw = function(){
        console.log(this)
        var alpha_sel = this.props.alpha_sel
        var alpha_unsel = this.props.alpha_unsel
    
        var legendItems = new Array();
        for(var i=0; i<this.props.labels.length; i++){
            var obj = {}
            obj.label = this.props.labels[i]
            
            var element_id = this.props.element_ids[i]
            mpld3_elements = []
            for(var j=0; j<element_id.length; j++){
                var mpld3_element = mpld3.get_element(element_id[j], this.fig)
                mpld3_elements.push(mpld3_element)
            }
            
            obj.mpld3_elements = mpld3_elements
            obj.visible = false; // must be setable from python side
            legendItems.push(obj);
        }
        console.log(legendItems)
        
        // determine the axes with which this legend is associated
        var ax = this.props.ax
        if(!ax){
            ax = this.fig.axes[0]
        } else{
            ax = mpld3.get_element(ax, this.fig);
        }
        
        // add a legend group to the canvas of the figure
        var legend = this.fig.canvas.append("svg:g")
                               .attr("class", "legend");
        
        // add the rectangles
        legend.selectAll("rect")
                .data(legendItems)
             .enter().append("rect")
                .attr("height",10)
                .attr("width", 25)
                .attr("x",ax.width+10+ax.position[0])
                .attr("y",function(d,i) {
                            return ax.position[1]+ i * 25 - 10;})
                .attr("stroke", get_color)
                .attr("class", "legend-box")
                .style("fill", function(d, i) {
                            return d.visible ? get_color(d) : "white";}) 
                .on("click", click)
        
        // add the labels
        legend.selectAll("text")
                .data(legendItems)
            .enter().append("text")
              .attr("x", function (d) {
                            return ax.width+10+ax.position[0] + 40})
              .attr("y", function(d,i) { 
                            return ax.position[1]+ i * 25})
              .text(function(d) { return d.label })
        
        // specify the action on click
        function click(d,i){
            d.visible = !d.visible;
            d3.select(this)
              .style("fill",function(d, i) {
                return d.visible ? get_color(d) : "white";
              })
              
            for(var i=0; i<d.mpld3_elements.length; i++){
            
                var type = d.mpld3_elements[i].constructor.name
                if(type =="mpld3_Line"){
                    d3.select(d.mpld3_elements[i].path[0][0])
                        .style("stroke-opacity", 
                                d.visible ? alpha_sel : alpha_unsel);
                } else if(type=="mpld3_PathCollection"){
                    d3.selectAll(d.mpld3_elements[i].pathsobj[0])
                        .style("stroke-opacity", 
                                d.visible ? alpha_sel : alpha_unsel)
                        .style("fill-opacity", 
                                d.visible ? alpha_sel : alpha_unsel);
                } else{
                    console.log(type + " not yet supported")
                }
            }
        };
        
        // helper function for determining the color of the rectangles
        function get_color(d){
            var type = d.mpld3_elements[0].constructor.name
            var color = "black";
            if(type =="mpld3_Line"){
                color = d.mpld3_elements[0].props.edgecolor;
            } else if(type=="mpld3_PathCollection"){
                color = d.mpld3_elements[0].props.facecolors[0];
            } else{
                console.log(type + " not yet supported")
            }
            return color
        };
    };
    """

    css_ = """
    .legend-box {
      cursor: pointer;  
    }
    """
    
    def __init__(self, plot_elements, labels, ax=None,
                 alpha_sel=1,alpha_unsel=0.2):
        
        self.ax = ax
        
        if ax:
            ax = utils.get_id(ax)
        
        mpld3_element_ids = self._determine_mpld3ids(plot_elements)
        self.mpld3_element_ids = mpld3_element_ids
        
        self.dict_ = {"type": "interactive_legend",
                      "element_ids": mpld3_element_ids,
                      "labels":labels,
                      "ax":ax,
                      "alpha_sel":alpha_sel,
                      "alpha_unsel":alpha_unsel}
    
    def _determine_mpld3ids(self, plot_elements):
        """
        Helper function to get the mpld3_id for each
        of the specified elements.
        
        This is a convenience function. You can
        now do:
        
        lines = ax.plot(x,y)
        plugins.connect(fig, HighlightLines(lines, labels))
        
        rather than first having to wrap each entry in
        lines in a seperate list.
        
        """


        mpld3_element_ids = []
    
        for entry in plot_elements:
            if isinstance(entry, collections.Iterable):
                mpld3_element_ids.append([utils.get_id(element) for element in entry])
            else:   
                mpld3_element_ids.append([utils.get_id(entry)])

        return mpld3_element_ids