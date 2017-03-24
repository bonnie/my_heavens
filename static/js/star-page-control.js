// page control functions for stars.html

"use strict";

// globals that will be initialized on document load
var datetimeRadio, changetimeRadio, datetimeInput, errorDiv, datelocInfoDiv,
    starfieldControlDiv, warnDiv, eclipticToggle, planetToggle, planetWarning,
    celestialInfoTable, datetimeFormGroup, datelocFormGroups, celestialInfoDiv,
    datelocChangeBtn, showStarsBtn, datelocForm, datelocInfoTable,
    datelocFormCancel, masterInfoDiv, celestialDivInstructions,
    celestialInfoHeader, datelocInfoHeader;

var displayError = function(error) {

    errorDiv.show();
    errorDiv.html(error);

};

// success function for geocode in getLatLng (which is triggered on submit 
// button click)
var processFormInputs = function(latlng) {

    // clear previous errors
    errorDiv.empty().hide();

    // hide starfield controls and info divs
    masterInfoDiv.hide();

    // erase info from the date/location table
    datelocInfoTable.empty();

    if (latlng === undefined) {
        // geolocation failed
        displayError('Please use autocomplete to select a location');
        $('#location-form-group').addClass('has-error');
        return;
    }

    // get the time data
    var datetime;
    if (changetimeRadio.is(':checked')) {
        datetime = datetimeInput.val();
        if (!datetime) {
            displayError('Please either choose "Now" or enter a valid date and time');
            datetimeFormGroup.addClass('has-error');
            return;
        }
    }

    // hide the form
    datelocForm.hide();

    // put the data into an obj
    var locTime = {
        lat: latlng.lat,
        lng: latlng.lng,
        datetime: datetime
    };

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
    d3.request('/place-time-data.json')
        .mimeType("application/json")
        .response(function(xhr) { return JSON.parse(xhr.responseText); })
        .header("Content-Type","application/x-www-form-urlencoded")
        // .on('progress', function()) // TODO: show progress bar!

        // rotateAndDrawSolarSystem is in solarsystem.js
        .post(data, rotateAndDrawSolarSystem);

};

var changeDateloc = function() {
    // callback for clicking on the 'change date / location' button

    datelocForm.show();
    datelocFormCancel.show();
    masterInfoDiv.hide();
};

var cancelDatelocForm = function() {
    // callback for cancel button on date / location form

    datelocForm.hide();
    masterInfoDiv.show();

};

var populateDatelocInfo = function(datelocInfo) {
    // to populate the date/location info div
    // uses global addInfoTableRow from d3-main.js

    var placeString = autocomplete.getPlace().name.split(',')[0];
    var datetimeString = datelocInfo.dateString + ' ' + datelocInfo.timeString;
    addInfoDivHeader(datelocInfoHeader, placeString, datetimeString);
    addDatelocTableRow('Latitude', datelocInfo.lat);
    addDatelocTableRow('Longitude', datelocInfo.lng);

};

$(document).ready(function() {

    // define some globals based on html ids
    datetimeRadio = $('input[name=datetime]:radio');
    changetimeRadio = $('#change-time');
    datetimeInput = $('#datetime-input');
    errorDiv = $('#error');
    starfieldControlDiv = $('#starfield-controls');
    warnDiv = $('#warn');

    eclipticToggle = $('#ecliptic-toggle');
    planetToggle = $('#planet-toggle');

    planetWarning = $('#planet-warning');

    showStarsBtn = $('#show-stars');
    masterInfoDiv = $('#master-info-div');
    datetimeFormGroup = $('#datetime-form-group');

    datelocForm = $('#dateloc-form');
    datelocFormGroups = $('#dateloc-form .form-group');
    datelocFormCancel = $('#dateloc-form-cancel');

    celestialInfoDiv = $('#celestial-info');
    celestialInfoTable = $('#celestial-info .info-table');
    celestialInfoHeader = $('#celestial-info .info-header');
    celestialDivInstructions = $('#celestial-div-instructions').get(0);

    datelocInfoDiv = $('#dateloc-info');
    datelocInfoHeader = $('#dateloc-info .info-header');
    datelocInfoTable = $('#dateloc-info .info-table');
    datelocChangeBtn = $('#dateloc-change-btn');

    // show time picker when someone wants a time other than now
    datetimeRadio.on('change', function() {

        var changetimeChecked = changetimeRadio.is(':checked');

        if (changetimeChecked) {
            datetimeFormGroup.show();
        } else {
            datetimeFormGroup.hide();
        }
    });

    // getLatLng defined in geocode.js
    showStarsBtn.on('click', getLatLng);

    // event handler for change button
    datelocChangeBtn.on('click', changeDateloc);

    // event handler for cancel button
    datelocFormCancel.on('click', cancelDatelocForm);

    // load them stars
    d3.json('/stars.json', drawSkyAndStars);
    
});

