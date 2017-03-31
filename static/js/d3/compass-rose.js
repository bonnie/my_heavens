// for drawing the compass rose to show directions are reversed

'use strict';

// variable for the compass ring that shows on mouseover to indicate clickability
var compassRing;

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

var transitionCompassRing = function(opacity) {
    // show/hide the compass ring on mouse over

    compassRing.transition()
        .duration(400)
        .style("opacity", opacity);

}

var drawCompass = function() {
    // draw the rose
    // use globals skyRadius and svgContatiner
        
    // important dimenstions for the compass
    var compassSize = skyRadius / 5;
    var compCent = compassSize / 2;
    var compNub = compassSize / 2 - compassSize / 8;

    var polyPath = d3.line()
        .x(function(d) { return d[0]; })
        .y(function(d) { return d[1]; });

    var compassRoseGrp = svgContainer.append('g')
            .attr('id', 'compass-rose');

    var polyPoints = [[compCent, compCent],
                  [compCent, 0],
                  [compNub, compNub],
                  [compCent, compCent]];

    var compassLetters = [{text: 'W', baseAlign: 'middle', anchor: 'start'},
                      {text: 'S', baseAlign: 'before-edge', anchor: 'middle'},
                      {text: 'E', baseAlign: 'middle', anchor: 'end'},
                      {text: 'N', baseAlign: 'after-edge', anchor: 'middle'}];

    for (var i=0;i < 4;i++) {
        compassRoseGrp.append('polygon')
                    .datum(polyPoints)
                    .attr("points",function(d) {return d.join(" ");})
                    // .attr('stroke', 'white')
                    // .attr('stroke-width', 1)
                    .attr('fill', 'white')
                    .attr('transform', rotateString(i * 90, compCent));

        compassRoseGrp.append('text')
                    .datum(compassLetters[i])
                    .text(function(d) {return d.text;})
                    .attr('x', 0)
                    .attr('y', 0)
                    .attr('transform', translateText(i, compCent))
                    .attr('text-anchor', function(d) {return d.anchor;})
                    .attr('alignment-baseline', function(d) {return d.baseAlign;})
                    .attr('fill', 'white')
                    .attr('class', 'compass-letter');
    }

    // move the rose into position
    var xShift = skyRadius * 2 - compassSize;
    var yShift = compassSize / 3;
    var roseTranslation = 'translate(' + xShift + ',' + yShift + ')';
    compassRoseGrp.attr('transform', roseTranslation);

    // add a ring that will show on mouseover to indicate something will happen
    // when you click. Don't add this to the group, so it can be shown and hidden
    // independently
    compassRing = svgContainer.append('circle')
                    .attr('cx', xShift + compassSize / 2)
                    .attr('cy', yShift + compassSize / 2)
                    .attr('r', compassSize)
                    .attr('opacity', 0)
                    .attr('fill-opacity', 0)
                    .attr('stroke', 'white')
                    .attr('stroke-width', '2')
                    .attr('id', 'compass-rose-ring')

    compassRing.on('mouseover', function() { transitionCompassRing(1); })
    compassRing.on('mouseout', function() { transitionCompassRing(0); })
    compassRing.on('click', function() { populateDefinition('compass'); })

    // finally, define the global variable so this can be shown/hidden from 
    // other files

    compassRose = $('#compass-rose');

};
