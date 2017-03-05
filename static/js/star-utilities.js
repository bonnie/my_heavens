// utilities for drawing star field

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