// Load data
var csv_full;
$.ajax({
    async: false,
    url: 'data/kl_geocode_0.csv',
    success: function(data) {csv_full = data;}
});
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
var length = data.length;

console.log("KL DATASET LOADED: "+ data.length);
var ind = 0;

function findImage(){
    var input = $('#id_field').val();
    var id = parseInt(input);
    if(Number.isInteger(id)){
      ind = ids.indexOf(id);
      renderTemplate();
    }
    else {console.log('NaN');}
}

function nextImage(){
    ind = (length+ind+1) % length;
    renderTemplate();
}

function prevImage(){
    ind = (length+ind-1) % length;
    renderTemplate();
  }

function renderTemplate(){
    console.log(ind);
    kl_url = 'images/'+data[ind]['id']+'.jpg';

    // FOR MAP BOX
    // if (data[ind]['query_result'] == 1) {
    //   map_url = 'https://api.mapbox.com/styles/v1/brianho/cj1drel9q00092spdf2ntlhjb/static/'+data[ind]['lng0']+','+data[ind]['lat0']+',15,0,0/250x250?access_token=pk.eyJ1IjoiYnJpYW5obyIsImEiOiJjamExNW1leW4wYXR1MzNsZnM3Z2d5NXJtIn0.dHg8RS63oDHkRsEsuPLGSg'
    //   $('#preview').html("<img src='"+kl_url+"' /><img src='"+map_url+"' />");
    // }
    // else {
      $('#preview').html("<img class='image' src='"+kl_url+"' />");
    // }

    $('#text').html(data[ind]['text']);
    $('#query_field').val(data[ind]['query']);
    $('#id').html(data[ind]['id']);
    $('#check').prop('checked', (data[ind]['query_result'] == 1) ? true : false);
    $('#latLng').html(data[ind]['lat0']+', '+data[ind]['lng0']);

    var event = new CustomEvent("loc_change", {
      detail: {
        lat: parseFloat(data[ind]['lat0']),
        lng: parseFloat(data[ind]['lng0'])
        }
      });
    document.dispatchEvent(event);
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

/*
* Click the map to set a new location for the Street View camera.
*/
 var map;
 var panorama;

 function initialize() {
   var boston = {lat: 42.377771, lng: -71.116268};
   var sv = new google.maps.StreetViewService();
   panorama = new google.maps.StreetViewPanorama(document.getElementById('street-view'));

   // Set up the map.
   map = new google.maps.Map(document.getElementById('map'), {
     center: boston,
     zoom: 16,
     streetViewControl: false
   });

   // Set the initial Street View camera to the center of the map
   sv.getPanorama({location: boston, radius: 50}, processSVData);
   // Look for a nearby Street View panorama when the map is clicked.
   // getPanoramaByLocation will return the nearest pano when the
   // given radius is 50 meters or less.
   map.addListener('click', function(event) {
     sv.getPanorama({location: event.latLng, radius: 50}, processSVData);
   });
   document.addEventListener('loc_change', function(event) {
     map.setCenter(event.detail);
     sv.getPanorama({location: event.detail, radius: 50}, processSVData);
   });
 }

 function processSVData(data, status) {
   if (status === 'OK') {
     var marker = new google.maps.Marker({
       position: data.location.latLng,
       map: map,
       title: data.location.description
     });

     panorama.setPano(data.location.pano);
     panorama.setPov({
       heading: 270,
       pitch: 0
     });
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

 renderTemplate()
