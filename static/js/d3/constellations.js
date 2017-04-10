// d3 for drawing constellations 
// pulls globals skyObjects, skyTransform from d3-main.js

    // Copyright (c) 2017 Bonnie Schulkin

    // This file is part of My Heavens.

    // My Heavens is free software: you can redistribute it and/or modify it under
    // the terms of the GNU Affero General Public License as published by the Free
    // Software Foundation, either version 3 of the License, or (at your option)
    // any later version.

    // My Heavens is distributed in the hope that it will be useful, but WITHOUT
    // ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    // FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
    // for more details.

    // You should have received a copy of the GNU Affero General Public License
    // along with My Heavens. If not, see <http://www.gnu.org/licenses/>.


'use strict';

var isInverted = function(poly) {
    // determine if a polygon is inverted on the sky sphere

    // I tried doing this using d3.geoArea(poly) and skyPath.area(poly) --
    // neither of them worked consistently across all constellations. 
    //
    // This way -- using the screen area of the constellation and comparing it
    // to the total screen area -- seems somewhat hacky, but it works in all
    // cases.

    var bounds = skyPath.bounds(poly);
    var screenArea = (bounds[1][0] - bounds[0][0]) * (bounds[1][1] - bounds[0][1]);
    var totalScreenArea = Math.pow(2 * skyRadius, 2);

    return screenArea / totalScreenArea > 3/4;

};

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


        // special split serpens gets a multipolygon; all else get polygons
        var geoType = d.bound_verts.length > 1 ? 'MultiPolygon' : 'Polygon';
        var boundVerts = d.bound_verts.length > 1 ? [d.bound_verts] : d.bound_verts


        var constBoundsPolygon = {
            geometry: {
                type: geoType,
                coordinates: boundVerts
            },
            type: 'Feature'
        };

        // if (d.name === 'Octans') {
        //     debugger;
        // }


        // make sure we're getting the actual bounds polygon, and not the inverse
        if (isInverted(constBoundsPolygon)) {

            // TODO: make this into a function to avoid so much repeated code

            var reversedBounds = []
            for (var i=0; i<d.bound_verts.length; i++) {
                reversedBounds.push(d.bound_verts[i].slice().reverse());
            }

            reversedBounds = d.bound_verts.length > 1 ? [reversedBounds] : reversedBounds

            constBoundsPolygon = {
                geometry: {
                    type: geoType,
                    coordinates: reversedBounds
                },
                type: 'Feature'
            };
 
        }

        // don't bother drawing constellation if it's not visible
        // isVisible is defined in sky.js
        var boundsViz = isVisible(constBoundsPolygon);

        if (boundsViz && isInverted(constBoundsPolygon)) {

        // sometimes circumpolar constellations that aren't showing are
        // inverted with their bounds forwards or backwards
        // example: octans at rotation -228.63065300575627 -37.8715926

        // TODO: understand better what's going on here and/or record error on server via ajax

            // console.log('constellation ' + d.name + ' inverted in both directions. Skipping.')
            boundsViz = false;

        } 

        if (!boundsViz) {
            // this constellation isn't showing; remove it
            thisConst.remove();

        } else {

            var constBounds = thisConst.append('path')
                                .datum(constBoundsPolygon)
                                .attr('class', 'constellation-bounds')
                                .attr('d', function(d) { return skyPath(d); });

            /////////////////////////
            // constellation lines //
            /////////////////////////

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
                                .attr('d', function(d) { return skyPath(d); });


            /////////////////////////
            // constellation label //
            /////////////////////////

            var labelPos = getLabelPosition(constLineMultiLine, constBoundsPolygon)

            // text for constellation name label
            var constLabel = thisConst.append('text')
                .text(d.name)
                .attr('class', 'constellation-label sky-label')
                .attr('x', labelPos.x)
                .attr('y', labelPos.y)
                .attr('text-anchor', labelPos.textAnchor);

            // if (d.name === 'Octans') {
            //     debugger;
            // }
        }
    });
};

var getLabelPosition = function(constLineMultiLine, constBoundsPolygon) {
    // return an object with x, y, and textAnchor keys for positioning
    // constellation labels, based on constLineMultiLine and constBoundsPolygon

    // to store return data
    var labelPosition = {}

    // if you can see the lines, place the label relative to the lines; 
    // otherwise place relative to the bounds polygon
    var boundsObj = isVisible(constLineMultiLine) ? constLineMultiLine : constBoundsPolygon;

    // TODO: do a better job of positioning, for example, hydra (curled around 
    // bottom, but label is quite far away) on Berkeley April 2, 2017 at 
    // 12:00 AM 
    var bounds = skyPath.bounds(boundsObj);
    var minX = bounds[0][0];
    var minY = bounds[0][1];
    var maxX = bounds[1][0];
    var maxY = bounds[1][1];
    var padding = 20;

    labelPosition.y = (minY < skyRadius) ? maxY + padding : minY - padding;
    labelPosition.x = (maxX > 3 * skyRadius / 4) ? minX : (minX + maxX) / 2;
    labelPosition.textAnchor = (maxX < skyRadius) ? 'start' : 'end';

    return labelPosition;
}