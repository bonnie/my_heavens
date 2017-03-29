// d3 for drawing planets (including sun/moon)
// pulls globals xxxx from main-d3.js

'use strict';

var revealPlanets = function() {
    // show / hide rings to highlight planet position(s)
    // TODO: label planets during reveal

    var params = {
      trigger: planetToggle,
      obj: planetHighlights
    };
    opacityTransition(params);

};

var rotateAndDrawSolarSystem = function(error, locationResponse) {
  // callback for getting data related to location and time 
  // (rotation and planet data)

  // success function for planet data from planets.json

  // TODO: catch error where server is down and connection is refused

    // clear previous errors and warnings
    // errorDiv, warnDiv, and formGroups defined in star-page-control.js
    errorDiv.empty().hide();
    warnDiv.empty().hide();
    datelocFormGroups.removeClass('has-error');

  //////////////////
  // handle error //
  //////////////////

  if (error) {
    console.log(error);
      showAjaxError(error);
      return;
  }

  console.log(locationResponse);

  // set global ss data and moon data
  planetData = locationResponse.planets;
  moonData = locationResponse.moon;
  sunData = locationResponse.sundata;
  dateLocData = locationResponse.dateloc;


  // then rotate sky
  // drawing planets will be taken care of during rotation
  var rotateInfo = locationResponse.rotation;
  rotateSky(rotateInfo.lambda, rotateInfo.phi);

  //////////////
  // controls //
  //////////////

  // re-enable the "show stars" button
  $('#show-stars').removeAttr('disabled');

  // populate date/location info window
  populateDatelocInfo(dateLocData);

  // TODO: clear the celestial info div and re-add instructions
  celestialInfoTable.empty();
  celestialInfoHeader.html(celestialDivInstructions);

  // show the controls and info divs
  masterInfoDiv.show();

  // attach 'reveal planets' button to the revealPlanets function
  planetToggle.on('click', revealPlanets);

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

    var visiblePlanetCount = renderSkyObjectList(planetParams);

    if (mode !== 'transition') {

      var opacity = planetToggle.is(':checked') ? 0.6 : 0;

      // add identifier circles for each visible planet
      planetHighlights = d3.selectAll('g.planet-group')
              .append('circle')
              .attr('cx', function(d) { return getScreenCoords(d, 'x'); })
              .attr('cy', function(d) { return getScreenCoords(d, 'y'); })
              .attr('r', sunMoonRadius * 3)
              .attr('stroke-width', 2)
              .attr('stroke', 'red')
              .attr('fill-opacity', 0)
              .attr('opacity', opacity)
              .attr('class', 'planet-highlight');


      // update "reveal planets" checkbox
      if (visiblePlanetCount === 0) {
        planetToggle.attr('disabled', 'disabled');
        planetWarning.html('(no planets visible)');
      } else {
        planetToggle.removeAttr('disabled');
        planetWarning.empty();

      }

    }

};


var getScreenCoords = function(d, axis) {
  // return the current screen coordinate for the data and axis

  var coords = skyProjection([d.ra, d.dec]);
  return axis === 'x' ? coords[0] : coords[1];
};

var getMoonRotation = function() {
  // get the screen rotation of the moon based on angle to the pole, plus
  // angle rotated from the pole
  //
  // uses globals moonData, dateLocData

  // screen angle of pole
  var poleDec = dateLocData.lat.slice(-1) === 'N' ? 90 : -90;
  var poleData = {ra: 0, dec: poleDec};
  var poleX = getScreenCoords(poleData, 'x');
  var poleY = getScreenCoords(poleData, 'y');

  var moonX = getScreenCoords(moonData, 'x');
  var moonY = getScreenCoords(moonData, 'y');

}


var drawMoon = function(mode) {
  // simluate the phase of the moon based on colong, using a half-lit sphere
  // append moon to svg parameter

  // uses globals moonData, sunMoonRadius, skyObjects, 

  // TODO: rotate the moon appropriately! 

  // for easier access
  var d = moonData;

  // don't draw moon if it's below the horizon
  // if (d.alt < 0) {
  //   return;
  // }


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

  var moonRotation = getMoonRotation();

  // create the projection
  var moonProjection = d3.geoOrthographic()
      .scale(sunMoonRadius) // this determines the size of the moon
      .translate(skyProjection([d.ra, d.dec])) // moon coords here
      .clipAngle(90)
      .rotate([0, 0, d.rotation])
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
          .center([90 - d.colong])
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
