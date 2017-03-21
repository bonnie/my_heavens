// d3 for drawing stars
// pulls globals renderSkyObjectList, getRadiusFromMag, starData from main-d3.js

'use strict';

var setGlobalStarDataAndDraw = function(starDataResult) {
    // a callback function to set global starData from ajax and call drawStars

    starData = starDataResult;
    drawStars();
};

var drawStars = function(mode) {
    // draw the stars on the sphere of the sky
    // mode is a string that can either be omitted or set to 'transition'
    // It will be 'transition' when animating, to make animations faster
    //
    // uses global starData

    var starParams = {listData: starData,
                      classPrefix: 'star',
                      radiusFunction: getRadiusFromMag,
                      mode: mode};

    renderSkyObjectList(starParams);
};