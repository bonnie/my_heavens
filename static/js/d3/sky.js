// d3 for drawing the sphere of the sky 
// pulls globals xxxx from main-d3.js

'use strict';

var daySkyColor = '#4169E1';


function printSkyBackground(planets) {
    // print the sky background as light blue or a dark gradient, depending on 
    // whether the sun is in the sky 

    // uses global svgContainer, daySkyColor, skyRadius
    // sets global sunInSky

    // will be gradient or light blue depending on whether it's daytime
    var skyFill;

    sunInSky = false;

    // check to see if the sun is in the sky
    for (var i=0; i < planets.length; i++) {
        if (planets[i].name == 'Sun') {
            sunInSky = true;
        }
    }

    if (sunInSky) {
        // If so, make background lighter blue
        skyFill = daySkyColor;

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
                              .attr('cx', skyRadius)
                              .attr('cy', skyRadius)
                              .attr('r', skyRadius)
                              .style("fill", skyFill);
}

var drawSky = function(skyData) {
    ////////////////////////
    // sphere for the sky //
    ////////////////////////

    // define globals:
        // skyProjection
        // skyPath
        // skyTransform
        // skySphere
        // skyObjects

    // and draw the sphere of the sky


    // create the projection for the sphere of the sky
    skyProjection = d3.geoOrthographic()
        .scale(skyRadius)
        .translate([skyRadius, skyRadius])
        .clipAngle(90)
        .precision(0.1)
        // .rotate(([0, 360 - 37, 0]));
        .rotate(([90, 331, 0]));

    // create a path generator for the sphere of the sky
    // globally scoped
    skyPath = d3.geoPath()
        .projection(skyProjection);

    // for transforming ra/dec coords onto sky sphere
    // globally scoped
    skyTransform = function(ra, dec) {      
         return 'translate(' + skyProjection([ra, dec]) + ')';
    };


    // the background sphere of the sky
    // globally scoped. TODO: does this need to be global? should it get its own function? 
    skySphere = svgContainer.append("path")
      .datum({type: "Sphere"})
      .attr("id", "sky-sphere")
      .attr("d", skyPath)
      .attr('opacity', 1)
      .attr('fill', 'black'); // for now...


    // for zooming, make a group for all the contents of the skySphere
    // globally scoped
    skyObjects = svgContainer.append('g')
        .attr('id', 'all-sky-objects');

    // show the background
    // printSkyBackground(skyData.planets);

};

var rotateSky = function(lambda, phi) {
    // rotate the sky for the lambda (based on latitude) and 
    // phi (based on longitude / time)

    // uses global skyProjection, 

    // calculate duration based on distance to go
    var oldRotation = skyProjection.rotate();
    var oldLambda = oldRotation[0];
    var oldPhi = oldRotation[1];
    var durTime = Math.sqrt(Math.pow((oldLambda - lambda), 2) + Math.pow((oldPhi - phi), 2)) * 15;
    console.log(durTime);


    // adapted from http://bl.ocks.org/KoGor/5994960
    // TODO: make less choppy -- maybe don't redraw everything, just transform it...?
    d3.transition()
      .duration(durTime)
      .ease(d3.easeLinear)
      .tween("rotate", function() {
        var rotation = d3.interpolate(skyProjection.rotate(), [lambda, phi]);
        return function(t) {
          skyProjection.rotate(rotation(t));

          // at every stage, clear the sky and start over
          $('#all-sky-objects').empty();

          // draw all the objects
          // setSunInSky();
          // printSkyBackground();

          // draw stars without labels and only bright stars (for faster transition)
          drawStars('transition');

            };
          })
      .on('end', function() {

            // finally, draw constellations and redraw the stars with labels on top of them
            $('#all-sky-objects').empty();

            // defined in d3-main.js
            drawSkyObjects();
        });

};