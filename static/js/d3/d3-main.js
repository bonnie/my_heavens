'use strict';

    // Copyright (c) 2017 Bonnie Schulkin

    // This file is part of My Heavens.

    // My Heavens is free software: you can redistribute it and/or modify it
    // under the terms of the GNU Affero General Public License as published by
    // the Free Software Foundation, either version 3 of the License, or (at
    // your option) any later version.

    // My Heavens is distributed in the hope that it will be useful, but WITHOUT
    // ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    // FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
    // License for more details.

    // You should have received a copy of the GNU Affero General Public License
    // along with My Heavens. If not, see <http://www.gnu.org/licenses/>.


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
/// https://bl.ocks.org/mbostock/a7bdfeb041e850799a8d3dce4d8c50c8 --polygon interior
/// https://github.com/mourner/suncalc --js library for calculating things like twilight and moon phases

////////
// rotation reference: https://www.jasondavies.com/maps/rotate/
//                      https://bl.ocks.org/mbostock/4282586


///////////////////////////
// globals and functions //
///////////////////////////

// globals to use across functions
var sunMoonRadius, planetInfoDiv, svgContainer, svgDefs, skyBackground, skyCircle;
var skySphere, skyProjection, skyPath, skyObjects, skyTransform, eclipticPath;
var starData, constData, planetData, sunData, moonData, dateLocData;
var planetHighlights; // for the identifier circles for the planets
var compassRoseGrp;


////////////////
// create svg //
////////////////

$(document).ready(function() {

    // start by drawing svg, as a placeholder
    var svgBodySelection = d3.select('#star-field');

    // make a place to draw the stars
    // svgContainer is globally scoped
    svgContainer = svgBodySelection.append('svg')
                                    .attr('class', 'star-circle');

    // make a background for the sky 
    skyBackground = svgContainer.append('circle')
                                .attr('stroke-width', 3)
                                .attr('stroke-color', 'black')
                                .attr('id', 'sky-background')
                                .attr('class', 'sky-background');


    // for svg definitions
    svgDefs = svgContainer.append("defs")

    // make a clip path so points don't appear off the edge of the sky
    var skyClipPath = svgDefs.append('svg:clipPath')
                             .attr('id', 'sky-clip')

    skyCircle = skyClipPath.append('circle')
                           .attr('id', 'sky-clip-path')

    // define the sky gradient just once, not every time we print the sky background
    // used in drawSkyBackground in solarsystem.js
    // adapted from https://bl.ocks.org/pbogden/14864573a3971b640a55
    var radialGradient = svgDefs
                .append("radialGradient")
                .attr("id", "radial-gradient");

            radialGradient.append("stop")
                .attr("offset", "85%")
                .attr("stop-color", 'black');

            radialGradient.append("stop")
                .attr("offset", "93%")
                .attr("stop-color", "#101035");

            radialGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "#191970");

    // resize the svg on window resize
    $(window).resize(svgSetDimensions);

});


var svgSetDimensions = function() {
    // redraw the svg if the sky radius has changed
    //
    // uses globals skyRadius, svgContainer, skyCircle, compassRoseGrp, 
    //    skyProjection, 

    // calculate the sky radius based on the window size
    skyRadius = getSkyRadius();

    svgContainer.attr('width', 2.25 * skyRadius)
                .attr('height', 2 * skyRadius + 30); // account for 15 padding top and bottom

    skyCircle.attr('cx', skyRadius)
               .attr('cy', skyRadius)
               .attr('r', skyRadius)

    skyBackground.attr('cx', skyRadius)
               .attr('cy', skyRadius)
               .attr('r', skyRadius)

    // the d3 sky sphere
    if (skyProjection !== undefined) {
        skyProjection.scale(skyRadius)
            .translate([skyRadius, skyRadius])
    }

    // finally, draw constellations and redraw the stars with labels on top of them
    redrawSkyObjects();
    drawCompass();

}

var redrawSkyObjects = function() {
    // erase and redraw the sky
    $('#all-sky-objects').empty();
    drawSkyObjects();
}

var getSkyRadius = function() {
    // return sky radius based on the available width / height
    //
    // uses global jquery obj starfieldDiv

    var ht = $(window).height() / 2;
    var wd = starfieldDiv.width() / 2;

    return Math.min(ht, wd) - 15; // 15 for padding

}

var showAjaxError = function(error) {
    // display error from ajax call

    // define error
    var errorTxt = error.srcElement.statusText;

    if (error.srcElement.readyState === 4) { // srcElement is the XMLHttpRequest
        // network error
        errorTxt = 'Could not connect to server. Please try again later.';
    }
    else if (errorTxt === 'INTERNAL SERVER ERROR') {
        errorTxt = 'The server could not complete this request.';
        errorTxt += ' Please contact the system administrator.';
    }

    // show the div and add the error
    errorDiv.show();
    errorDiv.html(errorTxt);

    // show the form again
    datelocForm.show();

    // console.log(error);  // debugging

};


var addInfoMouseOverAndClick = function(obj, d, infoLabel) {
// make a couple event handlers for this object:
// 1. update info div when clicked
// 2. update infoLabel position and text when star or planet gets a mouseover
// adapted from http://bl.ocks.org/d3noob/a22c42db65eb00d4e369


// uses global skyTransform, defined in the drawSkyAndStars function
// uses global skyRadius from d3-main.js

    obj.on("mouseover", function() {
            // snazzy fading in
            infoLabel.transition()
                .duration(200)
                .style("opacity", 0.9);

            var labelPos = findLabelPosition(d);

            // add text and reposition   
            // with help from https://bost.ocks.org/mike/map/
            // TODO: make background color and/or make placement always on "globe"
            infoLabel.attr('dy', (0.35 * labelPos.dyMultiplier) + 'em')
                .attr('dx', (0.35 * labelPos.dxMultiplier) + 'em')
                .attr('transform', skyTransform(d.ra, d.dec))
                .attr('text-anchor', labelPos.textAnchor)
                .text(d.name);

    })
    .on("mouseout", function() {
        infoLabel.transition()
        .duration(500)
        .style("opacity", 0);
    })
    .on('click', function() { populateInfoDiv(d); });
};

var findLabelPosition = function(d) {
    // figure out the best position for a label so it doesn't go off
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

    var labelPos = {textAnchor: textAnchor,
                dxMultiplier: dxMultiplier,
                dyMultiplier: dyMultiplier};

    return labelPos;
};


////////////////////////////
// main printing function //
////////////////////////////


var drawSkyAndStars = function(error, starDataResult) {
    // success function for d3 ajax call to get star data

    //////////////////
    // handle error //
    //////////////////

    if (error) {
        showAjaxError(error);
        return;
    }

    // console.log(starDataResult);

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

    // attach event listener to ecliptic checkbox
    eclipticToggle.on('click', toggleEcliptic);

};

var drawSkyObjects = function() {
    // draw sky objects either at beginning of page load or after change in data

    // draw ecliptic first, so that everything else is on top of it
    drawEcliptic();

    // defined in constellations.js
    drawConstellations();

    // defined in stars.js
    drawStars();

    if (planetData !== undefined) {
        // on intial page load, there will be no planet data.
        // TODO: use html5 geolocation and current date/time to set initial sky
        //      conditions 
        drawSolarSystem();
    }

};

var opacityTransition = function(p) {
    // do an opacity transition with the specified params
    //
    // p is a parameters object with these keys: 
    //      trigger (checkbox that triggered this transition; e.g. planetTrigger)
    //      obj (svg object to show/hide; e.g. planetHighlights)


    // determine whether to turn the feature on or off
    var finalOpacity = p.trigger.is(':checked') ? 0.5 : 0;
    var duration = p.trigger.is(':checked') ? 500 : 300;

    var t = d3.transition()
            .duration(duration)
            .ease(d3.easeLinear);

    p.obj.transition(t)
        .attr('opacity', 1)
      .transition(t)
        .attr('opacity', finalOpacity)
      .on('start', function() { p.trigger.attr('disabled', 'disabled'); })
      .on('end', function() {
        p.trigger.removeAttr('disabled');});
};

