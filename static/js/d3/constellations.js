// d3 for drawing constellations 
// pulls globals skyObjects, skyTransform from d3-main.js

'use strict';

var drawConstellations = function(constData) {
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

            var constBoundsPolygon = { 
                geometry: {
                    type: 'Polygon',
                    coordinates: [d.bound_verts] // because of potential holes, this needs to be an array of arrays of arrays of points
                },
                type: 'Feature'
            }

            var constBounds = thisConst.append('path')
                                .datum(constBoundsPolygon)
                                .attr('class', 'constellation-bounds')
                                .attr('d', function(d) { return skyPath(d); })
        }

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
            }

            var constLines = thisConst.append('path')
                                .datum(constLineMultiLine)
                                .attr('class', 'constellation-line')
                                .attr('d', function(d) { return skyPath(d); })
        }


        /////////////////////////
        // constellation label //
        /////////////////////////

        // TODO: position this better



// # d3.geoBounds(object) <>

// Returns the spherical bounding box for the specified GeoJSON object. The bounding box is represented by a two-dimensional array: [[left, bottom], [right, top]], where left is the minimum longitude, bottom is the minimum latitude, right is maximum longitude, and top is the maximum latitude. All coordinates are given in degrees. (Note that in projected planar coordinates, the minimum latitude is typically the maximum y-value, and the maximum latitude is typically the minimum y-value.) This is the spherical equivalent of path.bounds.


        // perhaps go back to what I do with stars and planets, one text box to rule them all, that gets transformed? 

        // I feel like I should be able to use centroid or bounding box here, but when
        // I do the debugger below, both of these return [NaN, NaN]: 

        // skyPath.centroid(constBounds)
        // skyPath.centroid(constLines)

        // the equivalent bounds functions return arrays whose items are Infinity or -Infinity

        // if (d.name === 'Cassiopeia') {
        //     debugger;
        // }

        // get the centroid of the constellation lines
        var constCent = skyPath.centroid(constLineMultiLine);

        // TODO: what to do about labels when constellation positions rotate 
        // must calculate dynamically somehow
        if (!isNaN(constCent[0])) {

            // text for constellation name label
            var constLabel = thisConst.append('text')
                .text(d.name)
                .attr('class', 'constellation-label sky-label')
                .attr('x', constCent[0])
                .attr('y', constCent[1]);
        }

    });
}