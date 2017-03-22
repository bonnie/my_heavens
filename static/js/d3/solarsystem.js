// d3 for drawing planets (including sun/moon)
// pulls globals xxxx from main-d3.js

'use strict';

var revealPlanets = function() {
    // show / hide rings to highlight planet position(s)
    // TODO: label planets during reveal
    // TODO: disable button and/or post message (in error div?) if no planets are visible 
    //        e.g.  berkeley 1/1/2017 1:00 AM

    //      triggerButton (button that called function; e.g. planetRevealButton)
    //      elementsShowing (state variable for this button; e.g. planetsRevealed)
    //      showText (text on button to show elements; e.g. 'Reveal Planets')
    //      hideText (text on button to hide elements; e.g. 'Hide planet indicators')
    //      obj (svg object to show/hide; e.g. planetHighlights)

    var params = {
      triggerButton: planetRevealButton,
      elementsShowing: planetsRevealed,
      showText: 'Reveal planets',
      hideText: 'Hide planet indicators',
      obj: planetHighlights
    };
    opacityTransition(params);
    planetsRevealed = !planetsRevealed;

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
  var rotateInfo = locationResponse.rotation;
  rotateSky(rotateInfo.lambda, rotateInfo.phi);

  //////////////
  // controls //
  //////////////

  // re-enable the "show stars" button
  $('#show-stars').removeAttr('disabled');

  // show the starfield controls 
  starfieldControlDiv.show();
  planetRevealButton.removeAttr('disabled');

  // attach 'reveal planets' button to the revealPlanets function
  planetRevealButton.on('click', revealPlanets);

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

  var coords = skyProjection([d.ra, d.dec]);
  return axis === 'x' ? coords[0] : coords[1];
};


var drawMoon = function(mode) {
  // simluate the phase of the moon based on colong, using a half-lit sphere
  // append moon to svg parameter

  // uses globals moonData, sunMoonRadius, skyObjects, 

  // TODO: rotate the moon appropriately! 

  // for easier access
  var d = moonData;

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

  var rotAngle = calculateMoonRotationAngle();

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

  var moonLabel = skyObjects.append('text')
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
