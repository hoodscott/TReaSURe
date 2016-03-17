var animMarkers=[];
var downloaded=[];
var used=[];
var rated=[];
var discuss=[];

function pushNcheck(markerType, pushLat,pushLon){
    if (markerType=="Downloaded") downloaded.push({lat:pushLat, lng: pushLon });
    else if (markerType=="Used") used.push({lat:pushLat, lng: pushLon });
    else if (markerType=="Rated") rated.push({lat:pushLat, lng: pushLon });
    else if (markerType=="Discuss") discuss.push({lat:pushLat, lng: pushLon });
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

function animate(){
  markersLen=animMarkers.length;
  if (markersLen>5) duration=10000;
  else duration=markersLen*2000;
  waitBeforeAnimation=1000;
  delay=duration/markersLen;
  center('Bounds');
  disableCheckboxes(true);
  toggleSpecific('Rated',false);
  toggleSpecific('Downloaded',false);
  toggleSpecific('Used',false);
  toggleSpecific('Discuss',false);
  for (var i = 0; i <markersLen; i++) {
    animMarkers[i].setVisible(false);
    animMarkers[i].setAnimation(google.maps.Animation.DROP);
  }
  for (var i = 0; i <markersLen; i++) {
    confTimeout(animMarkers[i], waitBeforeAnimation+i*delay);
  }
  window.setTimeout(function(){disableCheckboxes(false)}, duration+waitBeforeAnimation);
  window.setTimeout(function(){toggleCheckAll()}, duration+waitBeforeAnimation*2);
}

function confTimeout(marker, time){
  window.setTimeout(function(){marker.setVisible(true)}, time);
}

function disableCheckboxes(cond){
  document.getElementById('FeedbackCheckbox').disabled=cond;
  document.getElementById('DownloadsCheckbox').disabled=cond;
  document.getElementById('UsageCheckbox').disabled=cond;
  document.getElementById('DiscussionCheckbox').disabled=cond;
}

function checkCheckboxes(){
  document.getElementById('FeedbackCheckbox').checked='checked';
  document.getElementById('DownloadsCheckbox').checked='checked';
  document.getElementById('UsageCheckbox').checked='checked';
  document.getElementById('DiscussionCheckbox').checked=false;
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
    if (title!='Discuss') animMarkers.push(marker)
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

function toggleSpecific(type, cond) {
  for (var i = 0; i < markers[type].length; i++) {
    var marker = markers[type][i];
    marker.setVisible(cond);
    }
}


function toggleCheckAll(){
  toggleGroupCheckbox('Rated');
  toggleGroupCheckbox('Downloaded');
  toggleGroupCheckbox('Used');
  toggleGroupCheckbox('Discuss');
  center(document.getElementById('mapCenter').value);
}

function toggleGroupCheckbox(type) {
  if (type=='Rated') checkbox='FeedbackCheckbox'
  else if (type=='Downloaded') checkbox='DownloadsCheckbox';
  else if (type=='Used') checkbox='UsageCheckbox';
  else if (type=='Discuss') checkbox='DiscussionCheckbox';
  cond=document.getElementById(checkbox).checked;
  for (var i = 0; i < markers[type].length; i++) {
    var marker = markers[type][i];
    if (cond!=marker.getVisible()) {
      marker.setVisible(cond);
    }
  }
}

function bindInfoWindow(marker, map, infoWindow, html) {
  google.maps.event.addListener(marker, 'click', function() {
    infoWindow.setContent(html);
    infoWindow.open(map, marker);

  });
}