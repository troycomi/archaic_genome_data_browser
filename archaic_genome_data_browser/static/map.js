var mymap = L.map('mapid').fitWorld({ animate: false }).zoomIn(1, { animate: false });

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    noWrap: true,
    id: 'mapbox.outdoors',
    accessToken: 'pk.eyJ1IjoibHBhcnNvbnMiLCJhIjoiY2ptYXJtaWlmMW92YzNwcXFjdW5uZ2d4cCJ9.C_9_7EWGRR5zKOQfzSpx9g'
}).addTo(mymap);

var geojsonMarkerOptions = {
    radius: 8,
    fillColor: "#333333",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};

function onEachFeature(feature, layer) {
    layer.bindTooltip(
        layer.feature.properties.name, {
            permanent: false,
            direction: 'auto'
        }
    )
    layer.on('click', function(){
        window.location = (layer.feature.properties.url);
    });
}

let xhr = new XMLHttpRequest();
xhr.open('GET', data_url);
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.onload = function() {
    if (xhr.status === 200) {
        L.geoJSON(JSON.parse(xhr.responseText), {
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, geojsonMarkerOptions)
            },
            onEachFeature: onEachFeature,
            style: function (feature) {
                return {fillColor: feature.properties.color};
            }
        // }).bindPopup(function (layer) {
        //     return layer.feature.properties.description;
        }).addTo(mymap);
    }
};
xhr.send();

mymap.on('resize', function(e) {
    mymap.fitWorld({reset: true, animate: false}).zoomIn(1, { animate: false });
});
