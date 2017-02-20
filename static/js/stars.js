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


    // create constellations
    var constellations = constGroup.selectAll("g")
        .data(constInfo)
        .enter()
        .append("g")
        .attr("class", "constellation")
        .attr("data-name", function(d) { return d.name });


    constellations.each(function(d) {

        // create constellation boundaries
        constBounds = d3.select(this).append("path")
          .attr("class", "const-bounds")
          .attr("d", getLine(d.bound_verts))
          .attr("stroke", "#000099")
          .attr("stroke-width", 1)

          // to keep bounds from stepping on each other
          .attr("fill-opacity", 0);


        // create constellation line groups
        constLineGroups = d3.select(this).selectAll("g.constline-group")
            .data(d.line_groups)
            .enter()
            .append("g")
            .attr("class", "constline-group")

        // add lines for each group
        constLineGroups.each(function(d, i) {

                d3.select(this).append("path")
                    .attr("class", "constline")
                    .attr("d", getLine(d))
                    .attr("stroke", "#333333")
                    .attr("stroke-width", 2)

                    // these aren't meant to be closed shapes
                    .attr("fill-opacity", 0)

            });

    })
                

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



