
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
  .defer(d3.json, "geo/circle_7_5km.geojson")
  .defer(d3.json, "geo/circle_10km.geojson")
  .defer(d3.json, "geo/circle_15km.geojson")
  .defer(d3.json, "geo/coastline_20km.geojson")
  .defer(d3.json, "geo/hydro_20km.json")
  // .defer(d3.json, "geo/mass_roads_5km.json")
  .defer(d3.json, "geo/City_of_Boston_Boundary.json")
  .defer(d3.csv, "data/kl_geocode_2g.csv")
  .await(makeMyMap);


// d3.json("geo/City_of_Boston_Boundary.geojson", function(error, data) {
function makeMyMap(error, circle, circle2, circle3, circle4, coast, hydro, boundary, kl){
  if (error) throw error;


  // NAD83 Massachusetts Mainalnd (EPSG:26986)
  var projection = d3.geoConicConformal()
    .parallels([41 + 43 / 60, 42 + 41 / 60])
    .rotate([71 + 30 / 60, -41])
    .fitExtent([[0,0],[width,height]], circle4);
  var path = d3.geoPath().projection(projection);
  console.log(projection.scale(), projection.center());

  svg.selectAll(".boundary")
      .data(topojson.feature(boundary, boundary.objects.City_of_Boston_Boundary).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("stroke-width", .125)
      .attr("stroke","white");

  svg.selectAll(".circle")
      .data(circle4.features)
      // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-width", .125);

  svg.selectAll(".coast")
      .data(coast.features)
      // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-width", .125);

    // svg.selectAll(".hydro")
    //     .data(topojson.feature(hydro, hydro.objects.hydro_20km).features)
    //     // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
    //     .enter()
    //     .append("path")
    //     .attr("d", path)
    //     .attr("fill", "none")
    //     .attr("stroke", "white")
    //     .attr("stroke-width", .125);
  // svg.selectAll(".circle2")
  //     .data(circle2.features)
  //     // .data(topojson.feature(roads, roads.objects.mass_roads_5km).features)
  //     .enter()
  //     .append("path")
  //     .attr("d", path)
  //     .attr("stroke", "white")
  //     .attr("stroke-width", .125);

  svg.selectAll("circles")
      .data(kl)
      .enter()
      .append("circle")
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
  // });
}
  // svg.append("path")
  //   .attr("d", path(data.features))
  //   .attr("stroke","white")
  //   .attr("fill","white");
  // });
