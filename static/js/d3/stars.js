// d3 for drawing stars
// pulls globals xxxx from main-d3.js

var setGlobalStarDataAndDraw = function(starDataResult) {
    // a callback function to set global starData from ajax and call drawStars

    starData = starDataResult;
    drawStars();
};


var drawStars = function(mode) {
    // draw the stars on the sphere of the sky
    // mode is a string that can either be omitted or set to 'noLabels'
    // It will be 'noLabels' when animating, to make animations faster

    // uses globals skyObjects, skyProjection, labelDatum

    // starData global was set by setGlobalStarDataAndDraw

    // One label that just gets repurposed depending on moused-over star,
    // since we're never going to be showing more than one star label at once
    // with help from https://bost.ocks.org/mike/map/
    var starLabel = skyObjects.append('text')
        .attr('class', 'star-label sky-label');

    // add the star groups
    var stars = skyObjects.selectAll('g.star-group')
                            .data(starData)
                            .enter()
                            .append('g')
                            .attr('class', 'star-group');

    // add sub-elements for each star
    stars.each(function(d) {

        var thisStar = d3.select(this);
        var starPoint = {
            geometry: {
                type: 'Point',
                coordinates: [d.ra, d.dec]
            },
            type: 'Feature',
            properties: {
                radius: (5 - d.magnitude) * 0.5
            }
        };

        // circle to represent star
        // since we're in d3 geo world, this needs to be a path with a point
        // geometry, not an svg circle
        var starCircle = thisStar.append('path')
                            .datum(starPoint)
                            .attr('class', 'star')
                            .attr('d', function(d){
                                skyPath.pointRadius(d.properties.radius);
                                return skyPath(d); })
                            .attr('fill', d.color)
                            .style('opacity', d.magnitude < 0 ? 1 : (5 - d.magnitude) / 5);


        if (mode !== 'noLabels' && d.name !== null) {
            // make a fixed-width, larger surrounding circle for the mouseover, as some stars are too 
            // small to mouse over effectively
            var surroundingStarCircle = thisStar.append('path')
                            .datum(starPoint)
                            .attr('d', function(d){
                                skyPath.pointRadius(4);
                                return skyPath(d); })
                            .attr('class', 'star-surround')
                            .style('opacity', 0);

            addInfoWindowMouseOver(surroundingStarCircle, d, starLabel);
        }
    });
}