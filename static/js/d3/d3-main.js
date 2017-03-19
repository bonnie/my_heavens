'use strict';

////////
/// references
///
/// http://marcneuwirth.com/blog/2012/06/24/creating-the-earth-with-d3-js/  --earth with star background
/// https://github.com/d3/d3/blob/master/API.md#geographies-d3-geo  --d3-geo documentation
/// https://bost.ocks.org/mike/map/ --text labels
/// http://bl.ocks.org/d3noob/a22c42db65eb00d4e369 --transitions to show text on mouseover
/// https://www.dashingd3js.com/lessons/d3-geo-path --example usage of d3 path objects
/// https://bl.ocks.org/wwymak/dcdd12937bd4643cd9b3 --animated drag d3 sphere
/// http://bl.ocks.org/KoGor/5994960 --sphere rotation animation
/// https://github.com/d3/d3-transition --transitions documentation

////////
// rotation reference: https://www.jasondavies.com/maps/rotate/
//                      https://bl.ocks.org/mbostock/4282586


///////////////////////////
// globals and functions //
///////////////////////////

// globals to use across functions
var sunMoonRadius, planetInfoDiv, sunInSky, svgContainer;
var skySphere, skyProjection, skyPath, skyObjects, skyTransform, labelDatum;
var starData, constData, ssData;
var skyRadius = 300;  // for now


////////////////
// create svg //
////////////////

// start by drawing svg, as a placeholder
var svgBodySelection = d3.select('#star-field');

// make a place to draw the stars
// svgContainer is globally scoped
svgContainer = svgBodySelection.append('svg')
                                .attr('width', 2 * skyRadius)
                                .attr('height', 2 * skyRadius);


var showAjaxError = function(error) {
    // display error from ajax call

    // define error
    var errorTxt = error.srcElement.statusText;
    if (errorTxt === 'INTERNAL SERVER ERROR') {
        errorTxt = 'The server could not complete this request.';
        errorTxt += ' Please contact the system administrator.';
    }

    // show the div and add the error
    errorDiv.show();
    errorDiv.html(errorTxt);

    // console.log(error);  // debugging

};


var addInfoWindowMouseOver = function(obj, d, infoLabel) {

// update infoLabel position and text when star or planet gets a mouseover
// adapted from http://bl.ocks.org/d3noob/a22c42db65eb00d4e369

// uses global skyTransform, defined in the drawSkyAndStars function
// uses global skyRadius from d3-main.js

// TODO: make dimensions relative to radius, rather than hard-coded

    obj.on("mouseover", function() {
            // snazzy fading in
            infoLabel.transition()
                .duration(200)
                .style("opacity", 0.9);

            // figure out the best position for the label so it doesn't go off
            // the circle of the sky
            var textAnchor, dxMultiplier, dyMultiplier;
            var coords = skyProjection([d.ra, d.dec]);
            var x = coords[0];
            var y = coords[1];

            if (x < skyRadius) {
                textAnchor = 'start';
                dxMultiplier = 1;
            } else {
                textAnchor = 'end';
                dxMultiplier = -1;
            }

            if (y < skyRadius / 2) {
                dyMultiplier = 2;
            } else {
                dyMultiplier = -1;
            }

            // add text and reposition   
            // with help from https://bost.ocks.org/mike/map/
            // TODO: make background color and/or make placement always on "globe"
            infoLabel.attr('dy', (0.35 * dyMultiplier) + 'em')
                .attr('dx', (0.35 * dxMultiplier) + 'em')
                .attr('transform', skyTransform(d.ra, d.dec))
                .attr('text-anchor', textAnchor)
                .text(d.name);



    })
    .on("mouseout", function() { infoLabel.transition()
        .duration(500)
        .style("opacity", 0);
    });
};


////////////////////////////
// main printing function //
////////////////////////////


var drawSkyAndStars = function(error, starDataResult) {
    // success function for d3 ajax call to get star data

    // clear previous errors and warnings
    // errorDiv and warnDiv defined in star-page-control.js
    errorDiv.empty().hide();
    warnDiv.empty().hide();

    //////////////////
    // handle error //
    //////////////////

    if (error) {
        showAjaxError(error);
        return;
    }

    console.log(starDataResult);

    /////////////////////
    // handle warnings //
    /////////////////////

    // TODO: send warnings with star data


    /////////////////
    // set globals //
    /////////////////

    // these need to be global for redrawing sky when sphere animates
    constData = starDataResult.constellations;
    starData = starDataResult.stars;

    // defined in sky.js
    drawSky();

    drawSkyObjects();

};

var drawSkyObjects = function() {
    // draw sky objects either at beginning of page load or after change in data

    // defined in constellations.js
    drawConstellations();

    // defined in stars.js
    drawStars();

    // on intial page load, there will be no planet data
    // TODO: use html5 geolocation and current date/time to set initial sky
    //      conditions 
    if (ssData) {
        drawPlanets();
    }

};

