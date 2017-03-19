// d3 for drawing stars
// pulls globals xxxx from main-d3.js

var drawStars = function(starData) {
    // draw the stars on the sphere of the sky
    // uses globals skyObjects, skyProjection, labelDatum


    // One label that just gets repurposed depending on moused-over star,
    // since we're never going to be showing more than one star label at once
    // labelDatum is globally scoped, defined in drawStarData
    // var starInfoLabel = skyObjects.append("path")
    //     .datum(labelDatum)   
    //     .attr("class", "star-info info")               
    //     .style("opacity", 0) // to start anyway
    //     .style('border-radius', '4px');            


    // One label that just gets repurposed depending on moused-over star,
    // since we're never going to be showing more than one star label at once
    // with help from https://bost.ocks.org/mike/map/
    var starLabel = skyObjects.append('text')
        .attr('class', 'star-label sky-label')

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


        if (d.name !== null) {
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