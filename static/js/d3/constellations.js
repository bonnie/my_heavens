// d3 for drawing constellations 
// pulls globals skyObjects, skyTransform from d3-main.js

'use strict';

var drawConstellations = function() {
    // draw constellation lines and boundaries
    // uses global skyObjects

    var constellations = skyObjects.selectAll('g.constellation-group')
        .data(constData)
        .enter()
        .append('g')
        .attr('class', 'constellation-group')

        // don't display initially
        .attr('opacity', 0)

        ///////////////
        // mouseover //
        ///////////////

        // reveal boundaries and lines on mouseover
        .on('mouseover', function() { 
                  d3.select(this).transition()
                    .duration(200)
                    .style("opacity", 1);})

        .on('mouseout', function() {
                  d3.select(this).transition()
                    .duration(500)
                    .style("opacity", 0);});


    //////////////////
    // sub elements //
    //////////////////

    // add sub-elements for each constellation
    constellations.each(function(d) {

        var thisConst = d3.select(this);

        //////////////////////////
        // constellation bounds //
        //////////////////////////

        // TODO: find a better way of dealing with serpens/serpens cauda/serpens caput
        if (d.bound_verts.length > 0) {


            // reverse the bounds polygons if we're in the southern hemisphere
            // so d3 understands we want the constellations, not their inverse
            


            var constBoundsPolygon = {
                geometry: {
                    type: 'Polygon',
                    coordinates: [d.bound_verts] // because of potential holes, this needs to be an array of arrays of arrays of points
                },
                type: 'Feature'
            };

            // don't bother drawing constellation if it's not visible
            // isVisible is defined in sky.js
            var boundsViz = isVisible(constBoundsPolygon);
            if (boundsViz) {

                var constBounds = thisConst.append('path')
                                    .datum(constBoundsPolygon)
                                    .attr('class', 'constellation-bounds')
                                    .attr('d', function(d) { return skyPath(d); });
            } else {
                // this constellation isn't showing; remove it
                thisConst.remove();
            }
        }

        if (boundsViz) {

            /////////////////////////
            // constellation lines //
            /////////////////////////

            // TODO: find a better way of dealing with serpens/serpens cauda/serpens caput
            if (d.line_groups.length > 0) {

                var constLineMultiLine = {
                    geometry: {
                        type: 'MultiLineString',
                        coordinates: d.line_groups
                    },
                    type: 'Feature'
                };

                var constLines = thisConst.append('path')
                                    .datum(constLineMultiLine)
                                    .attr('class', 'constellation-line')
                                    .attr('d', function(d) { return skyPath(d); })
            }


            /////////////////////////
            // constellation label //
            /////////////////////////

            var boundsObj = isVisible(constLineMultiLine) ? constLineMultiLine : constBoundsPolygon;

            // get better positioning for the constellation labels along the edges
            // TODO: do a better job of positioning, esp for constellation off the middle right 
            // TODO: separate out into a function.
            var bounds = skyPath.bounds(boundsObj);
            var minX = bounds[0][0];
            var minY = bounds[0][1];
            var maxX = bounds[1][0];
            var maxY = bounds[1][1];
            var padding = 20;

            var y = (minY < skyRadius) ? maxY + padding : minY - padding;
            var x = (maxX > 3 * skyRadius / 4) ? minX : (minX + maxX) / 2;
            var textAnchor = (maxX < skyRadius) ? 'start' : 'end';

            // text for constellation name label
            var constLabel = thisConst.append('text')
                .text(d.name)
                .attr('class', 'constellation-label sky-label')
                .attr('x', x)
                .attr('y', y);

        }

        // if (d.name === 'Octans') {
        //     debugger;
        // }


    });
};