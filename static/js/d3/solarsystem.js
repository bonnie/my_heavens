// d3 for drawing planets (including sun/moon)
// pulls globals xxxx from main-d3.js


var revealPlanets = function() {
    // make planets grow and shrink to highlight their position(s)
    // TODO: label planets during reveal
    // TODO: disable button and/or post message (in error div?) if no planets are visible 
    //        e.g.  berkeley 1/1/2017 1:00 AM

    var trans1time = 1000;
    var trans2time = 1000;

    // disable the button
    $('#reveal-planets').attr('disabled', 'disabled');

    // select planets
    var planets = d3.selectAll('circle.planet');

    // do fun zoom transitions
    // TODO: chain these transitions, rather than delays and settimeouts the second one
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


var rotateAndDrawSolarSystem = function(error, locationResponse) {
  // callback for getting data related to location and time 
  // (rotation and planet data)

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

  console.log(locationResponse);

  // first start rotation
  // drawing planets will be taken care of during rotation
  rotateInfo = locationResponse.rotation;
  rotateSky(rotateInfo.lambda, rotateInfo.phi);

  // then set global ss data and moon data
  planetData = locationResponse.planets;
  moonData = locationResponse.moon;
  sunData = locationResponse.sundata;


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

//////////////////////////////////////////
// functions to draw planets, moon, sun //
//////////////////////////////////////////


var drawPlanets = function(mode) {
    // draw the stars on the sphere of the sky
    // mode is a string that can either be omitted or set to 'transition'
    // It will be 'transition' when animating, to make animations faster
    //
    // uses global planetData

    var planetParams = {listData: planetData,
                        classPrefix: 'planet',
                        radiusFunction: getRadiusFromMag,
                        mode: mode};

    renderSkyObjectList(planetParams);

};


var drawMoon = function(mode) {
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

var drawSun = function(mode) {
  // draw the sun (and adjust background color if necessary)

  var sunLabel = skyObjects.append('text').attr('class', 'sun-label sky-label');

  var sunParams = { group: skyObjects,
                    classPrefix: 'sun',
                    mode: mode,
                    d: sunData,
                    radius: sunMoonRadius,
                    itemLabel: sunLabel
                  };

  var sunPoint = renderSkyObject(sunParams);
  var sunInSky = isVisible(sunPoint);
  printSkyBackground(sunInSky);

};

var drawSolarSystem = function(mode) {
  // draw the sun, moon and planets 
  // mode may be set to 'transition' for faster rendering during animation

  // set the radius for the sun and the moon
  // sunMoonRadius is globally scoped
  sunMoonRadius = skyRadius / 42;

  drawSun(mode);
  drawPlanets(mode);
  // drawMoon(mode);

};


