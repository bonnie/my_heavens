'use strict';

// get star data and display it
d3.json('/stars.json', printStarData);

///////////////////////////
// globals and functions //
///////////////////////////

// to make a path from a list of xs and ys
// this code adapted from https://www.dashingd3js.com/svg-paths-and-d3js
// (they use v3 and I'm using v4, so I had to change d3.svg.line to d3.line,
// and remove the .interpolate method)
var getLine = d3.line()
                    .x( function(d) { return d.x } )
                    .y( function(d) { return d.y } )

function isPointOnCircle(x, y, radius) {
    // determine whether a point is on the sky circle or not

    var xFromCenter = x - radius;
    var yFromCenter = radius - y;

    return Math.sqrt(xFromCenter**2 + yFromCenter**2) < radius;

}

function getCornersOnCircle(minX, minY, maxX, maxY, radius) {
    // return booleans for each corner on the circle (tl, tr, bl, br)
    // true if corner is on the circle, false if it's not

    var corners = {}

    corners.tl = isPointOnCircle(minX, minY, radius);
    corners.tr = isPointOnCircle(maxX, minY, radius);
    corners.bl = isPointOnCircle(minX, maxY, radius);
    corners.br = isPointOnCircle(maxX, maxY, radius);

    // console.log( corners);

    return corners;

}

function getFloatFromPixels(floatString) {
    // from a string like '2.978px', return the float 2.978

    return parseFloat(floatString.substring(0, floatString.length - 2))
}


function getConstLabelCoords(bound_verts, radius, labelWidth, labelHeight) {
    // return x, y object for label based on constellation bound vertices
    // the label position depends on the bounding rect and the position of the 
    // constellation in the svg

    var maxX, maxY, minX, minY;

    // get bounding rect
    // is there a better way to do this in js? 
    for (var i=0; i < bound_verts.length; i++) {
        var vert = bound_verts[i];

        if (maxX === undefined || vert.x > maxX) { maxX = vert.x; }
        if (maxY === undefined || vert.y > maxY) { maxY = vert.y; }
        if (minX === undefined || vert.x < minX) { minX = vert.x; }
        if (minY === undefined || vert.y < minY) { minY = vert.y; }
    }

    // how much to offset the label from the boundary rectangle
    var offset = radius / 80

    // default horizontally at the middle
    var labelX = (maxX + minX) / 2;

    // position the label at the top or bottom based on where the constellation
    // falls on the chart
    var avgY = (minY + maxY) / 2
    var labelY = avgY > radius ? minY + offset : maxY - offset;

    // see which corners of the bounds are on the circle
    var corners = getCornersOnCircle(labelX - labelWidth / 2, 
                                     labelY, 
                                     labelX + labelWidth / 2,
                                     labelY + labelHeight,
                                     radius);



    // if lower left or upper left is off, move label to right
    if (corners.bl === false && corners.tl === false) { 
        // console.log('left off'); 
        labelX = maxX - offset; }


    // if lower right or upper right is off, move label to left
    else if (corners.br === false && corners.tr === false) { 
        // console.log('right off'); 
        labelX = minX + offset; }


    return { x: labelX, y: labelY };


}

////////////////
// d3 drawing //
////////////////

function printSkyBackground(svgContainer, radius) {
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

    var background = svgContainer.append('circle')
                              .attr('cx', radius)
                              .attr('cy', radius)
                              .attr('r', radius)
                              .style("fill", "url(#radial-gradient)");
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
    printSkyBackground(svgContainer, starData.radius);

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


    })
                

    ///////////
    // stars //
    ///////////

    // One div for every star info window
    var starInfoDiv = d3.select("body").append("div")   
        .attr("class", "star-info")               
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

        // info window for star
        // var starInfo = thisStar.append('p')
        //                      .attr('x', d.x)
        //                      .attr('y', d.y)
        //                      .attr('fill', '#444444')
        //                      .attr('height', '100px')
        //                      .attr('width', '100px')
        //                      .attr('class', 'star-info')
        //                      .attr('visibility', 'hidden');


        // update starInfoDiv position and text when star gets a mouseover
        // adapted from http://bl.ocks.org/d3noob/a22c42db65eb00d4e369
        // TODO: make dimensions relative to radius, rather than hard-coded

        if (d.name !== null) {
            starCircle.on("mouseover", function() { 

                // snazzy fading in
                starInfoDiv.transition()        
                    .duration(200)      
                    .style("opacity", .9);   

                // add text and reposition   
                starInfoDiv.html(d.name) // for now  
                    .style("left", (d.x + 2) + "px")     
                    .style("top", (d.y - 20) + "px");    
                })               

            .on("mouseout", function() {       
                starInfoDiv.transition()        
                    .duration(500)      
                    .style("opacity", 0);   
            });
        }
        // END: adaptation from http://bl.ocks.org/d3noob/a22c42db65eb00d4e369

    });

}

