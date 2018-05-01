console.log(appConfig);

var accessToken = appConfig.mapbox_key;
var aws_mt = appConfig.aws_MT;
var amazon_host = appConfig.amazon_host;
var image_loc = L.latLng(appConfig.lat, appConfig.lng);
var marker;
var startTime;
var trial = 0;

var map = L.map('map').setView([42.36, -71.06], 13);

function completeRead() {
  startTime = Date.now();
  document.getElementById("pano").style.filter = blur(0);
  document.getElementById("pano").setAttribute("style","-webkit-filter:blur(" + 0 + "px)")
  document.getElementById("pano").style.opacity = 1;
  document.getElementById("instructions").style.visibility = "hidden";
}

function clickMap(e) {
    if (marker) { map.removeLayer(marker) };
    marker = L.marker([e.latlng.lat, e.latlng.lng])
    marker.addTo(map);
        // .bindPopup('A pretty CSS3 popup.<br> Easily customizable.')
        // .openPopup();
    document.getElementById("guessX").value = e.latlng.lng;
    document.getElementById("guessY").value = e.latlng.lat;
    document.getElementById("guess").disabled = false;
}

function makeGuess() {
    var guess = L.latLng(document.getElementById("guessY").value, document.getElementById("guessX").value);

  	var findTime = (Date.now() - startTime)/1000.0;
  	document.getElementById("findTime").value = findTime;
    document.getElementById("guess").disabled = true;
    document.getElementById("submitBtn").disabled = false;

    marker = L.marker(image_loc)
    marker.addTo(map);
    line = L.polyline([guess,image_loc])
    line.addTo(map);
    map.options.zoomSnap = 0.1;
    map.fitBounds(line.getBounds(), {padding:[50,50]});
    map.off('click', clickMap);
    map.options.zoomSnap = 1;

    var distance = image_loc.distanceTo(guess);
    console.log(distance);
    document.getElementById("score").innerText = distance.toFixed(2)+" meters";

}

function submitForm() {
    var form = document.querySelector("#HIT");
    // Submit back to AWS
    if (aws_mt) {
      var d = new FormData(form);
      var xmlhttp = new XMLHttpRequest();
      xmlhttp.open("POST", "/submit");
      xmlhttp.send(d);
      form.action = (trial <= 4) ? "/guess" : amazon_host;
      form.submit();
    }
    // Website only
    else {
      form.action = (trial <= 4) ? "/guess" : "/submit";
      form.submit();
    }
}

L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {id:'dark-v9',accessToken:accessToken}).addTo(map);

map.on('click', clickMap)
