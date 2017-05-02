// d3 for drawing stars
// pulls globals renderSkyObjectList, getRadiusFromMag, starData from main-d3.js

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

var setGlobalStarDataAndDraw = function(starDataResult) {
    // a callback function to set global starData from ajax and call drawStars

    starData = starDataResult;
    drawStars();
};

var drawStars = function(mode, lambda, phi) {
    // draw the stars on the sphere of the sky
    // mode is a string that can either be omitted or set to 'transition'
    // It will be 'transition' when animating, to make animations faster
    //
    // uses global starData

    var starParams = {listData: starData,
                      classPrefix: 'star',
                      radiusFunction: getRadiusFromMag,
                      mode: mode,
                      lambda: lambda,
                      phi: phi};

    renderSkyObjectList(starParams);

};

var redrawStars = function() {
    // for redrawing stars upon changing to / from night mode

    $('.star-group').remove()
    drawStars();
}

var moveStars = function() {
    svgContainer.select('.star-group').each(function(d) {
        d3.select(this).attr('transform', function(d) {skyTransform(d.ra, d.dec)});
    });
}