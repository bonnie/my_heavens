// good reference: https://www.dashingd3js.com/creating-svg-elements-based-on-data

d3.json('/static/data.json', printStarData);

function printStarData(starData) {
  // d3 code
  console.log(starData);

    var stars = svgContainer.selectAll("circle")
                            .data(starData)
                            .enter()
                            .append('circle');


    var starAttributes = stars
                        .attr('cx', function(d) {return d.x})
                        .attr('cy', function(d) {return d.y})
                        .attr('r', function(d) {return 5-d.magnitude})
}


var svgBodySelection = d3.select("body");

var svgContainer = svgBodySelection.append("svg")
                               .attr("width", 400)
                                .attr("height", 600);

// var circleSelection = svgSelection.append("circle")
//                                   .attr("cx", 25)
//                                   .attr("cy", 25)
//                                   .attr("r", 25)
//                                   .style("fill", "purple");

console.log('hiya!');

