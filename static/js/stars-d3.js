'use strict';

///////////////////////////
// globals and functions //
///////////////////////////

// when form is submitted (code in geocode.js)
var getStars = function(lat, lng, datetime) {

    // clear previous starfield
    $('#star-field').empty();

    // d3.request needs data in a query string format
    var data = 'lat=' + lat;
    data += '&lng=' + lng;
    if (datetime !== undefined) {
        data += '&datetime=' + datetime;
    }

    d3.request('/stars.json')
        .mimeType("application/json")
        .response(function(xhr) { return JSON.parse(xhr.responseText); })
        .header("Content-Type","application/x-www-form-urlencoded")
        // .on('progress', function()) // TODO: show progress bar!
        .post(data, printStarData);

}

// update starInfoDiv position and text when star gets a mouseover
// adapted from http://bl.ocks.org/d3noob/a22c42db65eb00d4e369
// TODO: make dimensions relative to radius, rather than hard-coded

var showInfoWindow = function(d, windowDiv) {

    // snazzy fading in
    windowDiv.transition()        
        .duration(200)      
        .style("opacity", .9);   

    // add text and reposition   
    windowDiv.html(d.name) // for now  
        .style("left", (d.x + 2) + "px")     
        .style("top", (d.y - 20) + "px");    
}

var hideInfoWindow = function(windowDiv) {

    windowDiv.transition()        
        .duration(500)      
        .style("opacity", 0);   

}
// END: adaptation from http://bl.ocks.org/d3noob/a22c42db65eb00d4e369


// to make a path from a list of xs and ys
// this code adapted from https://www.dashingd3js.com/svg-paths-and-d3js
// (they use v3 and I'm using v4, so I had to change d3.svg.line to d3.line,
// and remove the .interpolate method)
var getLine = d3.line()
                    .x( function(d) { return d.x } )
                    .y( function(d) { return d.y } )


////////////////
// d3 drawing //
////////////////

function printSkyBackground(svgContainer, radius, planets) {

    // will be gradient or light blue depending on whether it's daytime
    var skyFill;

    var sunInSky = false;

    // check to see if the sun is in the sky
    for (var i=0; i < planets.length; i++) {
        if (planets[i].name == 'Sun') {
            sunInSky = true;
        }
    }

    if (sunInSky) {
        // If so, make background lighter blue
        skyFill = '#4169E1'

    } else {
        // print the radial gradient for the sky background
        // adapted from https://bl.ocks.org/pbogden/14864573a3971b640a55
        var radialGradient = svgContainer.append("defs")
            .append("radialGradient")
            .attr("id", "radial-gradient");

        radialGradient.append("stop")
            .attr("offset", "85%")
            .attr("stop-color", 'black');

        radialGradient.append("stop")
            .attr("offset", "95%")
            .attr("stop-color", "#101035");

        radialGradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", "#191970");

        skyFill = "url(#radial-gradient)";
    }

    var background = svgContainer.append('circle')
                              .attr('cx', radius)
                              .attr('cy', radius)
                              .attr('r', radius)
                              .style("fill", skyFill);
}

var revealPlanets = function() {

    var trans1time = 1000
    var trans2time = 1000

    // disable the button
    $('#reveal-planets').attr('disabled', 'disabled');

    // select planets
    var planets = d3.selectAll('circle.planet');

    // do fun zoom transitions
    planets.transition()        
        .duration(trans1time)      
        .attr('r', function(d) { return d3.select(this).attr('r') * 5 });

    planets.transition()
        .delay(trans1time)
        .duration(trans2time)
        .attr('r', function(d) { return d3.select(this).attr('r') });

    // re-enable the button
    setTimeout(function() {
                    $('#reveal-planets').removeAttr('disabled')
                }, 
                trans1time + trans2time);

}


function printStarData(starData) {
    // success function for d3 ajax call to get star data

    console.log(starData);

    var constInfo = starData.constellations;

    var svgBodySelection = d3.select('#star-field');

    // make a place to draw the stars
    var svgContainer = svgBodySelection.append('svg')
                                    .attr('width', 2 * starData.radius)
                                    .attr('height', 2 * starData.radius);

    // show the background
    printSkyBackground(svgContainer, starData.radius, starData.planets);

    // create constellations
    var constellations = svgContainer.selectAll('g.constellation-group')
        .data(constInfo)
        .enter()
        .append('g')
        .attr('class', 'constellation-group')

        // don't display initially
        .attr('opacity', 0)

        // reveal boundaries and lines on mouseover
        .on('mouseover', function() { 
                  d3.select(this).transition()        
                    .duration(200)      
                    .style("opacity", 1);})

        .on('mouseout', function() { 
                  d3.select(this).transition()        
                    .duration(500)      
                    .style("opacity", 0);});


    // add sub-elements for each constellation
    constellations.each(function(d) {

        var thisConst = d3.select(this);

        //////////////////////////
        // constellation bounds //
        //////////////////////////


        // create constellation boundaries
        var constBounds = thisConst.append('path')
          .attr('class', 'const-bounds')
          .attr('d', getLine(d.bound_verts))
          .attr('stroke', '#000099')
          .attr('stroke-width', 1)

          // to keep bounds from stepping on each other
          .attr('fill-opacity', 0);


        /////////////////////////
        // constellation lines //
        /////////////////////////

        // create constellation line groups
        var constLineGroups = thisConst.selectAll('g.constline-group')
            .data(d.line_groups)
            .enter()
            .append('g')
            .attr('class', 'constline-group');


        // add lines for each group
        constLineGroups.each(function(d, i) {

                d3.select(this).append('path')
                    .attr('class', 'constline')
                    .attr('d', getLine(d))
                    .attr('stroke', '#333333')
                    .attr('stroke-width', 2)

                    // these aren't meant to be closed shapes
                    .attr('fill-opacity', 0);

            });


        /////////////////////////
        // constellation label //
        /////////////////////////

        // text for constellation name label
        var constLabel = thisConst.append('text')
            .text(d.name)
            .attr('class', 'const-name');

        // position for label text
        var label_pos = getConstLabelCoords(d.bound_verts, starData.radius, 
                                getFloatFromPixels(constLabel.style('width')),
                                getFloatFromPixels(constLabel.style('height')));

        // apply calculated position to label
        constLabel.attr('x', label_pos.x)
                  .attr('y', label_pos.y);


    });
                

    ///////////
    // stars //
    ///////////

    // One div for every star info window
    var starInfoDiv = d3.select("body").append("div")   
        .attr("class", "star-info info")               
        .style("opacity", 0)
        .style('border-radius', '4px');            


    // add the star groups
    var stars = svgContainer.selectAll('g.star-group')
                            .data(starData.stars)
                            .enter()
                            .append('g')
                            .attr('class', 'star-group');

    // add sub-elements for each star
    stars.each(function(d) {

        var thisStar = d3.select(this);

        // circle to represent star
        var starCircle = thisStar.append('circle')
                             .attr('cx', d.x)
                             .attr('cy', d.y)
                             .attr('r', (5 - d.magnitude) * 0.5)
                             .attr('fill', d.color)
                             .attr('class', 'star')
                             .style('opacity', d.magnitude < 0 ? 1 : (5 - d.magnitude) / 5);

        if (d.name !== null) {
            // make a surrounding circle for the mouseover, as some stars are too 
            // small to mouse over effectively
            var surroundingStarCircle = thisStar.append('circle')
                             .attr('cx', d.x)
                             .attr('cy', d.y)
                             .attr('r', 4)
                             .attr('class', 'star-surround')
                             .style('opacity', 0);


            surroundingStarCircle.on("mouseover", 
                                        function(d) { showInfoWindow(d, starInfoDiv);})               
                                 .on("mouseout", 
                                        function(d) { hideInfoWindow(starInfoDiv);});
        }
    });

    /////////////
    // planets //
    /////////////

    // One div for every planet info window
    var planetInfoDiv = d3.select("body").append("div")   
        .attr("class", "planet-info info")               
        .style("opacity", 0)
        .style('border-radius', '4px');            

    // create circle for planet
    var planets = svgContainer.selectAll('circle.planet')
                            .data(starData.planets)
                            .enter()
                            .append('circle')
                            .attr('class', 'planet');

    // add details
    planets.each(function(d) {
        
        var planet = d3.select(this).attr('cx', d.x)
                        .attr('cy', d.y)
                        .attr('fill', d.color)
                        .on("mouseover", function(d) { showInfoWindow(d, planetInfoDiv);})               
                        .on("mouseout", function(d) { hideInfoWindow(planetInfoDiv);});

        if (d.name === 'Sun') {

            planet.attr('class', 'sun')
                  .attr('r', starData.radius / 42);
            
        } else if (d.name === 'Moon') {

            planet.attr('class', 'moon')
                  .attr('r', starData.radius / 42);

        } else {
            // let smaller planets be sized according to magnitude
            planet.attr('r', (5 - d.magnitude) * 0.5);
        }

    
    });

    // show the starfield controls 
    $('#starfield-controls').show();

    // attach 'reveal planets' button to the revealPlanets function
    $('#reveal-planets').on('click', revealPlanets);

}

