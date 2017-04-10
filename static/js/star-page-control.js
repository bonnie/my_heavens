// page control functions for stars.html

"use strict";

// jquery globals that will be initialized on document load
var datetimeRadio, changetimeRadio, datetimeInput, errorDiv, datelocInfoDiv,
    starfieldControlDiv, warnDiv, eclipticToggle, planetToggle, planetWarning,
    celestialInfoTable, datetimeFormGroup, datelocFormGroups, celestialInfoDiv,
    datelocChangeBtn, showStarsBtn, datelocForm, datelocInfoTable,
    datelocFormCancel, masterInfoDiv, celestialDivInstructions,
    celestialInfoHeader, datelocInfoHeader, compassRose, datelocFormInputs,
    starfieldDiv, celestialDefDiv, definableTerms, revealCheckboxes;

// global for skyRadius
var skyRadius;

// global for terms dictionary
var termDict;

var displayError = function(error) {

    errorDiv.show();
    errorDiv.html(error);

};

// success function for geocode in getLatLng (which is triggered on submit 
// button click)
var processFormInputs = function(latlng) {

    // clear previous errors
    errorDiv.empty().hide();

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
    var datetimeString = datelocInfo.dateString + ' at ' + datelocInfo.timeString;
    addInfoDivHeader(datelocInfoHeader, placeString, datetimeString);
    addDatelocTableRow('Latitude', datelocInfo.lat);
    addDatelocTableRow('Longitude', datelocInfo.lng);

};

var populateDefinition = function(term) {
    // populate the definition div for this term
    //
    // uses globals termDict, celestialDefDiv, addInfoDivHeader

    celestialDefDiv.show();
    var termInfo = termDict[term];

    term = termInfo.term === undefined ? term : termInfo.term;

    var defString = '<p class="definition">' + termInfo.definition;

    if (termInfo.wikipedia !== null) {
        defString += ' <span class="wiki-link"><a target="_blank" href="'
        defString += termInfo.wikipedia
        defString += '"">Wikipedia link</a></span>'
    }

    defString += '</p>'

    celestialDefDiv.empty();
    addInfoDivHeader(celestialDefDiv, term);
    celestialDefDiv.append(defString);
}

var addDefinitionOnclick = function() {
    // add the on click listener for the clickable-terms, which come and go from
    // the page frequently. 

    $('#celestial-data').on('click', '.term', function() {
        var term = $(this).html().toLowerCase();
        populateDefinition(term);
    });

}

var toggleNightMode = function() {

    // close the sidenav
    closeNav();

    var changeFrom, changeTo;

    if ($('.nightmode').length > 0) {
        changeFrom = 'nightmode';
        changeTo = 'daymode';
    } else {
        changeFrom = 'daymode';
        changeTo = 'nightmode';
    }

    $('.' + changeFrom).removeClass(changeFrom).addClass(changeTo);

}

$(document).ready(function() {

    // define some globals based on html ids
    datetimeRadio = $('input[name=datetime]:radio');
    changetimeRadio = $('#change-time');
    datetimeInput = $('#datetime-input');
    errorDiv = $('#error');
    starfieldControlDiv = $('#starfield-controls');
    warnDiv = $('#warn');
    starfieldDiv = $('#star-field');

    eclipticToggle = $('#ecliptic-toggle');
    planetToggle = $('#planet-toggle');
    revealCheckboxes = $('.reveal')

    planetWarning = $('#planet-warning');

    showStarsBtn = $('#show-stars');
    masterInfoDiv = $('#master-info-div');
    datetimeFormGroup = $('#datetime-form-group');

    datelocForm = $('#dateloc-form');
    datelocFormGroups = $('#dateloc-form .form-group');
    datelocFormInputs = $('#dateloc-form input');
    datelocFormCancel = $('#dateloc-form-cancel');

    celestialInfoDiv = $('#celestial-info');
    celestialInfoTable = $('#celestial-info .info-table');
    celestialInfoHeader = $('#celestial-info .info-header');
    celestialDivInstructions = $('#celestial-div-instructions').get(0);

    celestialDefDiv = $('#celestial-definitions');

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

    // hide error when someone changes form
    datelocFormInputs.on('change', function() { errorDiv.hide(); });

    // get dictionary terms
    $.get('/terms.json', function(result) {
        termDict = result;
        addDefinitionOnclick();
    });

    // load them stars
    d3.json('/stars.json', drawSkyAndStars);
    
});

