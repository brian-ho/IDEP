var width = $("#map-holder").width();
var height = $("#map-holder").height();
var svg = d3.select("#map-holder")
  .append("svg")
  // set to the same size as the "map-holder" div
  .attr("width", width)
  .attr("height", height);

var tooltip = d3.select("#map-holder")
	.append("div")
	.style("position", "absolute")
	.style("z-index", "10")
	.style("visibility", "hidden")
	.text("a simple tooltip");

d3.queue()
  .defer(d3.json, "geo/circle_5km.geojson")
  // .defer(d3.json, "geo/circle_7_5km.geojson")
  // // .defer(d3.json, "geo/circle_10km.geojson")
  .defer(d3.json, "geo/circle_15km.geojson")
  .defer(d3.json, "geo/hydro.geojson")
  .defer(d3.json, "geo/City_of_Boston_Boundary.json")
  .defer(d3.csv, "data/kl_geocode_2g.csv")
  .await(makeMyMap);


// d3.json("geo/City_of_Boston_Boundary.geojson", function(error, data) {
function makeMyMap(error, circle, circle2, hydro, boundary, kl){
  if (error) throw error;

  // NAD83 Massachusetts Mainalnd (EPSG:26986)
  var projection = d3.geoConicConformal()
    .parallels([41 + 43 / 60, 42 + 41 / 60])
    .rotate([71 + 30 / 60, -41])
    .fitExtent([[0,0],[width,height]], circle2);

  var path = d3.geoPath().projection(projection);
  var maxZoom = projection.scale();
  console.log(projection.scale(), projection.center());

  var zoom = d3.zoom()
      .scaleExtent([1, 15]) // This is a relative zoom level (go figure)
      .on("zoom", zoomed);

 svg.call(zoom)
  .on("wheel", function() { d3.event.preventDefault(); });

  svg.append("rect")
    .attr("class", "background")
    .attr("width", width)
    .attr("height", height)
    .on("click", reset);

  var g = svg.append('g')
    .attr("class", "geometry");
  //
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

  g.selectAll(".hydro")
      .data(hydro.features)
      // .data(topojson.feature(hydro, hydro.objects.hydro_20km_dissolve).features)
      .enter()
      .append("path")
      .attr("d", path)
      // .attr("fill", "grey")
      .attr("stroke", "white")
      .attr("stroke-width", .125);

  g.selectAll(".dots")
      .data(kl)
      .enter()
      .append("circle")
      .attr("class", "dots")
      .attr("r", 2)
      .attr("cx", function(d) {return projection([d.lng0, d.lat0])[0]} )
      .attr("cy", function(d) {return projection([d.lng0, d.lat0])[1]} )
      .attr("fill","white")

      .on("mouseover", function(d){
        console.log(d.id);
        tooltip.style("visibility", "visible")
        .text(d.id)
        .append("img")
        .attr("src", "images/"+d.id+".jpg");
      })

      .on("mousemove", function(){return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
      .on("mouseout", function(){return tooltip.style("visibility", "hidden");});

function reset() {
  console.log("clicked!");
  // active.classed("active", false);
  // active = d3.select(null);

  svg.transition()
      .duration(750)
      // .call( zoom.transform, d3.zoomIdentity.translate(0, 0).scale(1) ); // not in d3 v4
      .call( zoom.transform, d3.zoomIdentity ); // updated for d3 v4
}


function zoomed() {
  g.style("stroke-width", 1.5 / d3.event.transform.k + "px");
  g.attr("transform", d3.event.transform);
  d3.selectAll(".dots")
    .attr("r", 2 / d3.event.transform.k + "px");
    // updated for d3 v4
  }
}
