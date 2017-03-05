// javascript for getting latitude and longitude of user via Google
// autocomplete and geocoding

// global var for the autocomplete object
var autocomplete


function initPlaces() {
    // this is the callback for the google maps script load

    var autocompleteParams = {placeIdOnly: true}
    var cityInput = document.getElementById('city-input');

    autocomplete = new google.maps.places.Autocomplete(cityInput, autocompleteParams);
    autocomplete.setTypes(['(cities)']);
}

// on form 'submit'
$('#show-stars').on('click', function() {

    // for use later
    var geocoder = new google.maps.Geocoder;
    var errorDiv = $('#error');

    // clear any old errors
    errorDiv.empty().hide();

      // infowindow.close();
      var place = autocomplete.getPlace();

      if (!place || !place.place_id) {

        errorDiv.show().html('Please choose a city using autocomplete.');
        return;

      }
      geocoder.geocode({'placeId': place.place_id}, function(results, status) {

        if (status !== 'OK') {
          window.alert('Geocoder failed due to: ' + status);
          return;
        }
          city = results[0].geometry.location;

        // get star data and display it
        // getStars defined in stars-d3.js
        getStars(city.lat(), city.lng());

      });

});