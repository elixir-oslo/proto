var URL_PREFIX = '../../../..'; // use relative to get the correct proxy prefix (hb vs hbdev)

function Cookie(name, path) {
  this.name = name;
  this.path = path;
  if (!name) throw "cookie must have name";
}
Cookie.prototype.set = function (value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	var cpath = "";
	if (this.path) {
	  cpath = "; path=" + this.path;
	}
	document.cookie = this.name+"="+value+expires+cpath;
}
Cookie.prototype.get = function () {
	var nameEQ = this.name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}
Cookie.prototype.destroy = function () {
	createCookie(this.name,"",-1);
}


var MERCATOR_RANGE = 256;

function bound(value, opt_min, opt_max) {
  if (opt_min != null) value = Math.max(value, opt_min);
  if (opt_max != null) value = Math.min(value, opt_max);
  return value;
}

function degreesToRadians(deg) {
  return deg * (Math.PI / 180);
}

function radiansToDegrees(rad) {
  return rad / (Math.PI / 180);
}

function MercatorProjection() {
  this.pixelOrigin_ = new google.maps.Point(MERCATOR_RANGE / 2, MERCATOR_RANGE / 2);
  this.pixelsPerLonDegree_ = MERCATOR_RANGE / 360;
  this.pixelsPerLonRadian_ = MERCATOR_RANGE / (2 * Math.PI);
  this.zoom = 1024;
};

MercatorProjection.prototype.fromLatLngToPoint = function(latLng, opt_point) {
  //alert(latLng.toString());
  var me = this;

  var point = opt_point || new google.maps.Point(0, 0);

  var origin = me.pixelOrigin_;
  point.x = Math.round(this.zoom * (origin.x + latLng.lng() * me.pixelsPerLonDegree_));
  // NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
  // 89.189.  This is about a third of a tile past the edge of the world tile.
  var siny = bound(Math.sin(degreesToRadians(latLng.lat())), -0.9999, 0.9999);
  point.y = Math.round(this.zoom * (origin.y + 0.5 * Math.log((1 + siny) / (1 - siny)) * -me.pixelsPerLonRadian_));
  return point;
};

MercatorProjection.prototype.fromPointToLatLng = function(point) {
  //alert(point.toString());
  var me = this;
  
  var origin = me.pixelOrigin_;
  var lng = (point.x / this.zoom - origin.x) / me.pixelsPerLonDegree_;
  var latRadians = (point.y / this.zoom - origin.y) / -me.pixelsPerLonRadian_;
  var lat = radiansToDegrees(2 * Math.atan(Math.exp(latRadians)) - Math.PI / 2);
  return new google.maps.LatLng(lat, lng);
};



// Global variables
var map;
var projection = new MercatorProjection();

var scaleY = (config.numRows) / (config.southPixel - config.northPixel);
var scaleX = (config.numCols) / (config.eastPixel - config.westPixel);

var setNewMarker = false;
var setNewCluster = false;
var setDeleteObject = false;

/**
* Updates the Rectangle's bounds to resize its dimensions.
*/
function move_rectangle(rectangle) {
  var latLngBounds = new google.maps.LatLngBounds(
	  rectangle._marker1.getPosition(),
	  rectangle._marker2.getPosition()
  );
  rectangle.setBounds(latLngBounds);
  rectangle._hasInfo = false;
  rectangle._marker1._hasInfo = false;
  rectangle._marker2._hasInfo = false;
}

function LatLngToColRow(point) {
	var pp = projection.fromLatLngToPoint(point);
	this.pixel = pp;
	this.row = 1 + Math.floor((pp.y - config.northPixel) * scaleY);
	this.col = 1 + Math.floor((pp.x - config.westPixel) * scaleX);
	this.valid = true;
	if (this.row > config.numRows || this.row < 1) this.valid = false;
	if (this.col > config.numCols || this.col < 1) this.valid = false;
}

function ColRowToLatLng(col, row) {
  var x = (col - 0.5) / scaleX + config.westPixel;
  var y = (row - 0.5) / scaleY + config.northPixel;
  var point = new google.maps.Point(x, y);
  var latLng = projection.fromPointToLatLng(point);
  //alert(point.toString());
  return latLng;
}

function gotoColRow(col, row) {
  searcher.hide();
  var col2, row2, row1, col1;
  if (col == -1) {
	col2 = col = config.numCols;
	col1 = 1;
	row2 = row1 = row;
  }
  if (row == -1) {
	row = row1 = config.numRows;
	row2 = 1;
	col2 = col1 = col;
  }
  var ll = ColRowToLatLng(col, row);
  var ll1 = ColRowToLatLng(col1 - 0.45, row1 + 0.45);
  var ll2 = ColRowToLatLng(col2 + 0.45, row2 - 0.45);
  map.panTo(config.center);
  //alert(ll.toString());
  map.panTo(ll);
  map.setZoom(6);
  rectangles.create(ll1, ll2);
}

function clusterInfo(event) {
  var cluster = this;
  if (setDeleteObject == true) {
	setDeleteObject = false;
	this._infoWindow.close();
	clusters.remove(this);
	return;
  }
  var bounds = this.getBounds();
  var ne = new LatLngToColRow(bounds.getNorthEast());
  var sw = new LatLngToColRow(bounds.getSouthWest());
  var from = ne.col + "," + ne.row;
  var to = sw.col + "," + sw.row;
  cluster._infoWindow.setPosition(bounds.getCenter());
  if (!cluster._hasInfo) {
    cluster._infoWindow.setContent('...fetching cluster info...');
    $.get(URL_PREFIX + "/hyper?mako=gmapclusterinfo&from="+from+"&to="+to+"&map="+config.name+"&mapid="+config.mapId, function (info) {
      cluster._infoWindow.setContent(info);
      cluster._hasInfo = true;
    });
  }
  searcher.hide();
  cluster._infoWindow.open(map);
}

function markInfo(event, mark) {
  if (!mark) mark = this;
  
  if (setDeleteObject == true) {
	setDeleteObject = false;
	markers.remove(mark);
	mark._infoWindow.close();
	return;
  }
  
  var pos = new LatLngToColRow(mark.getPosition());
  if (config.debug) {
//	var ll = ColRowToLatLng(pos.col, pos.row);
//	var data = 'Coords: ' + mark.getPosition().toString() + ' X,Y: ' + pos.pixel.x + ', ' + pos.pixel.y + ' Col,row: ' + pos.col + ',' + pos.row;
//	data += ' Reverse: '+ll.toString();

        var data = '<b>X (West - East):</b> ' + pos.pixel.x + '<br>' + '<b>Y (North - South):</b> ' + pos.pixel.y + '<br>'

	mark._infoWindow.setContent(data);
	mark._infoWindow.open(map, mark);
  } else {
	if (!mark._hasInfo && pos.valid) {
	  mark._infoWindow.setContent('...fetching mark info...');
        $.get(URL_PREFIX + "/hyper?mako=gmapinfo&row="+pos.row+"&col="+pos.col+"&map=" + config.name + "&mapid=" + config.mapId, function(data) {
		mark._infoWindow.setContent(data);
		mark._hasInfo = true;
	  });
	}
	mark._infoWindow.open(map, mark);
  }
  searcher.hide();
}

function markDragged(event) {
  this._hasInfo = null;
  markInfo(event, this);
}


function Objects(name) {
  this.list = [];
  this.cookie = new Cookie(name);
}
Objects.prototype._fixList = function() {
  for (var o in this.list) {
	var obj = this.list[o];
	obj._index = o;
  }
}
Objects.prototype._removeIndex = function(obj) {
  this.list.splice(obj._index, 1);
  this._fixList();
}
Objects.prototype._remove = undefined;
Objects.prototype.remove = function(obj) {
  this._remove(obj);
  this._removeIndex(obj);
}
Objects.prototype.removeAll = function() {
  for (var m in this.list) {
	this._remove(this.list[m]);
  }
  this.list = [];
}

function Markers() {}
Markers.prototype = new Objects('markers');
Markers.prototype.create = function(latLng, openInfo) {
    var mark = new google.maps.Marker({
      map: map,
      position: latLng,
      draggable: true
    });
    mark._infoWindow = new google.maps.InfoWindow();
    mark._hasInfo = false;
    google.maps.event.addListener(mark, 'click', markInfo);
    google.maps.event.addListener(mark, 'dragend', markDragged);
	if (openInfo != false) google.maps.event.trigger(mark, 'click');
	
	mark._index = this.list.push(mark) - 1;
}
Markers.prototype._remove = function(mark) {
  mark._infoWindow.close();
  mark.setMap(null);
}
Markers.prototype.save = function() {
  var cook = '';
  for (var m in this.list) {
	var mark = this.list[m];
	var pos = mark.getPosition();
	cook += pos.toUrlValue() + '|';
  }
  this.cookie.set(cook);
}
Markers.prototype.restore = function() {
  var cook = this.cookie.get();
  if (cook == null) return;
  var marks = cook.split('|');
  for (var m in marks) {
	var pos = marks[m].split(',');
	if (pos.length == 2) {
	  var lat = parseFloat(pos[0]);
	  var lng = parseFloat(pos[1]);
	  if (!isNaN(lat) && !isNaN(lng))
		  this.create(new google.maps.LatLng(lat, lng), false);
	}
  }
}

function Rectangles() {}
Rectangles.prototype = new Objects('rectangles');
Rectangles.prototype.create = function (latLng, latLng2) {
  var rectangle = new google.maps.Rectangle({map: map, fillOpacity: 0.0, strokeColor: '#FFFFFF', strokeWeight: 2, strokeOpacity: 1.0});
  var latLngBounds = new google.maps.LatLngBounds(latLng, latLng2);
  rectangle.setBounds(latLngBounds);
  google.maps.event.addListener(rectangle, 'click', function() {
	if (setDeleteObject) {
	  setDeleteObject = false;
	  rectangles.remove(this);
	}
	});
  rectangle._index = this.list.push(rectangle) - 1;
}
Rectangles.prototype._remove = function(rect) {
  rect.setMap(null);
}

function Clusters() {}
Clusters.prototype = new Objects('clusters');
Clusters.prototype.create = function (latLng, latLng2) {
  // Plot two markers to represent the Rectangle's bounds.
  var marker1 = new google.maps.Marker({
    map: map,
    position: new google.maps.LatLng(latLng.lat(), latLng.lng()),
    draggable: true,
    title: 'Drag me!'
  });
  marker1._infoWindow = new google.maps.InfoWindow();
  //marker1._hasInfo = false;
  google.maps.event.addListener(marker1, 'click', markInfo);
  
  if (!latLng2) 
    latLng2 = new google.maps.LatLng(latLng.lat() + (1 / map.getZoom()), latLng.lng() + (10 / map.getZoom()))
  
  var marker2 = new google.maps.Marker({
    map: map,
    position: latLng2,
    draggable: true,
    title: 'Drag me!'
  });
  marker2._infoWindow = new google.maps.InfoWindow();
  //marker2._hasInfo = false;
  google.maps.event.addListener(marker2, 'click', markInfo);
  
  
  var rectangle = new google.maps.Rectangle({map: map, fillOpacity: 0.1, strokeColor: '#FFFFFF', strokeWeight: 2, strokeOpacity: 1.0});
  rectangle._marker1 = marker1;
  rectangle._marker2 = marker2;
  rectangle._infoWindow = new google.maps.InfoWindow();
  rectangle._hasInfo = false;
  
  // Allow user to drag each marker to resize the size of the Rectangle.
  google.maps.event.addListener(marker1, 'drag', function(){move_rectangle(rectangle)});
  google.maps.event.addListener(marker2, 'drag', function(){move_rectangle(rectangle)});
  google.maps.event.addListener(rectangle, 'click', clusterInfo);
  move_rectangle(rectangle);
  
  rectangle._index = this.list.push(rectangle) - 1;
}
Clusters.prototype._remove = function(clust) {
  markers.remove(clust._marker1);
  markers.remove(clust._marker2);
  clust._infoWindow.close();
  clust.setMap(null);
}
Clusters.prototype.save = function() {
  var cook = '';
  for (var r in this.list) {
    var rect = this.list[r];
    var pos1 = rect._marker1.getPosition().toUrlValue();
    var pos2 = rect._marker2.getPosition().toUrlValue();
    cook += pos1 + ',' + pos2 + '|';
  }
  this.cookie.set(cook);
}
Clusters.prototype.restore = function() {
  var cook = this.cookie.get();
  if (cook == null) return;
  var marks = cook.split('|');
  for (var m in marks) {
    var pos = marks[m].split(',');
    if (pos.length == 4) {
      var lat1 = parseFloat(pos[0]);
      var lng1 = parseFloat(pos[1]);
      var lat2 = parseFloat(pos[2]);
      var lng2 = parseFloat(pos[3]);
      if (!isNaN(lat1) && !isNaN(lng1) && !isNaN(lat2) && !isNaN(lng2))
        this.create(new google.maps.LatLng(lat1, lng1), new google.maps.LatLng(lat2, lng2));
    }
  }
}

function MapState(map) {
  this.map = map;
  this.cookie = new Cookie('state');
}
MapState.prototype.save = function() {
  var cook = map.getCenter().toUrlValue() + "|" + map.getZoom();
  this.cookie.set(cook);
}
MapState.prototype.restore = function() {
  var cook = this.cookie.get();
  if (cook == null) return;
  var state = cook.split('|');
  var pos = state[0].split(',');
  map.setCenter(new google.maps.LatLng(parseFloat(pos[0]), parseFloat(pos[1])));
  map.setZoom(parseInt(state[1]));
}
MapState.prototype.reset = function() {
  if (!config.debug)
    config.center = ColRowToLatLng(config.numCols/2, config.numRows/2);
  else 
	config.center = new google.maps.LatLng(80, 0);
  map.setCenter(config.center);
  map.setZoom(config.zoom);
}


function Searcher(elText, elList) {
  this.elText = elText;
  this.elList = elList;
}
Searcher.prototype.search = function () {
  var _this = this;
  var text = _this.elText.value;
  this.timeOut = null;
  if (text.length >= 1) {
	if (!_this.searching && text != _this.oldText) {
	  _this.searching = true;
	  _this.oldText = text;
	  $.get(URL_PREFIX + '/hyper?mako=gmapsearch&map='+config.name+"&mapid="+config.mapId+'&query='+text, function(data){
		_this.searching = false;
		// check if query changed in the meantime
		if (_this.elText.value != _this.oldText) {
		  _this.search();
		}
		$(_this.elList).html(data);
		$(_this.elList).show();		  
		
	  });
	} else {
	  $(_this.elList).show();
	}
  } else {
	_this.oldText = text;
	$(_this.elList).hide();
	$(_this.elList).html('');
  }
}
Searcher.prototype.hide = function () {
	$(this.elList).hide();
	$(this.elText).blur();
	//google.maps.event.trigger(map, 'click');
}

function ClusterControl(map, div) {
  div.style.padding = '2px';
  div.style.textAlign = 'right';

  var newMarker = document.createElement("input");
  newMarker.type = "button";
  newMarker.value = "New marker";
  div.appendChild(newMarker);
  google.maps.event.addDomListener(newMarker, 'click', function() {
    setNewMarker = true;
  });
  
  var newCluster = document.createElement("input");
  newCluster.type = "button";
  newCluster.value = "New cluster";
  div.appendChild(newCluster);
  google.maps.event.addDomListener(newCluster, 'click', function() {
    setNewCluster = true;
  });

  var delObject = document.createElement("input");
  delObject.type = "button";
  delObject.value = "Delete object";
  div.appendChild(delObject);
  google.maps.event.addDomListener(delObject, 'click', function() {
    setDeleteObject = true;
  });

  var delAll = document.createElement("input");
  delAll.type = "button";
  delAll.value = "Reset map";
  div.appendChild(delAll);
  google.maps.event.addDomListener(delAll, 'click', function() {
	mapState.reset();
	if (markers.list.length > 0 || clusters.list.length > 0 || rectangles.list.length > 0) {
	  if (confirm('Delete all markers and clusters?')) {
		markers.removeAll();
		clusters.removeAll();
		rectangles.removeAll();
	  }
	}
  });

  var searchDiv = document.createElement("div");
  searchDiv.style.textAlign = 'right';
  searchDiv.style.width = "400px";
  
  var searchText = document.createElement("input");
  searchText.type = "text";
  searchText.size = "25";  
  searchText.value = "";
  searchDiv.appendChild(searchText);

  var searchList = document.createElement("div");
  searchList.style.height = "200px";
  searchList.style.backgroundColor = "#ffffff";
  searchList.style.overflow = "scroll";
  searchList.style.display = "none";
  searchList.style.textAlign = 'left';
//  searchList.style.whiteSpace = 'nowrap';

  searcher = new Searcher(searchText, searchList);
  google.maps.event.addDomListener(searchText, 'keyup', function() {
	if (!searcher.timeOut)
	  searcher.timeOut = setTimeout('searcher.search()', 1000);
  });
  google.maps.event.addDomListener(searchText, 'click', function() {
	searcher.search();
    //setTimeout('searcher.search()', 1500);
  });

  searchDiv.appendChild(searchList);
  
  div.appendChild(searchDiv);

}

var searcher;
var markers = new Markers();
var clusters = new Clusters();
var rectangles = new Rectangles();
var mapState;

function initialize() {
  $('body').css('margin', '0');
  $('body').append("<div id='map_canvas' style='height: " + $(window).height() + "px; width: " + $(window).width() + "px'></div>");
//  $('#map_canvas').height($(window).height()).width($(window).width());

  var heatMapType = new google.maps.ImageMapType({
	//projection: projection,
	getTileUrl: function(coord, zoom) {
	  if (coord.x >= 0 && coord.y >= 0)
		return "tiles/" + zoom + "/" + coord.x + "-" + coord.y + ".png";
	  else
		return false;
	},
	tileSize: new google.maps.Size(256, 256),
	isPng: true,
	minZoom: 0,
	maxZoom: 9
  });

  if (!config.debug)
    config.center = ColRowToLatLng(config.numCols/2, config.numRows/2);
  else 
	config.center = new google.maps.LatLng(80, 0);
	
  if (!config.zoom)	config.zoom = 2;
	
  map = new google.maps.Map(document.getElementById("map_canvas"), {
    zoom: config.zoom,
    center: config.center,
    mapTypeId: google.maps.MapTypeId.ROADMAP, //dummy value
    mapTypeControl: false,
    backgroundColor: '#111111',
	disableDoubleClickZoom: false,
	scrollwheel: false
  });

  // Now attach the map type to the map's registry
  map.mapTypes.set('heatmap', heatMapType);
  // We can now set the map to use the map type
  map.setMapTypeId('heatmap');

  var clusterControlDiv = document.createElement('DIV');
  var clusterControl = new ClusterControl(map, clusterControlDiv);

  clusterControlDiv.index = 1;
  map.controls[google.maps.ControlPosition.TOP_RIGHT].push(clusterControlDiv);

  google.maps.event.addListener(map, 'rightclick', function(event) {
  });

  google.maps.event.addListener(map, 'click', function(event) {
	searcher.hide();
    if (setNewCluster) {
      setNewCluster = false;
      clusters.create(event.latLng);
    }
    else if (setNewMarker) {
      setNewMarker = false;
      markers.create(event.latLng);
    }
  });

  mapState = new MapState(map);

  markers.restore();
  clusters.restore();
  mapState.restore();
}

function GUnload(){
  markers.save();
  clusters.save();
  mapState.save();
}

$(document).ready(initialize);
