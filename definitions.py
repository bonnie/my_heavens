"""Definitions to for terms used in the app.

Each term has its wikipedia title (for ease in linking) in addition to a definition."""

import re

# a formattable string for the wikipedia url
WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/{}'
HTML_RE = r'<[^>]*>'

DEFINITIONS = {
    'parsecs': {
      'term': 'parsec',
      'wikipedia': 'Parsec',
      'definition': 'A parsec is a unit of distance equal to 3.26 <span class="term">light-year</span>s, 31 trillion kilometers, or 19 trillion miles.'
    }, 
    'ecliptic': {
      'wikipedia': 'Ecliptic',
      'definition': 'The ecliptic marks the apparent path of the sun in the sky against the background of stars, as the earth orbits the sun. Since the solar system is all roughly in the same plane, all planets and the moon will be found on or near the ecliptic.'
    },
    'compass': {
      'term': 'Why are East and West reversed?',
      'wikipedia': None,
      'definition': 'On a map looking toward earth, west is clockwise from north, but on this map looking at the sky, east is clockwise from north. Think about holding this map over your head: if north is behind your head and south is in front, then east will be to the left and west to the right.'
    },
    'magnitude': {
      'wikipedia': 'Magnitude_(astronomy)',
      'definition': 'Magnitude (or apparent magnitude) is a measure of brightness for an object in the sky. Smaller magnitudes are brighter, so the brightest star in the sky has a magnitude of around -1.5, and the unaided eye in dark skies can typically see objects as dim as magnitude 6.'
    },
    'absolute magnitude': {
      'wikipedia': 'Absolute_magnitude',
      'definition': 'Absolute magnitude is the <span class="term">magnitude</span> of an object if it were viewed at 10 <span class="term">parsecs</span> from earth. This helps with comparing the intrinsic brightness of stars regardless of their actual distance from earth.'
    },
    'au': {
      'term': 'astronomical unit (AU)',
      'wikipedia':'Astronomical_unit',
      'definition': 'The astronomical unit is used to measure solar system distances. It is based on the average distance from earth to the sun: roughly 150 million kilometers, or 93 million miles.'
    },
    'spectral class': {
      'wikipedia': 'Stellar_classification',
      'definition': 'The spectral class of a star indicates its temperature (which is related to its color) and its current life cycle stage.'
    },
    'light-year': {
      'wikipedia': 'Light-year',
      'definition': 'A unit of distance equal to the span light travels in one year.'
    },
    'waxing': {
      'wikipedia': 'Lunar_phase',
      'definition': 'The moon is said to be "waxing" if the lit portion visible from earth is growing larger each day.'
    },
    'crescent': {
      'wikipedia':'Lunar_phase',
      'definition': 'A moon is labeled "crescent" if less than half the lit portion is visible from earth.'
    },
    'gibbous': {
      'wikipedia': 'Lunar_phase',
      'definition': 'A moon is labeled "gibbous" if more than half the lit portion is visible from earth.'
    },
    'waning': {
      'wikipedia': 'Lunar_phase',
      'definition': 'The moon is said to be "waning" if the lit portion visible from earth is growing smaller each day.'
    }
}

# do some stuff all at once to avoid repetitive code
for term, term_info in DEFINITIONS.iteritems():
    if term_info['wikipedia']:
        term_info['wikipedia'] = WIKIPEDIA_URL.format(term_info['wikipedia'])
    
    term_info['clean_definition'] = re.sub(HTML_RE, '', term_info['definition'])