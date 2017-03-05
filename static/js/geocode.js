// javascript for getting latitude and longitude of user via Google
// autocomplete and geocoding

"use strict";

// global var for the autocomplete object
var autocomplete;


function initPlaces() {
    // this is the callback for the google maps script load

    var autocompleteParams = {placeIdOnly: true}
    var cityInput = document.getElementById('city-input');

    autocomplete = new google.maps.places.Autocomplete(cityInput, autocompleteParams);
    autocomplete.setTypes(['(cities)']);
}


// on form 'submit'
var getLatLng = function() {

    // for use later
    var geocoder = new google.maps.Geocoder;

    var place = autocomplete.getPlace();

    // couldn't get a place? display an error and bail
    if (!place || !place.place_id) { 
        processFormInputs(); 
        return; 
    }

    // otherwise, get the data and return
    geocoder.geocode({'placeId': place.place_id}, function(results, status) {

        if (status !== 'OK') {
            window.alert('Geocoder failed due to: ' + status);
            return;
        }
            
        var city = results[0].geometry.location;

        // continue with the form processing, now that we have lat and lng
        // processFormInputs is found in star-page-control.js
        processFormInputs({ lat: city.lat(), lng: city.lng() });

    });

}

$(document).ready(function() {
    // getLatLng defined in geocode.js
    $('#show-stars').on('click', getLatLng);
});