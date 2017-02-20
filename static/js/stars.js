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
    var constellations = svgContainer.append("g")
                                    .attr("id", "cons");


    // add data to constellations
    var g = constellations.selectAll("g")
        .data(starData.constellations)
        .enter()
        .append("g");


    // create paths constellation boundaries
    constBounds = g.selectAll("path")
        .data(starData.constellations)
        .enter()
        .append("path")


    // draw constellation boundaries
    constBounds.attr("class", "const-bounds")
        .attr("d", function(d) { return getLine(d.bound_verts) })
        // .attr("d", getLine({x: 10, y:10}, {x:20, y:20}))

        // works!!
        // the second arg is a result of doing this in the terminal with a debugger right at the beginning of printStarData: 
        // bounds = starData.constellations[0].bound_verts
        // getLine(bounds)
        // .attr("d", "M339.8019412114568,528.4672000165192L344.1320518476296,527.4231098992378L367.69759784975133,520.2687459222661L388.4405671779828,511.8732234007942L387.0781535583861,509.6091686586589L412.29378363098056,496.9539805966417L397.01821366983916,467.8405839566501L395.6455119875311,468.3340656915737L393.07222087985497,461.4673144025827L389.68128884478426,462.52788727418124L381.66814054957274,430.19234622190015L380.65199831820644,430.33714152948437L369.20830660951583,431.88562446965307L370.12317984101196,437.5163325858095L359.2936522217372,439.08146704336724L358.9334573222166,436.8821981014901L346.67533215970917,438.3652109536258L347.58287688496847,443.9592048537573L354.3610262374083,443.0449899245852L356.07993564559024,451.7149872126686L357.1035268088501,451.54063989428863L359.9975699320602,463.2930128169436L358.97162088219574,463.509980696122L362.29482825940846,474.56468607637845L326.97092959341217,481.66274229991933L339.530071547254,517.3855482981743L335.2606885207184,518.3175807608449")


        .attr("stroke", "#333333")
        .attr("stroke-width", 2)


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



