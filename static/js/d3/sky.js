// d3 for drawing the sphere of the sky 
// pulls globals xxxx from main-d3.js

'use strict';


function printSkyBackground(sunInSky) {
    // print the sky background as light blue or a dark gradient, depending on 
    // whether the sun is in the sky 
    // sunInSky is a boolean indicating whether sun is visible or not

    // uses global skyBackground and element #radial-gradient from d3-main.js

    // will be gradient or light blue depending on whether it's daytime
    var daySkyColor = '#4169E1';
    var skyFill = sunInSky ? daySkyColor : "url(#radial-gradient)";
    skyBackground.style("fill", skyFill);

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
        .clipAngle(90)
        .precision(0.1)
        // .rotate(([0, 360 - 37, 0]));
        // .rotate([92, 331, 0]); // this is a bad one for inverted constellation bounds


    // create a path generator for the sphere of the sky
    // globally scoped
    skyPath = d3.geoPath()
        .projection(skyProjection);

    // for transforming ra/dec coords onto sky sphere
    // globally scoped
    skyTransform = function(ra, dec) {      
         return 'translate(' + skyProjection([ra, dec]) + ')';
    };

    // print the background
    printSkyBackground();

    // for zooming, make a group for all the contents of the skySphere
    // globally scoped
    skyObjects = svgContainer.append('g')
        .attr("clip-path", "url(#sky-clip)")
        .attr('id', 'all-sky-objects');


};

var rotateSky = function(lambda, phi) {
    // rotate the sky for the lambda (based on latitude) and 
    // phi (based on longitude / time)

    // uses global skyProjection, 

    console.log('rotating to', lambda, phi);

    // planet rings are going to be removed during transition
    // do it deliberately here first]
    // TODO: this doesn't work. Reveal planets hides them after this code runs, and doesn't toggle the button.
    // if (planetsRevealed === true) {
    //     planetsRevealed = false;
    //     planetRevealBox.html('Reveal planets');
    // }


    // calculate duration based on distance to go
    var oldRotation = skyProjection.rotate();
    var oldLambda = oldRotation[0];
    var oldPhi = oldRotation[1];
    var durTime = Math.sqrt(Math.pow((oldLambda - lambda), 2) + Math.pow((oldPhi - phi), 2)) * 15;
    // console.log(durTime);


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
          if (eclipticToggle.is(':checked')) { drawEcliptic(); }

          // draw the background and sun/moon/planets without labels
          drawSolarSystem('transition');

          // draw stars without labels and only bright stars (for faster transition)
          drawStars('transition');

        };
      })
      .on('start', function() {
        // disable reveal checkboxes
        revealCheckboxes.attr('disabled', 'disabled');
      })
      .on('end', function() {

            // finally, draw constellations and redraw the stars with labels on top of them
            $('#all-sky-objects').empty();

            // defined in d3-main.js
            drawSkyObjects();

            // re-enable reveal checkboxes
            revealCheckboxes.removeAttr('disabled');

        });

};

var drawEcliptic = function() {
    // draw the line of the ecliptic in the sky. It will be hidden until
    // revealed with a button click
    //
    // uses global skyObjects, skyPath
    //
    // for reference: https://en.wikipedia.org/wiki/Ecliptic

    // var ecliptic = d3.geoCircle()
    //     .center([90, 90 - 23.4])
    //     .radius(90); // sets the circle radius to the specified angle in degrees


    // ecliptic path goes from equinox to lowest point to equinox to highest
    // point I could do this with a circle, but then there's an ugly ring around
    // the sky where the circle completes -- much more visually appealing to do
    // it with a line
    var eclipticPathCoords = [[0,0], [90, -23.4], [180,0], [270, 23.4], [0,0]];

    var eclipticPolygon = {
                geometry: {
                    type: 'LineString',
                    coordinates: eclipticPathCoords
                },
                type: 'Feature'
    };

    var overallOpacity = eclipticToggle.is(':checked') ? 0.6 : 0;

    eclipticPath = skyObjects.append('path')
      .datum(eclipticPolygon)
      .attr("d", function(d) { return skyPath(d); })
      .attr('stroke', 'red')
      .attr('stroke-width', 2)
      .attr('fill-opacity', 0)
      .attr('opacity', overallOpacity)
      .attr('id', 'ecliptic');
};


var toggleEcliptic = function() {
    // a callback function to show / hide the ecliptic
    // uses opacityTransition from d3-main.js

    var params = {
      trigger: eclipticToggle,
      obj: eclipticPath
    };
    opacityTransition(params);

};

var isVisible = function(obj) {
    // given an object, determine whether it's visible in the current sky projection

    var corners = skyPath.bounds(obj);

    for (var i=0;i<=1;i++) {
        for (var j=0;j<=1;j++) {

        // if this corner is on the sky, return true
        var pt = corners[i][j];
        if (pt !== Infinity &&
            pt !== -Infinity &&
            !isNaN(pt)) {

                return true;
            }
        }
    }

    // if we haven't yet returned true, return false
    return false;
    
};
