// Get page dimensions
var width = $("#map-holder").width();
var height = $("#map-holder").height();
var margin = 100; // Set for projector (offset from edge)

// Create a canvas, same as div
var svg = d3.select("#map-holder")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

// Create a tooltip
var tooltip = d3.select("#map-holder")
	.append("div")
	.style("z-index", "10")
	.style("visibility", "hidden")
  .style("position", "absolute");

  tooltip.append("p")
    .attr("id", "tool-id")
  	.text("123");
  tooltip.append("img")
    .attr("id", "tool-img");
  tooltip.append("p")
    .attr("id", "tool-text")
  	.text("a simple tooltip");

var callout = d3.select("#map-holder")
  .append("div")
	.style("z-index", "10")
  .style("visibility", "visible")
  .attr("id", "callout")
  .style("position", "absolute");

  callout.append("p")
    .attr("id", "callout-id")
  	.text("123");
  callout.append("img")
    .attr("id", "callout-img");
  callout.append("p")
    .attr("id", "callout-text")
  	.text("a simple tooltip");

var g;

// Load in geospatial data layers
// TODO consolidate to topoJSON
d3.queue()
  .defer(d3.json, "geo/circle_5km.geojson")
  .defer(d3.json, "geo/hydro.geojson")
  .defer(d3.json, "geo/KLelements.json")
  .defer(d3.csv, "data/kl_geocode_2h.csv")
  .await(makeMyMap);

// Function to draw map
function makeMyMap(error, circle, hydro, elements, kl){
  if (error) throw error;

    // Set projection to NAD83 Massachusetts Mainalnd (EPSG:26986)
  var projection = d3.geoConicConformal()
    .parallels([41 + 43 / 60, 42 + 41 / 60])
    .rotate([71 + 30 / 60, -41])
    .fitExtent([[margin, margin],[width-margin,height-margin]], circle); // Center for projector

  // Set up path and zoom
  var path = d3.geoPath().projection(projection);
  var zoom = d3.zoom()
      .scaleExtent([.75, 15]) // This is a relative zoom level (go figure)
      .on("zoom", zoomed);

  console.log(projection.scale(), projection.center());

  // Disable scrolling throughout!
  d3.select("body").call(zoom)
    .on("wheel", function() { d3.event.preventDefault(); });

  // Background listens for click events to reset view
  svg.append("rect")
    .attr("class", "background")
    .attr("width", width)
    .attr("height", height)
    .on("click", reset);

  // Group to hold geometry
  g = svg.append('g')
    .attr("class", "geometry");

  // Geospatial layers drawn here
  // TODO consolidate, CSS attributes, fix draw order
  var circleBounds = g.selectAll(".circle")
      .data(circle.features)
      // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", "none")
      .attr("stroke", "none");

  // Background diagram
  // TODO Re-export proper background with correct origin to avoid manual scaling
  // var circleX = (circleBounds.node().getBBox().width)*.47;
  // var circleY = (circleBounds.node().getBBox().height)*.47;

  // var sketch = g.append("image")
  //     .attr("id", "sketch")
  //     .attr("width",  circleX + "px")
  //     .attr("height", circleY + "px")
  //     .attr("x", (width/2)-(circleX/1.535))
  //     .attr("y", (height/2)-(circleY/3.6))
  //     .attr("xlink:href", "geo/city_image.png");

g.selectAll(".hydro")
      .data(hydro.features)
      // .data(topojson.feature(hydro, hydro.objects.hydro_20km_dissolve).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", "black")
      .attr("stroke", "white")
      .attr("stroke-width", .25);

  g.selectAll(".paths")
      .data(topojson.feature(elements, elements.objects.KLpaths).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("class", "paths")
      .attr("stroke", "white")
      .attr("fill", "none")
      .attr("stroke-width", .5);

  g.selectAll(".nodes")
      .data(topojson.feature(elements, elements.objects.KLnodes).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("class", "nodes")
      .attr("opacity", 0.5)
      .attr("fill", "#222")
      .on("mouseover", function(d){
        console.log(d);
        tooltip.style("visibility", "visible")
        d3.select("#tool-id").text(d.properties.text)
        d3.select("#tool-text").text('');})
      .on("mousemove", function(){
        tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
      .on("mouseout", function(){;
        tooltip.style("visibility", "hidden");});

  g.selectAll(".districts")
      .data(topojson.feature(elements, elements.objects.KLdistricts).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", "grey ");
      // .attr("stroke", "black")
      // .attr("stroke-width", .25);

  g.selectAll(".landmarks")
      .data(topojson.feature(elements, elements.objects.KLlandmarks).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("class", "landmarks")
      .attr("fill", "white")
      .on("mouseover", function(d){
        console.log(d);
        tooltip.style("visibility", "visible")
        d3.select("#tool-id").text(d.properties.text)
        d3.select("#tool-text").text('');})
      .on("mousemove", function(){
        tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
      .on("mouseout", function(){
        tooltip.style("visibility", "hidden");});

  g.selectAll(".edges")
      .data(topojson.feature(elements, elements.objects.KLedges).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("class", "edges")
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-width", 1);

  g.selectAll(".dots")
      .data(kl)
      .enter()
      .append("circle")
      .attr("class", "dots")
      .attr("r", 2)
      .attr("cx", function(d) {return projection([d.lng0, d.lat0])[0]} )
      .attr("cy", function(d) {return projection([d.lng0, d.lat0])[1]} )
      .attr("fill","cyan")
      .on("mouseover", function(d){
        console.log(d.id);
        tooltip.style("visibility", "visible")
        d3.select("#tool-img").attr("src", "images/"+d.id+".jpg");
        d3.select("#tool-id").text(d.id);
        d3.select("#tool-text").text(d.text);})
      .on("mousemove", function(){return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
      .on("mouseout", function(){tooltip.style("visibility", "hidden");});


  // Reset zoom and extents
  function reset() {
    console.log("reset!");
    // active.classed("active", false);
    // active = d3.select(null);
    svg.transition()
        .duration(750)
        .call( zoom.transform, d3.zoomIdentity ); // updated for d3 v4
      }

  // Zoom control
  function zoomed() {
    g.style("stroke-width", 1.5 / d3.event.transform.k + "px");
    g.attr("transform", d3.event.transform);
    d3.selectAll(".dots")
      .attr("r", 2 / d3.event.transform.k + "px");
      // updated for d3 v4
    }


    // Call animate to set it off!
    animate();
};
// Animation implementation
// var n = Object.keys(kl).length;
var n = 1909;
var i = -1;
var toggle_state = true;

function animate() {
  if (toggle_state) {
  i = (i + 101) % n;
    // Delete previous highlight
    g.selectAll(".highlight")
      .transition()
      .duration(2500)
      .attr("r",2)
      .on("end", function() {this.remove()})

    // d3.selectAll('.dots').filter(function(d, j) { return j!=i; })
    //   .transition()
    //   .duration(2500)
    //   .attr("fill", "cyan")
    //   .attr("r", 1)
    //   .delay(1000);
    //   // .style("z-index", -1);

    // Filter returns data to be highlighted
    var highlight_data = d3.selectAll('.dots').filter(function(d, j) { return j==i; });

    // Create highlight geometry
    g.append("circle")
      .attr("class", "highlight")
      .attr("r", 2)
      .attr("opacity", .5)
      .attr("stroke", "cyan")
      .attr("fill", "none")
      .attr("cx", highlight_data.attr("cx"))
      .attr("cy", highlight_data.attr("cy"))
      .transition()
      .duration(2500)
      .attr("r", 100)
      .on("start", function(){
        callout.style("top", ((highlight_data.attr("cy") - (height/2))+height/2 + "px"))
          .style("left", ((highlight_data.attr("cx") - (width/2))+width/2 + "px"))
          .style("visibilty", "visible");
        d3.select("#callout-img").attr("src", "images/"+highlight_data.datum().id+".jpg");
        d3.select("#callout-id").text(highlight_data.datum().id);
        d3.select("#callout-text").text(highlight_data.datum().text);
          ;})
      .on("end", animate);
      }
      else {
        // Delete previous highlight
        g.selectAll(".highlight")
          .transition()
          .duration(2500)
          .attr("r",2)
          .on("end", function() {this.remove(); callout.style("visibility", "hidden")});
    };
  }

$(document).ready(function() {
  $("#toggle").change(function() {
        toggle_state = (toggle_state ? false : true);
        console.log('TOGGLE '+toggle_state);
        if (toggle_state){ animate(); }
  });
});
