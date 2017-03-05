// javascript for getting latitude and longitude of user via Google
// autocomplete and geocoding

function initPlaces() {
    // this is the callback for the google maps script load

    var cityInput = document.getElementById('city-input');
    var autocomplete = new google.maps.places.Autocomplete(cityInput)
                            .setTypes(['(cities)']);

}
