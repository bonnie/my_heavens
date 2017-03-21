// d3 for drawing planets (including sun/moon)
// pulls globals xxxx from main-d3.js


var revealPlanets = function() {
    // make planets grow and shrink to highlight their position(s)
    // TODO: label planets during reveal
    // TODO: disable button and/or post message (in error div?) if no planets are visible 
    //        e.g.  berkeley 1/1/2017 1:00 AM


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

  // uses globals moonData, sunMoonRadius, skyObjects, 

  // TODO: rotate the moon appropriately! 

  // for easier access
  d = moonData;

  // create the projection
  var moonProjection = d3.geoOrthographic()
      .scale(sunMoonRadius) // this determines the size of the moon
      .translate(skyProjection([d.ra, d.dec])) // moon coords here
      .clipAngle(90)
      .precision(0.1);
      // .rotate([0, 0, d.rotation]); // rotate the moon so the lit part points to the sun

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
          .center([90 - d.colong, 0])
          .radius(90); // sets the circle radius to the specified angle in degrees

  // project the lit hemisphere onto the moon sphere
  skyObjects.append('path')
      .datum(litHemisphere)
      .attr("d", function(d) { return moonPath(d); })
      .attr('fill', 'white')
      .attr('stroke', 'white')
      .attr('stroke-width', 1)
      .attr('class', 'lit-moon');

  addInfoWindowMouseOver(moon, d, planetInfoDiv);

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


