// Load full data
var csv_full;
$.ajax({
    async: false,
    url: 'data/kl_geocode_2e.csv',
    success: function(data) {csv_full = data;}
});

// Load IDs only, for index loolup
var csv;
$.ajax({
    async: false,
    url: 'data/kl_ids.csv',
    success: function(data) {csv = data;}
});

// Initialize array of image IDs and index
var ids = $.csv.toArray(csv).map(Number);
var results = Papa.parse(csv_full, {header: true,});
var data = results['data'];
var data_backup = data;
var length = data.length;
var ind = 0;
console.log("KL DATASET LOADED: "+ data.length+' images');

// Search functionality
function findImage(){
    var input = $('#id_field').val();
    var id = parseInt(input);
    if(Number.isInteger(id)){
      ind = ids.indexOf(id)-1;
      renderTemplate();
    }
    else {console.log('Input is not a valid id.');}
}

// Navigation
function nextImage(){
    ind = ((length-1)+ind+1) % (length-1);
    renderTemplate();
}
function prevImage(){
    ind = ((length-1)+ind-1) % (length-1);
    renderTemplate();
  }

// Render an image and data
function renderTemplate(){
    console.log(ind);
    kl_url = 'images/'+data[ind]['id']+'.jpg';

    // FOR MAP BOX
    // if (data[ind]['query_result'] == 1) {
    //   map_url = 'https://api.mapbox.com/styles/v1/brianho/cj1drel9q00092spdf2ntlhjb/static/'+data[ind]['lng0']+','+data[ind]['lat0']+',15,0,0/250x250?access_token=pk.eyJ1IjoiYnJpYW5obyIsImEiOiJjamExNW1leW4wYXR1MzNsZnM3Z2d5NXJtIn0.dHg8RS63oDHkRsEsuPLGSg'
    //   $('#preview').html("<img src='"+kl_url+"' /><img src='"+map_url+"' />");
    // }
    // else {
      $('#preview').html("<img class='image' src='images/"+kl_url+"' />");
    // }
    $('#text').html(data[ind]['text']);
    $('#query_field').val(data[ind]['query']);
    $('#id').html(data[ind]['id']);
    $('#check').prop('checked', (data[ind]['query_result'] == 1) ? true : false);
    $('#exclude').prop('checked', (data[ind]['exclude'] == 1) ? true : false);
    $('#type').val(data[ind]['type']);
    $('#heading').html(parseInt(data[ind]['heading']));
    $('#counter').html((ind+1)+' / '+ (length-1));
    $('#constraint').val(data[ind]['constraint']);

    if (data[ind]['lat0'] == ''){
      $('#latLng').html('()');
      var event = new CustomEvent("loc_change", {
        detail: false
        });
      }
    else {
      $('#latLng').html(parseFloat(data[ind]['lat0']).toFixed(4)+', '+parseFloat(data[ind]['lng0']).toFixed(4));
      var event = new CustomEvent("loc_change", {
        detail: {
          lat: parseFloat(data[ind]['lat0']),
          lng: parseFloat(data[ind]['lng0'])
          }
        });
      }
    document.dispatchEvent(event);
  }

function saveChanges(){
  data[ind]['lat0'] = panorama.getPosition().lat();
  data[ind]['lng0'] = panorama.getPosition().lng();
  data[ind]['heading'] = panorama.getPov().heading;
  data[ind]['pitch'] = panorama.getPov().pitch;
  data[ind]['query_result'] = ($('#check').is(":checked")) ? 1 : 0;
  data[ind]['exclude'] = ($('#exclude').is(":checked")) ? 1 : 0;
  data[ind]['query'] = $('#query_field').val();
  data[ind]['type'] = $('#type').val();
  data[ind]['constraint'] = $('#constraint').val();
}

function exportCSV(){
  console.log("EXPORT");
   var csvContent = Papa.unparse(data);
   console.log(csvContent);
   var encodedUri = encodeURI('data:text/plain;charset=utf-8,'+csvContent);
   var link = document.createElement("a");
   link.setAttribute("href", encodedUri);
   link.setAttribute("download", "kl_update.csv");
   document.body.appendChild(link); // Required for FF
   link.click();
 }

// for Google Maps API
var map;
var markers = [];
var panorama;

// Initalize after load
function initialize() {
 var boston = {lat: 42.377771, lng: -71.116268};
 var sv = new google.maps.StreetViewService();
 var geocoder = new google.maps.Geocoder;

 // Set up the SV panorama
 panorama = new google.maps.StreetViewPanorama(document.getElementById('street-view'));
 // Set the initial Street View camera to the center of the map
 sv.getPanorama({location: boston, radius: 50}, processSVData);

 // Set up the map
 map = new google.maps.Map(document.getElementById('map'), {
   center: {lat: parseFloat(data[ind]['lat0']), lng: parseFloat(data[ind]['lng0'])},
   zoom: 16,
   streetViewControl: false
 });

 // Look for a nearby Street View panorama when the map is clicked.
 // getPanoramaByLocation will return the nearest pano when the
 // given radius is 50 meters or less.
 map.addListener('click', function(event) {
   sv.getPanorama({location: event.latLng, radius: 50}, processSVData);
 });

 panorama.addListener('position_changed', function() {
    // $('#sv_latLng').html(panorama.getPosition() + '');
    $('#sv_latLng').html(parseFloat(panorama.getPosition().lat()).toFixed(4)+', '+parseFloat(panorama.getPosition().lng()).toFixed(4));
    map.setCenter(panorama.getPosition());
  });

  panorama.addListener('pov_changed', function() {
    $('#sv_heading').html(panorama.getPov().heading + '');
    $('#sv_pitch').html(panorama.getPov().pitch + '');
  });

  document.getElementById('geocode').addEventListener('click', function() {
    geocodeInput(geocoder, map, sv);
  });

  document.addEventListener('loc_change', function(event) {
    if (!event.detail) {
      map.setCenter(boston);
      // map.checkResize();
      sv.getPanorama({location: boston, radius: 50}, processSVData);
    }
    else {
      map.setCenter(event.detail);
      // map.checkResize();
      sv.getPanorama({location: event.detail, radius: 50}, processSVData);
      panorama.setPov({
        heading: parseFloat(data[ind]['heading']) ,
        pitch: parseFloat(data[ind]['pitch'])
      });
    }
  });
}

function processSVData(data, status) {
 if (status === 'OK') {
   var marker = new google.maps.Marker({
     position: data.location.latLng,
     map: map,
     title: data.location.description
   });
   markers.push(marker);

   panorama.setPano(data.location.pano);
   panorama.setVisible(true);

   marker.addListener('click', function() {
     var markerPanoID = data.location.pano;
     // Set the Pano to use the passed panoID.
     panorama.setPano(markerPanoID);
     panorama.setPov({
       heading: 270,
       pitch: 0
     });
     panorama.setVisible(true);
   });
 } else {
   console.error('Street View data not found for this location.');
 }
}

function geocodeInput(geocoder, map, sv) {
  var input = document.getElementById('query_field').value;
  var constraint = document.getElementById('constraint').value;
  geocoder.geocode({'address': input+' '+constraint+', MA'}, function(results, status) {
    if (status === 'OK') {
      map.setCenter(results[0].geometry.location);
      // map.checkResize();
      var marker = new google.maps.Marker({
        map: map,
        position: results[0].geometry.location
      });
      markers.push(marker);

      sv.getPanorama({location: results[0].geometry.location, radius: 50}, processSVData);
      panorama.setPov({
        heading: parseFloat(data[ind]['heading']),
        pitch: 0
      });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}
// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
  setMapOnAll(null);
}
// Shows any markers currently in the array.
function showMarkers() {
  setMapOnAll(map);
}
// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
  clearMarkers();
  markers = [];
}

nextImage();
prevImage();
renderTemplate();
