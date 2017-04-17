// for drawing the compass rose to show directions are reversed

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

var compassRoseGrp;

var rotateString = function(theta, compCent) {
    // return svg rotate translation for theta around the compass center
    return 'rotate(' + theta + ',' + compCent + ',' + compCent + ')';
};

var translateText = function(i, compCent) {
    // return translate compass text according to where in the sequence it is

    var theta = i * Math.PI / 2;
    var y = (compCent + 5) * (1 + Math.sin(theta)) - 5;
    var x = (compCent + 10) * (1 + Math.cos(theta)) - 10;

    return 'translate(' + x + ',' + y + ')';
};

var transitionCompassRing = function(elements, mouseIn) {
    // change fill color in array of elements on mouse over
    // mouseIn is true for mouseover, false for mouseout

    var oldClass = mouseIn ? 'compass' : 'compass-hover';
    var newClass = mouseIn ? 'compass-hover' : 'compass';

    for (var i=0; i<elements.length; i++) {
        elements[i].classed(oldClass, false).classed(newClass, true);
    }

}

var drawCompass = function() {
    // draw the rose
    // use globals skyRadius and svgContainer
    // sets global compassRoseGrp
        
    // remove compass if it already exists
    if (compassRoseGrp !== undefined) {
        compassRoseGrp.remove();
    }

    // important dimenstions for the compass
    var compassSize = skyRadius / 5;
    var compCent = compassSize / 2;
    var compNub = compassSize / 2 - compassSize / 8;

    var polyPath = d3.line()
        .x(function(d) { return d[0]; })
        .y(function(d) { return d[1]; });

    compassRoseGrp = svgContainer.append('g')
            .attr('id', 'compass-rose')
            .attr('class', 'compass compass-rose');

    var polyPoints = [[compCent, compCent],
                  [compCent, 0],
                  [compNub, compNub],
                  [compCent, compCent]];

    var compassLetterInfo = [{text: 'W', baseAlign: 'middle', anchor: 'start'},
                      {text: 'S', baseAlign: 'before-edge', anchor: 'middle'},
                      {text: 'E', baseAlign: 'middle', anchor: 'end'},
                      {text: 'N', baseAlign: 'after-edge', anchor: 'middle'}];

    // for tracking what color needs to be changed on mouseover
    var filledElements = Array();

    for (var i=0;i < 4;i++) {
        var compassSpike = compassRoseGrp.append('polygon')
                    .datum(polyPoints)
                    .attr("points",function(d) {return d.join(" ");})
                    // .attr('stroke', 'white')
                    // .attr('stroke-width', 1)
                    // .attr('fill', fillColor)
                    .attr('class', 'compass compass-spike')
                    .attr('transform', rotateString(i * 90, compCent));
        filledElements.push(compassSpike);

        var compassLetter = compassRoseGrp.append('text')
                    .datum(compassLetterInfo[i])
                    .text(function(d) {return d.text;})
                    .attr('x', 0)
                    .attr('y', 0)
                    .attr('transform', translateText(i, compCent))
                    .attr('text-anchor', function(d) {return d.anchor;})
                    .attr('alignment-baseline', function(d) {return d.baseAlign;})
                    // .attr('fill', fillColor)
                    .attr('class', 'compass compass-letter');
        filledElements.push(compassLetter);
    }

    // add a ring to make the group more cohesive for mousever and click
    var compassRing = compassRoseGrp.append('circle')
                    .attr('cx', compassSize / 2)
                    .attr('cy', compassSize / 2)
                    .attr('r', compassSize)
                    .attr('opacity', 0)

    // move the rose into position
    var xShift = skyRadius * 2 - compassSize;
    var yShift = compassSize / 3;
    var roseTranslation = 'translate(' + xShift + ',' + yShift + ')';
    compassRoseGrp.attr('transform', roseTranslation);

    // create effects
    compassRoseGrp.on('mouseover', function() { transitionCompassRing(filledElements, true); })
    compassRoseGrp.on('mouseout', function() { transitionCompassRing(filledElements, false); })
    compassRoseGrp.on('click', function() { populateDefinition('compass'); })

    // finally, define the global variable so this can be shown/hidden from 
    // other files

    compassRose = $('#compass-rose');

};
