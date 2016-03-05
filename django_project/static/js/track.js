function pushNcheck(markerType, pushLat,pushLon){
    if (markerType=="Downloaded"){
      downloaded.push({lat:pushLat, lng: pushLon });
    }else if (markerType=="Used"){
      used.push({lat:pushLat, lng: pushLon });
    }else if (markerType=="Rated"){
      rated.push({lat:pushLat, lng: pushLon });
    }else if (markerType=="Discuss"){
      discuss.push({lat:pushLat, lng: pushLon });
    }
    if (pushLat>maxLat) maxLat=pushLat;
    if (pushLat<minLat) minLat=pushLat;
    if (pushLon>maxLon) maxLon=pushLon;
    if (pushLon<minLon) minLon=pushLon;

}

function instantBounds(){
    var bounds = new google.maps.LatLngBounds();
    var types= ["Downloaded", "Used", "Rated", "Discuss"];
    var type='';
    for (var j=0; j<4; j++) {
        type=types[j];
        for (var i = 0; i < markers[type].length; i++) {
          var markerPosition =  markers[type][i].getPosition();
          if (markers[type][i].getVisible()) {
            bounds.extend(markerPosition);
          }
        }
    }
    return bounds
}

function addMarkerWithTimeout(array, index, timeout, icon, title) {
  window.setTimeout(function(){addMarker(array, index,icon, title);}, timeout);
}

function addMarker(array, index, icon, title) {
    var marker= new google.maps.Marker({
      position: array[index],
      map: map,
      icon: icon,
      animation: google.maps.Animation.DROP,
      title: title,
      zIndex: index+2
    })
    if (!markers[title]) markers[title] = [];
    markers[title].push(marker);
    var html = "<b>" + title + "</b> <br/>";
    bindInfoWindow(marker, map, infoWindow, html);
  }

function toggleGroup(type) {
  for (var i = 0; i < markers[type].length; i++) {
    var marker = markers[type][i];
    if (!marker.getVisible()) {
      marker.setVisible(true);
    } else {
      marker.setVisible(false);
    }
  }
}

function center(spot) {
  var location;
  var zoom;
  if (spot=='Scotland'){
    location= Scotland;
    zoom=6;
  }else if (spot=='UK'){
    location= UK;
    zoom=5;
  }else if (spot=='User'){
    location= User;
    zoom=10;
  }else if (spot=='Bounds'){
    location= boundCenter;
    zoom=boundZoom-1;
  }
  map.setCenter(location);
  map.setZoom(zoom);
  if (spot=="Bounds"){
    var ccenter=map.getCenter();
    var zzoom=map.getZoom();
    var stop=map.getZoom();
  }
}

function bindInfoWindow(marker, map, infoWindow, html) {
  google.maps.event.addListener(marker, 'click', function() {
    infoWindow.setContent(html);
    infoWindow.open(map, marker);

  });
}