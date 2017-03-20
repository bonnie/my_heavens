// d3 for drawing planets (including sun/moon)
// pulls globals xxxx from main-d3.js


var revealPlanets = function() {
    // make planets grow and shrink to highlight their position(s)
    // TODO: label planets during reveal
    // TODO: post message (in error div?) if no planets are visible 
    //        e.g.  berkeley 1/1/2017 1:00 AM

    var trans1time = 1000;
    var trans2time = 1000;

    // disable the button
    $('#reveal-planets').attr('disabled', 'disabled');

    // select planets
    var planets = d3.selectAll('circle.planet');

    // do fun zoom transitions
    planets.transition()
        .duration(trans1time)
        .attr('r', function(d) { return d3.select(this).attr('r') * 5; });

    planets.transition()
        .delay(trans1time)
        .duration(trans2time)
        .attr('r', function(d) { return d3.select(this).attr('r'); });

    // re-enable the button
    setTimeout(function() {
                    $('#reveal-planets').removeAttr('disabled');
                },
                trans1time + trans2time);

};


var rotateAndDrawSolarSystem = function(locationResponse) {
  // callback for getting data related to location and time 
  // (rotation and planet data)

  console.log(locationResponse);

  // first rotate
  rotateInfo = locationResponse.rotation;
  rotateSky(rotateInfo.lambda, rotateInfo.phi);

  // then set global ss data and moon data
  ssData = locationResponse.planets;
  moonData = locationResponse.moon;

  // then draw planets
  drawPlanets();

};

//////////////////////////////////////////
// functions to draw planets, moon, sun //
//////////////////////////////////////////


var drawPlanets = function() {
    // draw planets on sky sphere
    // uses globals skySphere, skyProjection, sunMoonRadius

    // the radius for the sun and the moon
    // sunMoonRadius is globally scoped
    sunMoonRadius = skyRadius / 42;

    // One div for every planet info window
    // planetInfoDiv is globally scoped
    planetInfoDiv = d3.select("body").append("div")
        .attr("class", "planet-info info")
        .style("opacity", 0)
        .style('border-radius', '4px');

    // create group for planet
    var planets = svgContainer.selectAll('g.planet')
                            .data(ssData)
                            .enter()
                            .append('g')
                            .attr('class', 'planet-group');

    // add details
    planets.each(function(d) {
        
        var thisPlanet = d3.select(this);

        var planet = thisPlanet.append('circle')
                        .attr('cx', d.x)
                        .attr('cy', d.y)
                        .attr('fill', d.color)
                        .attr('class', 'planet');

        var planetRadius;
        if (d.name === 'Sun') {

            planetRadius = sunMoonRadius;
            planet.attr('class', 'sun')
                  .attr('r', planetRadius);
            
        } else {
            // let smaller planets be sized according to magnitude
            planetRadius = (5 - d.magnitude) * 0.5;
            planet.attr('r', planetRadius);
        }

        // make a surrounding circle for tiny planets
        // (I'm looking at you, mercury)

        var surroundingPlanetCircle = thisPlanet.append('circle')
                        .attr('cx', d.x)
                        .attr('cy', d.y)
                        .attr('r', planetRadius < 4 ? 4 : planetRadius)
                        .attr('opacity', 0);

        addInfoWindowMouseOver(surroundingPlanetCircle, d, d.name, planetInfoDiv);


    
    });
};


var drawMoon = function(moonData) {
  // simluate the phase of the moon based on colong, using a half-lit sphere
  // append moon to svg parameter

  // uses globals sunMoonData, planetInfoDiv, sunInSky, daySkyColor and svgContainer

  // TODO: rotate the moon appropriately! 

  if (moonData === null) {
    // the moon isn't out; nothing to draw
    return;
  }

  // create the projection
  var moonProjection = d3.geoOrthographic()
      .scale(sunMoonRadius) // this determines the size of the moon
      .translate([d.x, d.y]) // moon coords here
      .clipAngle(90)
      .precision(0.1)
      .rotate([0, 0, d.rotation]); // rotate the moon so the lit part points to the sun

  // create a path generator
  var moonPath = d3.geoPath()
      .projection(moonProjection);

  // create the moon sphere
  var moon = svgContainer.append("path")
      .datum({type: "Sphere"})
      .attr("id", "moon-sphere")
      .attr("d", moonPath)
      .attr('opacity', 0);


  // create the lit hemisphere
  var litHemisphere = d3.geoCircle()
          // sets the circle center to the specified point [longitude, latitude] in degrees
          // 0 degrees is on the left side of the sphere
          .center([90 - d.colong, 0])
          .radius(90); // sets the circle radius to the specified angle in degrees

  // project the lit hemisphere onto the moon sphere
  svgContainer.append('path')
      .datum(litHemisphere)
      .attr("d", moonPath)
      .attr('fill', 'white')
      .attr('stroke', 'white')
      .attr('stroke-width', 1)
      .attr('class', 'lit-moon');

  addInfoWindowMouseOver(moon, d, planetInfoDiv);

};

var drawSolarSystem = function(error, ssData) {
    // success function for planet data from planets.json

    // clear previous errors and warnings
    // errorDiv and warnDiv defined in star-page-control.js
    errorDiv.empty().hide();
    warnDiv.empty().hide();

    //////////////////
    // handle error //
    //////////////////

    if (error) {
        showAjaxError(error);
        return;
    }

    /////////////
    // planets //
    /////////////

    // drawPlanets(ssData.planets);

    //////////
    // Moon //
    //////////

    // drawMoon(ssData.moon);


    //////////////
    // controls //
    //////////////

    // re-enable the "show stars" button
    $('#show-stars').removeAttr('disabled');

    // show the starfield controls 
    $('#starfield-controls').show();

    // attach 'reveal planets' button to the revealPlanets function
    $('#reveal-planets').on('click', revealPlanets);


};


