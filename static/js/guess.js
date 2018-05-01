var map = L.map('map').setView([42.36, -71.06], 13);
var accessToken = appConfig.mapbox_key;
var aws_mt = appConfig.aws_MT;
var amazon_host = appConfig.amazon_host;
var lng = appConfig.lng;
var lat = appConfig.lat;
var marker;
var startTime;

var circleIcon = L.icon({
    iconUrl: 'leaf-green.png',
    shadowUrl: 'leaf-shadow.png',

    iconSize:     [38, 95], // size of the icon
    shadowSize:   [50, 64], // size of the shadow
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    shadowAnchor: [4, 62],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});

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
  	var findTime = (Date.now() - startTime)/1000.0;
  	document.getElementById("findTime").value = findTime;
    document.getElementById("guess").disabled = true;
    document.getElementById("submitBtn").disabled = false;

    marker = L.marker([lat, lng])
    marker.addTo(map);

    line = L.polyline([[document.getElementById("guessY").value,document.getElementById("guessX").value],[lat, lng]])
    line.addTo(map);
    map.fitBounds(line.getBounds(), { padding: [10,10] });

    map.off('click', clickMap);
}

function submitForm() {
    var form = document.querySelector("#HIT");
    // Submit back to AWS
    if (aws_mt) {
      var d = new FormData(form);
      var xmlhttp = new XMLHttpRequest();
      xmlhttp.open("POST", "/submit");
      xmlhttp.send(d);
      form.action = amazon_host;
      form.submit();
    }
    // Website only
    else {
      form.action = "/submit"
      form.submit();
    }
}

L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {id:'dark-v9',accessToken:accessToken}).addTo(map);

map.on('click', clickMap)
