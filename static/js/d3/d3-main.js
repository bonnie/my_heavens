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
/// https://bl.ocks.org/mbostock/a7bdfeb041e850799a8d3dce4d8c50c8 --polygon interior
/// https://github.com/mourner/suncalc --js library for calculating things like twilight and moon phases

////////
// rotation reference: https://www.jasondavies.com/maps/rotate/
//                      https://bl.ocks.org/mbostock/4282586


///////////////////////////
// globals and functions //
///////////////////////////

// globals to use across functions
var sunMoonRadius, planetInfoDiv, svgContainer, skyBackground;
var skySphere, skyProjection, skyPath, skyObjects, skyTransform, eclipticPath;
var starData, constData, planetData, sunData, moonData;
var planetHighlights; // for the identifier circles for the planets
var skyRadius = 350;  // for now


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


// make a background for the sky 
skyBackground = svgContainer.append('circle')
                              .attr('cx', skyRadius)
                              .attr('cy', skyRadius)
                              .attr('r', skyRadius)
                              .attr('id', 'sky-background');


// define the sky gradient just once, not every time we print the sky background
// used in drawSkyBackground in solarsystem.js
// adapted from https://bl.ocks.org/pbogden/14864573a3971b640a55
var radialGradient = svgContainer.append("defs")
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


var populateInfoDiv = function(d) {
    // reveal and populate the info div when someone clicks on an item
    
    // show the div
    $('#celestial-info').show();

    // populate the headers
    $('#celestial-name-value').html(d.name);
    if (d.name !== d.celestialType) { $('#celestial-type-value').html(d.celestialType); }

    // empty the info table
    celestialInfoTable.empty();

    // populate table info
    addInfoTableRow('Magnitude', d.magnitude);
    addInfoTableRow('Distance', d.distance + ' ' + d.distanceUnits);

    if (d.celestialType === 'planet' || d.celestialType === 'moon') {
        addInfoTableRow('Phase', d.phase + '%'); }

    if (d.celestialType !== 'star' || d.name == 'Sun') {
        addInfoTableRow('Rose at', d.prevRise);
        addInfoTableRow('Will set at', d.nextSet);
    }

};

var addInfoTableRow = function(rowName, rowValue) {
    // add a row to the info table (celestialInfoTable)

    var rowString = '<tr><td class="info-table-name text-right">';
    rowString += rowName;
    rowString += '</td><td>';
    rowString += rowValue;
    rowString += '</td></tr>';

    celestialInfoTable.append(rowString);

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

    // show ecliptic toggle button and attach event listener
    $('#starfield-controls').show()
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

var getRadiusFromMag = function(d) {
    return (5 - d.magnitude) * 0.5;
};

var renderSkyObjectList = function(params) {
    // render a list of sky objects
    // for use in drawing stars and planets
    //
    // params is an object with these keys:
    //      listData (e.g. starData)
    //      classPrefix (e.g. star)
    //      mode (e.g. transition)
    //      radiusFunction (e.g. function(d) {return (5 - d.magnitude) * 0.5})

    // uses global skyObjects

    // One label that just gets repurposed depending on moused-over item,
    // since we're never going to be showing more than one item label at once
    var itemLabel = skyObjects.append('text')
        .attr('class', params.classPrefix + '-label sky-label');

    var groupClass = params.classPrefix + '-group';

    // add the item groups
    var items = skyObjects.selectAll('g.' + groupClass)
                            .data(params.listData)
                            .enter()
                            .append('g')
                            .attr('class', groupClass);

    // add sub-elements for each star
    items.each(function(d) {

        var objParams = {group: d3.select(this),
                     mode: params.mode,
                     d: d,
                     radius: params.radiusFunction(d),
                     classPrefix: params.classPrefix,
                     itemLabel: itemLabel};

        renderSkyObject(objParams);
    });


};

var renderSingleSkyObject = function(params) {
    // render a list of sky objects
    // for use in drawing stars and planets
    //
    // params is an object with these keys:
    //      d (e.g. sunData)
    //      classPrefix (e.g. sun)
    //      mode (e.g. transition)
    //      radius (eg sunMoonRadius)

    // uses global skyObjects

    // make a group for this obj and its label

    var itemGroup = skyObjects.append('g')
                            .attr('class', params.classPrefix + '-group');

    // One label that just gets repurposed depending on moused-over item,
    // since we're never going to be showing more than one item label at once
    // TODO: make function for this for less repitition
    var itemLabel = itemGroup.append('text')
        .attr('class', params.classPrefix + '-label sky-label');

    var objParams = {group: itemGroup,
                     mode: params.mode,
                     d: params.d,
                     radius: params.radius,
                     classPrefix: params.classPrefix,
                     itemLabel: itemLabel};

    return renderSkyObject(objParams);

};

var renderSkyObject = function(params) {
    // render one sky object
    // for use in drawing individual stars and planets, sun, moon
    //
    // params is an object with these keys:
    //      group (group to which to attach this item)
    //      mode (e.g. transition)
    //      classPrefix (class for individual object, e.g. star)
    //      d (data object, expected to have ra, dec, magnitude, name, color)
    //      radiusFunction (radius function for this object)
    //      itemLabel (svg text element for object label)

    // for easier reference
    var d = params.d;

    // don't bother drawing dim items during transition
    if (params.mode !== 'transition' || d.magnitude < 3) {
        var itemPoint = {
            geometry: {
                type: 'Point',
                coordinates: [d.ra, d.dec]
            },
            type: 'Feature',
            properties: {
                radius: params.radius
            }
        };

        if (params.mode !== 'transition' && !isVisible(itemPoint)) {
            // remove the star if it's not visible and don't bother going on
            // skip this step if the mode is transition, as it slows things down a tad
            params.group.remove();

        } else {

            // circle to represent item
            // since we're in d3 geo world, this needs to be a path with a point
            // geometry, not an svg circle
            var itemCircle = params.group.append('path')
                                .datum(itemPoint)
                                .attr('class', params.objClass)
                                .attr('d', function(d){
                                    skyPath.pointRadius(d.properties.radius);
                                    return skyPath(d); })
                                .attr('fill', d.color)
                                .style('opacity', d.magnitude < 0 ? 1 : (5 - d.magnitude) / 5);


            if (params.mode !== 'transition' && d.name !== null) {
                // make a fixed-width, larger surrounding circle for the
                // mouseover, as some items are too  small to mouse over
                // effectively
                var surroundingCircle = params.group.append('path')
                                .datum(itemPoint)
                                .attr('d', function(d){
                                    skyPath.pointRadius(params.radius < 4 ? 4 : params.radius);
                                    return skyPath(d); })
                                .attr('class', params.objClass + '-surround')
                                .style('opacity', 0);

                addInfoMouseOverAndClick(surroundingCircle, d, params.itemLabel);
            }
        }
        // for sun, return the point for ease in telling whether it's visible
        return itemPoint;
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

    var t = d3.transition()
            .duration(500)
            .ease(d3.easeLinear);

    p.obj.transition(t)
        .attr('opacity', 1)
      .transition(t)
        .attr('opacity', finalOpacity)
      .on('start', function() { p.trigger.attr('disabled', 'disabled'); })
      .on('end', function() {
        p.trigger.removeAttr('disabled');});
};

