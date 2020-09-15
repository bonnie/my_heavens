# My Heavens 
### An open-source view of the stars and planets
[![Build Status](https://travis-ci.org/flyrightsister/my_heavens.svg?branch=master)](https://travis-ci.org/flyrightsister/my_heavens)

## Contents

1. [Deployed Site](#deployed-site)
2. [License](#license)
3. [Overview](#overview)
4. [Data Sources](#data-sources)
5. [Tech Stack](#tech-stack)
6. [d3](#d3)
7. [Testing](#testing)
8. [Sticking Points](#sticking-points)
9. [Future Development](#future-development)
10. [About the Author](#about-the-author)

## License

My Heavens is licensed under the [GNU Affero General Public
License](http://www.gnu.org/licenses/).

## Overview

My Heavens is a web app 
inspired by Zoe Gotch-Strain's stellar (sorry, couldn't resist) [Hackbright
Student Project](https://github.com/ZoeShirah/Hackbright_Star_Project). The site
allows the user to enter a time and location, and it will show the configuration
of stars and planets (and sun and moon) as viewed from that time and place.
Mouseovers reveal constellations, and clicking on a sky object brings up more
information about the object. Clicking an astronomical term shows a brief
definition, as well as a link to more complete information on Wikipedia.
Finally, since astronomers value night vision, there is a "night mode" which
limits the color palette to a night-vision friendly red.

One thing the app does not do: take into account proper motion of the stars
(that is, the movement of the stars relative to one another). The configuration
of the stars will not change regardless of the date entered.

## Data Sources

#### Star cooridnates, magnitude, distance, spectral type, names, constellations
<http://astronexus.com/files/downloads/hygfull.csv.gz>

#### Mapping constellation abbreviations to names
<https://ircatalog.gsfc.nasa.gov/constel_names.html>

#### Coordinates of constellation boundaries
<http://pbarbier.com/constellations/boundaries.html#bnd18>

#### Constellation lines
<http://observe.phy.sfasu.edu/SFAStarCharts/ExcelCharts/ConstellationLinesAll2002.xls>

#### Mapping spectral type to hex color
<http://www.vendian.org/mncharity/dir3/starcolor/UnstableURLs/starcolors.txt>


## Tech Stack

- **PostgreSQL** 

    for stars, constellations, constellation boundaries, constellation lines

- **Python** 

    for processing database data and some calculations (such as apparent moon
    rotation in the sky field as seen on the web site)

- **Flask** 

    for serving the initial HTML and returing JSON for the [d3](#d3)

- **JavaScript/JQuery**

    for general page manipulation, and switching between pages (this is a
    one-page app, with different page views managed by JavaScript and CSS)

- **[d3](#d3)**

    for projecting stars and constellations onto three-dimensional sky sphere.
    [See below](#d3) for more details

## d3

The presentation of the star field relies heavily on
[d3-geo](https://github.com/d3/d3/blob/master/API.md#geographies-d3-geo). The
stars, planets, constellations, and all other sky objects are projected onto a
three-dimensional d3-geo sphere representing the sky. All star coordinates
needed to be reversed, since d3 presents the outside of the sphere, but the
viewers need to have the illusion that they are looking at the inside of the
sphere. 

This turns out to be a very efficient way to present the stars at an arbitrary
viewing location and time, since there is no need to calculate positions of
stars as the viewer would see them. An analogy to help understand this
efficiency: if you wanted to display the earth as viewed from a certain location
in space (say, the moon) at a certain time (say, right now), you could either:

a. Draw the earth as a circle, determining exactly what the earth would look
   like for that viewer and drawing the visible continents precisely positioned, or

b. draw *all* the continents on a sphere, and then rotate the
   sphere to display the half that our particular user would see (of course, on
   a two-dimensional screen, a sphere is flattened to a circle -- so what the user
   actually sees looks identical to choice (a)).

This app uses option (b) to approach showing the stars. This means the stars and
their locations need to load only once, when the app first loads. Any
repositioning of the user in time or space simply requires rotating the sphere
of the sky --- whose star data is already plotted --- to represent that view.

Since the planets, sun and moon move against the background of the stars, these
need to be re-plotted with each newly entered time. However, there are very
few of these compared to the thousands of visible stars in the sky, so this
takes a negligible amount of time.

## Testing

As of the time of writing this readme (May 2, 2017), 100% of the Python code is
covered by unit tests, and a [Travis](https://travis-ci.org) integration runs
the tests with every GitHub push. 0% of the JavaScript is tested (see [Future
Development](#future-development)).

The app was developed using Chrome 57.0.2987.133 (64-bit) on Mac OS X 10.11.5.
There has been no testing with other browsers or platforms.

## Sticking Points

Some interesting technical issues arose in the making of this app. 

### Constellation boundaries

The constellation boundaries were d3 polygons projected onto a sphere. I wanted
to use these boundary polygons to trigger the constellation visibility on
mouseover --- but I was stymied when some polygons seemed to take up the whole
sky, covering any constellation polygons that had come before them. 

This was a tough one -- it took a while even to figure out what to google to
remedy this. It turns out that the polygons for these constellation "space hogs"
were inverted, so that the "interior" of the polygon was everything *but* the
constellation, instead of the constellation itself. The inversion occurred when
the constellation boundary coordinates were counter-clockwise instead of
clockwise.

Helpful web sites for this: 
    
<https://github.com/d3/d3/issues/2051>

<https://bl.ocks.org/mbostock/a7bdfeb041e850799a8d3dce4d8c50c8>

### How to rotate the sky sphere

I needed to figure out how to rotate the sphere of the sky to represent the view
that the user would see for the desired place and time. This was a lot more
difficult that I thought it would be, and required way more wikipedia reading
and dredging up of college astronomy than I expected.

Basically, I wanted to provide a declination (which happens to be the latitude)
and an altitude (90 degrees), and get the right ascension (which will determine
how much the sky sphere needs to rotate). 

I eventually worked out that I could use the hour angle from the [sidereal
python library](http://infohost.nmt.edu/tcc/help/lang/python/examples/sidereal/)
to get the desired rotation.

### How to draw the moon phase

I wanted to draw the moon in its current phase, and the easiest(!) way to do
this seemed to be:

- make a little d3 sphere for the moon

- light up half of it

- rotate the correct part of the lit half into view

Thankfully, the [pyEphem python library](http://rhodesmill.org/pyephem/)
provides the selenegraphic colongitude of the moon (which is the angle of the
terminus of the lit hemisphere --- more wikipedia research!). Also, you can't
project a d3 sphere (i.e. the moon) onto another d3 sphere (the sky), so the
moon would show up regardless of whether it was on the "right" side of the sky
sphere. I needed to make a proxy point for the moon's location in the sky,
determine whether that point was visible, and only show the moon in that case.

### How to rotate the moon

This was by far the most vexing technical problem of this app, thanks to a
combination of mathematical obscurity and programmer error. The most helpful
link for this was a formula from this paper:

<https://planetarium.madison.k12.wi.us/mooncal/crescent-tilt/Crescent.html>

Even with that formula, it took me many, many hours to determine how to rotate
the moon sphere so that the axis of the phase was properly perpendicular to the
ecliptic -- or in more layman's terms, so that the points of the crescent
pointed in the right direction. The "show ecliptic" feature was mostly so I
could check to see whether the moon was correctly rotated.

### Serpens

Serpens is the "problem child" of the constellations --- it has two distinct
boundary polygons (imagine if the state of California was both California and
Washington). I ultimately decided it wasn't worth structuring the database
around this oddity (Serpens is the only constellation with two boundary
polygons, and the constellations are fixed and unchanging), so Serpens has
its own dedicated code for processing its special configuration.

### Deployment and tzwhere

It turns out the utility I was using for getting a time zone from latitude and
longitude -- [tzwhere](https://pypi.python.org/pypi/tzwhere) -- is quite memory
intensive. So memory intensive, in fact that the lowest tier of AWS LightSail
refuses to run it. I went down a false path of trying the less-memory intensive
[geopy](https://pypi.python.org/pypi/geopy/1.11.0) for timezone lookup -- but
sadly, it was also less reliable. My Travis tests would sporadically fail when
this service failed.

Ultimately, I went with using tzwhere in conjunction with numpy to reduce memory
usage. This slows down the travis tests considerably, though, since numpy takes
a long time to pip install.

## Future Development

Open issues are [tracked via
GitHub](https://github.com/flyrightsister/my_heavens/issues).

Please send all bug reports and feature requests to admin@myheavens.space. This
is a hobby project, so there are no guarantees of follow-through!

## About the Author

Bonnie Schulkin is a teacher, coder, and astronomer (in that order). This app is
a fun combination of all three.
