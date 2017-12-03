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


// d3.json("geo/City_of_Boston_Boundary.geojson", function(error, data) {
function makeMyMap(error, circle, circle2, boundary,landmark, kl){
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


var n = Object.keys(kl).length;
var i = -1; // a counter!

function animate() {
  i = (i + 100) % n;
  console.log(i);
  /*
  d3.transition()
      .duration(1250)
      .on("start", function() {
        })
      .tween("scale", function() {
      */


        g.selectAll(".highlight")
          .transition()
          .duration(2500)
          .attr("r",1)
          .on("end", function() {this.remove()})

        d3.selectAll('.dots').filter(function(d, j) { return j!=i; })
          .transition()
          .duration(2500)
          .attr("fill", "cyan")
          .attr("r", 1)
          .delay(1000);
          // .style("z-index", -1);

        var highlight = d3.selectAll('.dots').filter(function(d, j) { return j==i; });

        g.append("circle")
          .attr("class", "highlight")
          .attr("fill", "red")
          .attr("r", 1)
          .attr("opacity", .5)
          .attr("cx", highlight.attr("cx"))
          .attr("cy", highlight.attr("cy"))
          .transition()
          .duration(2500)
          .attr("r", 100)
          .on("end", animate);
        // .style("z-index", 100)

    };
animate();

/*
/////
      var globe = {type: "Sphere"},
          land = topojson.feature(world, world.objects.land),
          countries = topojson.feature(world, world.objects.countries).features,
          borders = topojson.mesh(world, world.objects.countries, function(a, b) { return a !== b; }),
          i = -1,
          n = countries.length;

      countries = countries.filter(function(d) {
        return names.some(function(n) {
          if (d.id == n.id) return d.name = n.name;
        });
      }).sort(function(a, b) {
        return a.name.localeCompare(b.name);
      });

      (function transition() {
        d3.transition()
            .duration(1250)
            .each("start", function() {
              title.text(countries[i = (i + 1) % n].name);
            })
            .tween("rotate", function() {
              var p = d3.geo.centroid(countries[i]),
                  r = d3.interpolate(projection.rotate(), [-p[0], -p[1]]);
              return function(t) {
                projection.rotate(r(t));
                c.clearRect(0, 0, width, height);
                c.fillStyle = "#ccc", c.beginPath(), path(land), c.fill();
                c.fillStyle = "#f00", c.beginPath(), path(countries[i]), c.fill();
                c.strokeStyle = "#fff", c.lineWidth = .5, c.beginPath(), path(borders), c.stroke();
                c.strokeStyle = "#000", c.lineWidth = 2, c.beginPath(), path(globe), c.stroke();
              };
            })
          .transition()
            .each("end", transition);
      })();
    }
/////
*/

function reset() {
  console.log("clicked!");
  // active.classed("active", false);
  // active = d3.select(null);
  svg.transition()
      .duration(750)
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
