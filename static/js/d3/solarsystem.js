// d3 for drawing planets (including sun/moon)
// pulls globals xxxx from main-d3.js


disablePlanetButton = function() {
  // disable the "reveal planets" button
  $('#reveal-planets').attr('disabled', 'disabled');

};

enablePlanetButton = function() {
  // enable the "reveal planets" button
  $('#reveal-planets').removeAttr('disabled');
};

var revealPlanets = function() {
    // make planets grow and shrink to highlight their position(s)
    // TODO: label planets during reveal
    // TODO: disable button and/or post message (in error div?) if no planets are visible 
    //        e.g.  berkeley 1/1/2017 1:00 AM


  var t = d3.transition()
      .duration(500)
      .ease(d3.easeLinear);

    planetHighlights.transition(t)
        .attr('opacity', 1)
      .transition(t)
        .attr('opacity', 0)
      .on('start', disablePlanetButton)
      .on('end', enablePlanetButton);


    // TODO: make a nice ux here, like clicking a button to put a circle around planets 
    // and show the planet names, and then clicking the same button to hide

  // var t = d3.transition()
  //     .duration(1000)
  //     .ease(d3.easeLinear);

  // d3.selectAll('g.planet-group')
  //     .on('start', $('#reveal-planets').attr('disabled', 'disabled'))
  //     .transition(t)
  //       .attr('transform', 'scale(5)')
  //     .transition(t)
  //       .attr('transform', 'scale(1)')
  //     .on('end', $('#reveal-planets').removeAttr('disabled'));


// d3.selectAll(".orange").transition(t)
//     .style("fill", "orange");

//     // do fun zoom transitions
//     // TODO: chain these transitions, rather than delays and settimeouts the second one
//     planets.transition()
//         .duration(transtime)
//         .attr('r', function(d) { return d3.select(this).attr('r') * 5; });

//     planets.transition()
//         .delay(trans1time)
//         .duration(trans2time)
//         .attr('r', function(d) { return d3.select(this).attr('r'); });

//     // re-enable the button
//     setTimeout(function() {
//                     ;
//                 },
//                 trans1time + trans2time);

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


  // set global ss data and moon data
  planetData = locationResponse.planets;
  moonData = locationResponse.moon;
  sunData = locationResponse.sundata;


  // then rotate sky
  // drawing planets will be taken care of during rotation
  rotateInfo = locationResponse.rotation;
  rotateSky(rotateInfo.lambda, rotateInfo.phi);

  //////////////
  // controls //
  //////////////

  // re-enable the "show stars" button
  $('#show-stars').removeAttr('disabled');

  // show the starfield controls 
  starfieldControlDiv.show();
  $('#reveal-planets').removeAttr('disabled');

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

    if (mode !== 'transition') {
      // add identifier circles for each visible planet
      planetHighlights = d3.selectAll('g.planet-group')
              .append('circle')
              .attr('cx', function(d) { return getScreenCoords(d, 'x'); })
              .attr('cy', function(d) { return getScreenCoords(d, 'y'); })
              .attr('r', sunMoonRadius * 3)
              .attr('stroke-width', 2)
              .attr('stroke', 'red')
              .attr('fill-opacity', 0)
              .attr('opacity', 0)
              .attr('class', 'planet-highlight');
    }
};


var getScreenCoords = function(d, axis) {
  // return the current screen coordinate for the data and axis

  coords = skyProjection([d.ra, d.dec]);
  return axis === 'x' ? coords[0] : coords[1];
};


var drawMoon = function(mode) {
  // simluate the phase of the moon based on colong, using a half-lit sphere
  // append moon to svg parameter

  // uses globals moonData, sunMoonRadius, skyObjects, 

  // TODO: rotate the moon appropriately! 

  // for easier access
  d = moonData;

  // how to tell if the moon is on the far side of the sky? Make a proxy point
  // and see  if it's visible...
  var moonPoint = {
            geometry: {
                type: 'Point',
                coordinates: [d.ra, d.dec]
            },
            type: 'Feature',
  };

  if (!isVisible(moonPoint)) {
    return;
  }

  // otherwise, carry on...

  rotAngle = calculateMoonRotationAngle();

  // create the projection
  var moonProjection = d3.geoOrthographic()
      .scale(sunMoonRadius) // this determines the size of the moon
      .translate(skyProjection([d.ra, d.dec])) // moon coords here
      .clipAngle(90)
      .precision(0.1);

  // create a path generator
  var moonPath = d3.geoPath()
      .projection(moonProjection);

  // create the moon sphere
  var moon = skyObjects.append("path")
      .datum({type: "Sphere"})
      .attr("id", "moon-sphere")
      .attr("d", function(d) { return moonPath(d); })
      // .attr('fill', 'red')
      .attr('opacity', 0);


  // create the lit hemisphere
  var litHemisphere = d3.geoCircle()
          // sets the circle center to the specified point [longitude, latitude] in degrees
          // 0 degrees is on the left side of the sphere
          .center([90 - d.colong, 0]) // TODO: change the 0 to the proper rotation angle
          .radius(90); // sets the circle radius to the specified angle in degrees

  // project the lit hemisphere onto the moon sphere
  skyObjects.append('path')
      .datum(litHemisphere)
      .attr("d", function(d) { return moonPath(d); })
      .attr('fill', 'white')
      .attr('stroke', 'white')
      .attr('stroke-width', 1)
      .attr('class', 'lit-moon');

  moonLabel = skyObjects.append('text')
        .attr('class', 'moon-label sky-label');

  addInfoMouseOverAndClick(moon, d, moonLabel);
};

var drawSun = function(mode) {
  // draw the sun (and adjust background color if necessary)

  var sunParams = { d: sunData,
                    classPrefix: 'sun',
                    radius: sunMoonRadius,
                    mode: mode};

  var sunPoint = renderSingleSkyObject(sunParams);
  var sunInSky = isVisible(sunPoint);
  printSkyBackground(sunInSky, mode);

};

var drawSolarSystem = function(mode) {
  // draw the sun, moon and planets 
  // mode may be set to 'transition' for faster rendering during animation

  // set the radius for the sun and the moon
  // sunMoonRadius is globally scoped
  sunMoonRadius = skyRadius / 42;

  drawSun(mode);
  drawPlanets(mode);
  drawMoon(mode);

};

var calculateMoonRotationAngle = function() {
  // get the angle that the moon will need to rotate in order to be "pointing"
  // in the right direction, based on where it is, and where the sun is

  var moonCoords = skyProjection([moonData.ra, moonData.dec]);
  var sunCoords = skyProjection([sunData.ra, sunData.dec]);
  var moonX = moonCoords[0];
  var moonY = moonCoords[1];
  var sunX = sunCoords[0];
  var sunY = sunCoords[1];

  var rotationInRads = Math.atan2(sunX - moonX, sunY - moonY);
  return rotationInRads * 180 / Math.PI - 90;

};
