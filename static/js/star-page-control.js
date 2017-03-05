// page control functions for stars.html

"use strict";

// globals that will be initialized on document load
var datetimeRadio, changetimeRadio, datetimeSelector, datetimeInput, errorDiv;

var displayError = function(error) {

    errorDiv.show();
    errorDiv.html(error);

}

// success function for geocode in getLatLng (which is triggered on submit 
// button click)
var processFormInputs = function(latlng) {

    // clear previous errors
    errorDiv.empty().hide();

    if (latlng === undefined) {
        // geolocation failed
        displayError('Please use autocomplete to select a location');
        return;
    }

    // get the time data
    var datetime;
    if (changetimeRadio.is(':checked')) {
        datetime = datetimeInput.val();
        if (!datetime) {
            displayError('Please either choose "Now" or enter a date and time');
            return;
        }
    }

    // getStars is defined in stars-d3.js
    getStars(latlng.lat, latlng.lng, datetime);

};

$(document).ready(function() {

    // define some globals based on html ids
    datetimeRadio = $('input[name=datetime]:radio');
    changetimeRadio = $('#change-time')
    datetimeSelector =  $('#datetime-selector')
    datetimeInput = $('#datetime-input')
    errorDiv = $('#error');

    // show time picker when someone wants a time other than now
    datetimeRadio.on('change', function() {

        var changetimeChecked = changetimeRadio.is(':checked');

        if (changetimeChecked) {
            datetimeSelector.show();
        } else {
            datetimeSelector.hide();
        }
    });

});
