'use strict';

////////
/// references
///
/// http://marcneuwirth.com/blog/2012/06/24/creating-the-earth-with-d3-js/  --earth with star background
/// https://github.com/d3/d3/blob/master/API.md#geographies-d3-geo  --d3-geo documentation
/// https://bost.ocks.org/mike/map/ --text labels
/// http://bl.ocks.org/d3noob/a22c42db65eb00d4e369 -- transitions to show text on mouseover

////////
// rotation reference: https://www.jasondavies.com/maps/rotate/
//                      https://bl.ocks.org/mbostock/4282586


///////////////////////////
// globals and functions //
///////////////////////////

// globals to use across functions
var sunMoonRadius, planetInfoDiv, sunInSky, svgContainer
var skySphere, skyProjection, skyPath, skyObjects, skyTransform, labelDatum
var skyRadius = 300 // for now


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

}


var addInfoWindowMouseOver = function(obj, d, infoLabel) {

// update infoLabel position and text when star or planet gets a mouseover
// adapted from http://bl.ocks.org/d3noob/a22c42db65eb00d4e369
// uses global skyTransform, defined in the drawSkyAndStars function
// TODO: make dimensions relative to radius, rather than hard-coded

    obj.on("mouseover", function() {   
            // snazzy fading in
            infoLabel.transition()        
                .duration(200)      
                .style("opacity", .9);   

            // add text and reposition   
            // with help from https://bost.ocks.org/mike/map/
            // TODO: make background color and/or make placement always on "globe"
            infoLabel.attr('dy', '-0.35em')
                .attr('dx', '0.35em')
                .attr('transform', skyTransform(d.ra, d.dec))
                .text(d.name);

    })               
    .on("mouseout", function() { infoLabel.transition()        
        .duration(500)      
        .style("opacity", 0);  
    });
}


////////////////////////////
// main printing function //
////////////////////////////


function drawSkyAndStars(error, starData) {
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

    console.log(starData);

    /////////////////////
    // handle warnings //
    /////////////////////

    // TODO: send warnings with star data


    // defined in sky.js
    drawSky();

    // defined in constellations.js
    drawConstellations(starData.constellations);

    // defined in stars.js
    drawStars(starData.stars);

}

