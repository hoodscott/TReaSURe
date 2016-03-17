var infoWindow = new google.maps.InfoWindow();
var UK = {lat: 54.53, lng: -4.17};
var Scotland = {lat: 57.83, lng: -4.25};


var markers={
  "Downloaded": [],
  "Used": [],
  "Rated": [],
  "Discuss": []
};

var map = new google.maps.Map(document.getElementById('map'));
var infoWindow = new google.maps.InfoWindow();

for (i = 0; i < downloaded.length; i++) addMarker(downloaded, i, dlicon, "Downloaded");
for (i = 0; i < used.length; i++) addMarker(used, i, classicon, "Used");
for (i = 0; i < rated.length; i++) addMarker(rated, i, fbicon, "Rated");
for (i = 0; i < discuss.length; i++) addMarker(rated, i, talkicon, "Discuss");
function fitMarkers(){
  var boundZoom=0;
  var maxLat = -90;
  var minLat = 90;
  var maxLon = -180;
  var minLon = 180;

  function checkPushedLonLat(pushLon,pushLat){
    if (pushLat>maxLat) maxLat=pushLat;
    if (pushLat<minLat) minLat=pushLat;
    if (pushLon>maxLon) maxLon=pushLon;
    if (pushLon<minLon) minLon=pushLon;
  }

  for (i = 0; i < downloaded.length; i++) checkPushedLonLat(downloaded[i]['lng'],downloaded[i]['lat']);
  for (i = 0; i < used.length; i++) checkPushedLonLat(used[i]['lng'],used[i]['lat']);
  for (i = 0; i < rated.length; i++) checkPushedLonLat(rated[i]['lng'],rated[i]['lat']);
  for (i = 0; i < discuss.length; i++) checkPushedLonLat(discuss[i]['lng'],discuss[i]['lat']);
  var tmpLat=((maxLat + minLat)/2.0);
  var tmpLon=((maxLon + minLon)/2.0);
  var boundCenter= {lat: ((maxLat+minLat)/2.0), lng:((maxLon+minLon)/2.0)};
  //Determine the best zoom level based on the map scale and bounding coordinate information
  //best zoom level based on map width
  var zoom1 = Math.log(360.0 / 256.0 * (640-20) / (maxLon - minLon)) / Math.log(2);
  //best zoom level based on map height
  var zoom2 = Math.log(180.0 / 256.0 * (480-20) / (maxLat - minLat)) / Math.log(2);

  //use the most zoomed out of the two zoom levels
  boundZoom = Math.ceil((zoom1 < zoom2) ? zoom1 : zoom2);
  map.setCenter(boundCenter);
  map.setZoom(boundZoom-1);
}

function center(spot) {
  var location;
  var zoom;
  if(spot=='Bounds'){
    fitMarkers();
  }else{
    if (spot=='Scotland'){
      location= Scotland;
      zoom=6;
    }else if (spot=='UK'){
      location= UK;
      zoom=5;
    }else if (spot=='User'){
      location= User;
      zoom=10;
    }
    map.setCenter(location);
    map.setZoom(zoom);
  }
}
if (document.getElementById('mapCenter').value=='Bounds'){
  $(window).bind('load', function(){toggleCheckAll();})
}
  toggleCheckAll();

