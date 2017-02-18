
// get star data and display it
d3.json('/stars.json', printStarData);

function printStarData(starData) {

    var svgBodySelection = d3.select("body");

    // make a place to draw the stars
    var svgContainer = svgBodySelection.append("svg")
                                    .attr("width", 2 * starData.radius)
                                    .attr("height", 2 * starData.radius);

    // show the background
    background = svgContainer.append('circle')
                              .attr('cx', starData.radius)
                              .attr('cy', starData.radius)
                              .attr('r', starData.radius)
                              .attr('fill', 'black')

    // add the stars
    var stars = svgContainer.selectAll("circle.star")
                            .data(starData.stars)
                            .enter()
                            .append('circle');

    var starAttributes = stars
                        .attr('cx', function(d) {return d.x})
                        .attr('cy', function(d) {return d.y})
                        .attr('r', function(d) {return (5 - d.magnitude) * 0.75})
                        .attr('fill', function(d) {return d.color})
}



