// utilities for drawing star field

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

var isPointOnCircle = function(x, y, radius) {
    // determine whether a point is on the sky circle or not

    var xFromCenter = x - radius;
    var yFromCenter = radius - y;

    return Math.sqrt(xFromCenter**2 + yFromCenter**2) < radius;

}

var getCornersOnCircle = function(minX, minY, maxX, maxY, radius) {
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

var getFloatFromPixels = function(floatString) {
    // from a string like '2.978px', return the float 2.978

    return parseFloat(floatString.substring(0, floatString.length - 2))
}


var getConstLabelCoords = function(bound_verts, radius, labelWidth, labelHeight) {
    // return x, y object for label based on constellation bound vertices
    // the label position depends on the bounding rect and the position of the 
    // constellation in the svg

    var maxX, maxY, minX, minY;

    // get bounding rect
    // is there a better way to do this in js? 
    for (var i=0; i < bound_verts.length; i++) {
        var vert = bound_verts[i];

        // ignore negatives and over 400s
        var vertx = vert.x > 0 ? vert.x : 0;
        var verty = vert.y > 0 ? vert.y : 0;
        vertx = vertx < radius * 2 ? vertx : radius * 2;
        verty = verty < radius * 2 ? verty : radius * 2;

        if (maxX === undefined || vertx > maxX) { maxX = vertx; }
        if (maxY === undefined || verty > maxY) { maxY = verty; }
        if (minX === undefined || vertx < minX) { minX = vertx; }
        if (minY === undefined || verty < minY) { minY = verty; }
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