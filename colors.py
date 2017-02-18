"""parse data to make dictionary connecting spectral classes to rbg colors. 

Data comes from 
http://www.vendian.org/mncharity/dir3/starcolor/UnstableURLs/starcolors.txt"""

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

