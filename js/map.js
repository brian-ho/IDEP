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
	.style("position", "absolute")
	.style("z-index", "10")
	.style("visibility", "hidden");

  tooltip.append("p")
    .attr("id", "tool-id")
  	.text("123");
  tooltip.append("img")
    .attr("id", "tool-img")
  	.text("123");
  tooltip.append("p")
    .attr("id", "tool-text")
  	.text("a simple tooltip");

var callout = d3.select("#map-holder")
  .append("div")
	.style("position", "absolute")
	.style("z-index", "10")
  .style("visibility", "visible")
  .attr("id", "callout");

  callout.append("p")
    .attr("id", "callout-id")
  	.text("123");
  callout.append("img")
    .attr("id", "callout-img")
  	.text("123");
  callout.append("p")
    .attr("id", "callout-text")
  	.text("a simple tooltip");

// Load in geospatial data layers
// TODO consolidate to topoJSON
d3.queue()
  .defer(d3.json, "geo/circle_5km.geojson")
  // .defer(d3.json, "geo/circle_7_5km.geojson")
  // // .defer(d3.json, "geo/circle_10km.geojson")
  .defer(d3.json, "geo/circle_10km.geojson")
  // .defer(d3.json, "geo/hydro.geojson")
  .defer(d3.json, "geo/City_of_Boston_Boundary.json")
  // .defer(d3.json, "geo/district_bldg.geojson")
  // .defer(d3.json, "geo/edge_parcel.geojson")
  // .defer(d3.json, "geo/edges_buffer_1.geojson")
  .defer(d3.json, "geo/landmark_bldg.geojson")
  // .defer(d3.json, "geo/node_seg.geojson")
  .defer(d3.csv, "data/kl_geocode_2g.csv")
  .await(makeMyMap);

// Function to draw map
function makeMyMap(error, circle, circle2, boundary,landmark, kl){
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
  // Disable scrolling
  svg.call(zoom)
    .on("wheel", function() { d3.event.preventDefault(); });

  // Background listens for click events to reset view
  svg.append("rect")
    .attr("class", "background")
    .attr("width", width)
    .attr("height", height)
    .on("click", reset);

  // Group to hold geometry
  var g = svg.append('g')
    .attr("class", "geometry");

  // Geospatial layers drawn here
  // TODO consolidate, CSS attributes, fix draw order

  // g.selectAll(".boundary")
  //     .data(topojson.feature(boundary, boundary.objects.City_of_Boston_Boundary).features)
  //     .enter()
  //     .append("path")
  //     .attr("d", path)
  //     .attr("stroke-width", .125)
  //     .attr("stroke","white");

  g.selectAll(".circle")
      .data(circle.features)
      // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-width", .125);

  // g.selectAll(".hydro")
  //     .data(hydro.features)
  //     // .data(topojson.feature(hydro, hydro.objects.hydro_20km_dissolve).features)
  //     .enter()
  //     .append("path")
  //     .attr("d", path)
  //     // .attr("fill", "grey")
  //     .attr("stroke", "white")
  //     .attr("stroke-width", .125);
  //
  // g.selectAll(".districts")
  //     .data(districts.features)
  //     // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
  //     .enter()
  //     .append("path")
  //     .attr("d", path)
  //     .attr("opacity", 0.3)
  //     .attr("fill", "white")
  //     .attr("stroke", "none");

  // g.selectAll(".edges")
  //     .data(edges.features)
  //     // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
  //     .enter()
  //     .append("path")
  //     .attr("d", path)
  //     .attr("opacity", 0.3)
  //     .attr("stroke-width", 6)
  //     .attr("fill", "white");

  g.selectAll(".landmarks")
      .data(landmark.features)
      // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("opacity", .9)
      .attr("stroke-width", 6)
      .attr("fill", "white");

  // g.selectAll(".nodes")
  //     .data(nodes.features)
  //     // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
  //     .enter()
  //     .append("path")
  //     .attr("d", path)
  //     .attr("opacity", 1)
  //     .attr("stroke-width", .5)
  //     .attr("stroke", "white")
  //     .attr("fill", "none");

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
        d3.select("#tool-text").text(d.text);
      })

      .on("mousemove", function(){return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
      .on("mouseout", function(){return tooltip.style("visibility", "hidden");});

// Animation implementation
var n = Object.keys(kl).length;
var i = -1;

function animate() {
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
      .attr("fill", "red")
      .attr("r", 2)
      .attr("opacity", .5)
      .attr("cx", highlight_data.attr("cx"))
      .attr("cy", highlight_data.attr("cy"))
      .transition()
      .duration(2500)
      .attr("r", 100)
      .on("start", function(){
        console.log((highlight_data.attr("cy") - height)/4 + "px");
        return
        callout.style("top", (highlight_data.attr("cy") - height)/4 + "px")
          .style("left", (highlight_data.attr("cx") - width)/4 + "px");})
      .on("end", animate);
  };

// Call animate to set it off!
animate();

// Reset zoom and extents
function reset() {
  console.log("clicked!");
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
}
