// d3 for drawing constellations 
// pulls globals xxxx from main-d3.js


var drawConstellations = function(constData) {
    // draw constellation lines and boundaries
    // uses global skyObjects

// -- const bounds should be returned in skyData as a Polygon, and 
// -- const lines should be returned as a MultiLineString


// var geoLineString = {
//         "type": "Polygon",
//         "coordinates": [
//             [ -101.744384765625,   39.32155002466662  ],
//             [ -101.5521240234375,  39.330048552942415 ],
//             [ -101.40380859375,    39.330048552942415 ],
//             [ -101.33239746093749, 39.364032338047984 ],
//             [ -101.041259765625,   39.36827914916011  ],
//             [ -100.975341796875,   39.30454987014581  ],
//             [ -100.9149169921875,  39.24501680713314  ],
//             [ -100.843505859375,   39.16414104768742  ],
//             [ -100.8050537109375,  39.104488809440475 ],
//             [ -100.491943359375,   39.10022600175347  ],
//             [ -100.43701171875,    39.095962936305476 ],
//             [ -100.338134765625,   39.095962936305476 ],
//             [ -100.1953125,        39.027718840211605 ],
//             [ -100.008544921875,   39.01064750994083  ],
//             [ -99.86572265625,     39.00211029922512  ],
//             [ -99.6844482421875,   38.97222194853654  ],
//             [ -99.51416015625,     38.929502416386605 ],
//             [ -99.38232421875,     38.92095542046727  ],
//             [ -99.3218994140625,   38.89530825492018  ],
//             [ -99.1131591796875,   38.86965182408357  ],
//             [ -99.0802001953125,   38.85682013474361  ],
//             [ -98.82202148437499,  38.85682013474361  ],
//             [ -98.44848632812499,  38.84826438869913  ],
//             [ -98.20678710937499,  38.84826438869913  ],
//             [ -98.02001953125,     38.8782049970615   ],
//             [ -97.635498046875,    38.87392853923629  ]
//         ]
//     };

// // GeoJSON LineString Example Path Data
// geoPath(geoLineString);

// var lineStringPath = svgContainer
//   .append("path")
//     .attr("d", geoPath(geoLineString))
//     .style("stroke", "#FF00FF");

    var constellations = skyObjects.selectAll('g.constellation-group')
        .data(constData)
        .enter()
        .append('g')
        .attr('class', 'constellation-group')

        // don't display initially
        .attr('opacity', 0)

        ///////////////
        // mouseover //
        ///////////////

        // reveal boundaries and lines on mouseover
        .on('mouseover', function() { 
                  d3.select(this).transition()        
                    .duration(200)      
                    .style("opacity", 1);})

        .on('mouseout', function() { 
                  d3.select(this).transition()        
                    .duration(500)      
                    .style("opacity", 0);});


    //////////////////
    // sub elements //
    //////////////////

    // add sub-elements for each constellation
    constellations.each(function(d) {        

        var thisConst = d3.select(this);

        //////////////////////////
        // constellation bounds //
        //////////////////////////

        // TODO: find a better way of dealing with serpens/serpens cauda/serpens caput
        if (d.bound_verts.length > 0) {

            var constBoundsPolygon = { 
                geometry: {
                    type: 'Polygon',
                    coordinates: [d.bound_verts] // because of potential holes, this needs to be an array of arrays of arrays of points
                },
                type: 'Feature'
            }

            var constBounds = thisConst.append('path')
                                .datum(constBoundsPolygon)
                                .attr('class', 'constellation-bounds')
                                .attr('d', function(d) { return skyPath(d); })
        }

        /////////////////////////
        // constellation lines //
        /////////////////////////

        console.log(d);

        // TODO: find a better way of dealing with serpens/serpens cauda/serpens caput
        if (d.line_groups.length > 0) {

            var constLineMultiLine = { 
                geometry: {
                    type: 'MultiLineString',
                    coordinates: d.line_groups
                },
                type: 'Feature'
            }

            var constLines = thisConst.append('path')
                                .datum(constLineMultiLine)
                                .attr('class', 'constellation-line')
                                .attr('d', function(d) { return skyPath(d); })
        }


        /////////////////////////
        // constellation label //
        /////////////////////////

        // TODO: position this better



// # d3.geoBounds(object) <>

// Returns the spherical bounding box for the specified GeoJSON object. The bounding box is represented by a two-dimensional array: [[left, bottom], [right, top]], where left is the minimum longitude, bottom is the minimum latitude, right is maximum longitude, and top is the maximum latitude. All coordinates are given in degrees. (Note that in projected planar coordinates, the minimum latitude is typically the maximum y-value, and the maximum latitude is typically the minimum y-value.) This is the spherical equivalent of path.bounds.



    //     // text for constellation name label
    //     var constLabel = thisConst.append('text')
    //         .text(d.name)
    //         .attr('class', 'const-name');

    //     // position for label text
    //     var label_pos = getConstLabelCoords(d.bound_verts, skyRadius, 
    //                             getFloatFromPixels(constLabel.style('width')),
    //                             getFloatFromPixels(constLabel.style('height')));

    //     // apply calculated position to label
    //     constLabel.attr('x', label_pos.x)
    //               .attr('y', label_pos.y);


    });
}