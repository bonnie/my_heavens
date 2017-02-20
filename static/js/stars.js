// to make a path from a list of xs and ys
// this code adapted from https://www.dashingd3js.com/svg-paths-and-d3js
// (they use v3 and I'm using v4, so I had to change d3.svg.line to d3.line,
// and remove the .interpolate method)
var getLine = d3.line()
                    .x( function(d) { return d.x } )
                    .y( function(d) { return d.y } )

// get star data and display it
d3.json('/stars.json', printStarData);

function printStarData(starData) {

    console.log(starData);

    var constInfo = starData.constellations;

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

    // set up constellations
    var constGroup = svgContainer.append("g")
                                    .attr("id", "cons");


    // add basic data to constellations
    var constellations = constGroup.selectAll("g")
        .data(constInfo)
        .enter()
        .append("g")
        .attr("class", "constellation");


    // create constellation boundaries
    constellations.each(function(d) {
        d3.select(this).append("path")
          .attr("class", "const-bounds")
          .attr("d", getLine(d.bound_verts))
          .attr("stroke", "#333333")
          .attr("stroke-width", 2)
    })
                

    //// I think the below will make more sense once I figure out how to do one boundary for each constellation, 
    //// not all constellation boundaries for each constellation

    // create groups for constellation lines
    // constLineGroups = constellations.selectAll("g.const-line-group")
    //     .data(constInfo)
    //     .enter()
    //     .append("g")
    //     .attr("class", "const-line-group")


    // // create paths for each line in the groups
    // constLines = constLineGroups.selectAll("path.const-line")
    //     .enter()
    //     .append("path")
    //     .attr("class", "const-line")


    // // draw constellation lines
    // constLines.attr("d", function(d, i) { return getLine(d.group_lines[i]) })
    //     .attr("stroke", "#333333")
    //     .attr("stroke-width", 2)



    // add the stars
    var stars = svgContainer.selectAll("circle.star")
                            .data(starData.stars)
                            .enter()
                            .append('circle');

    var starAttributes = stars
                        .attr('cx', function(d) { return d.x })
                        .attr('cy', function(d) { return d.y })
                        .attr('r', function(d) { return (5 - d.magnitude) * 0.5 })
                        .attr('fill', function(d) { return d.color })
                        .style("opacity", function(d) { return d.magnitude < 0 ? 1 : (5 - d.magnitude) / 5 });
}



