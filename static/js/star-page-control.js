// page control functions for stars.html

"use strict";

// globals that will be initialized on document load
var datetimeRadio, changetimeRadio, datetimeSelector, datetimeInput, errorDiv,
    starfieldControlDiv, warnDiv;

var displayError = function(error) {

    errorDiv.show();
    errorDiv.html(error);

}

// success function for geocode in getLatLng (which is triggered on submit 
// button click)
var processFormInputs = function(latlng) {

    // clear previous errors
    errorDiv.empty().hide();

    // hide starfield controls
    starfieldControlDiv.hide();


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

    // disable the button
    // $('#show-stars').attr('disabled', 'disabled');

    // put the data into an obj
    var locTime = {
        lat: latlng.lat,
        lng: latlng.lng,
        datetime: datetime
    }

    // get rotation and ss data
    getLocTimeData(locTime);

};

// when form is submitted
var getLocTimeData = function(locTime) {

    // clear previous planets
    // $('#star-field').empty();

    // d3.request needs data in a query string format
    var data = 'lat=' + locTime.lat;
    data += '&lng=' + locTime.lng;
    if (locTime.datetime !== undefined) {
        data += '&datetime=' + locTime.datetime;
    }

    // can't do simple d3.json because we need to post data
    d3.request('/planets.json')
        .mimeType("application/json")
        .response(function(xhr) { return JSON.parse(xhr.responseText); })
        .header("Content-Type","application/x-www-form-urlencoded")
        // .on('progress', function()) // TODO: show progress bar!

        // rotateAndDrawSolarSystem is in solarsystem.js
        .post(data, rotateAndDrawSolarSystem);

};

$(document).ready(function() {

    // define some globals based on html ids
    datetimeRadio = $('input[name=datetime]:radio');
    changetimeRadio = $('#change-time');
    datetimeSelector =  $('#datetime-selector');
    datetimeInput = $('#datetime-input');
    errorDiv = $('#error');
    starfieldControlDiv = $('#starfield-controls');
    warnDiv = $('#warn');

    // show time picker when someone wants a time other than now
    datetimeRadio.on('change', function() {

        var changetimeChecked = changetimeRadio.is(':checked');

        if (changetimeChecked) {
            datetimeSelector.show();
        } else {
            datetimeSelector.hide();
        }
    });

    // load them stars
    d3.json('/stars.json', drawSkyAndStars);
    
});
