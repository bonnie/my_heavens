
// get star data and display it
d3.json('/stars.json', printStarData);

function printStarData(starData) {

    var svgBodySelection = d3.select("body");

    // make a place to draw the stars
    var svgContainer = svgBodySelection.append("svg")
                                    .attr("width", starData.radius)
                                    .attr("height", starData.radius);

    // add the stars
    var stars = svgContainer.selectAll("circle")
                            .data(starData.stars)
                            .enter()
                            .append('circle');

    var starAttributes = stars
                        .attr('cx', function(d) {return d.x})
                        .attr('cy', function(d) {return d.y})
                        .attr('r', function(d) {return 4 - d.magnitude})
                        .attr('fill', 'black')
}



