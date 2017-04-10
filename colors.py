"""parse data to make dictionary connecting spectral classes to rbg colors. 

Data comes from 
http://www.vendian.org/mncharity/dir3/starcolor/UnstableURLs/starcolors.txt

    Copyright (c) 2017 Bonnie Schulkin

    This file is part of My Heavens.

    My Heavens is free software: you can redistribute it and/or modify it under
    the terms of the GNU Affero General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    My Heavens is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
    for more details.

    You should have received a copy of the GNU Affero General Public License
    along with My Heavens. If not, see <http://www.gnu.org/licenses/>.

"""

import re

COLOR_FILE = 'seed_data/colors.txt'
SC_RE = re.compile(r'([OBAFGKM]\d)\(([VI]+)\)')
cfile = open(COLOR_FILE)

COLOR_BY_SPECTRAL_CLASS = {}
for line in cfile:

    # line columns: 
    # class CIE xy chromaticity-x CIE xy chromaticity-y r g b RGB(hex)

    line = line.rstrip()
    tokens = line.split()

    # parse spectral class
    # ignore spectral classes with decimals, and N
    spectral_class = tokens[0].strip()
    matches = SC_RE.match(spectral_class)

    if matches:

        sc_a = matches.group(1)
        sc_b = matches.group(2)

        # TODO: use defaultdict here
        if sc_a not in COLOR_BY_SPECTRAL_CLASS:
            COLOR_BY_SPECTRAL_CLASS[sc_a] = {}

        COLOR_BY_SPECTRAL_CLASS[sc_a][sc_b] = tokens[-1].rstrip()


PLANET_COLORS_BY_NAME = {
    'Mercury': '#f5f5f5',
    'Venus': '#ffffee',
    'Mars': '#ffca8a',
    'Jupiter': '#ffffc8',
    'Saturn': '#ffffc8',
    'Uranus': '#f8f8ff',
    'Neptune': '#f8f8ff',
    'Sun': '#f0e68c',
    'Moon': '#f5f5f5'
}