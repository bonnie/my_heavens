// generic functions for rendering sky objects
// used for stars and planets

    // Copyright (c) 2017 Bonnie Schulkin

    // This file is part of My Heavens.

    // My Heavens is free software: you can redistribute it and/or modify it
    // under the terms of the GNU Affero General Public License as published by
    // the Free Software Foundation, either version 3 of the License, or (at
    // your option) any later version.

    // My Heavens is distributed in the hope that it will be useful, but WITHOUT
    // ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    // FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
    // License for more details.

    // You should have received a copy of the GNU Affero General Public License
    // along with My Heavens. If not, see <http://www.gnu.org/licenses/>.

'use strict';

var renderSkyObjectList = function(params) {
    // render a list of sky objects
    // for use in drawing stars and planets
    //
    // params is an object with these keys:
    //      listData (e.g. starData)
    //      classPrefix (e.g. star)
    //      mode (e.g. transition)
    //      radiusFunction (e.g. function(d) {return (5 - d.magnitude) * 0.5})
    //      lambda (angle by which dec is rotated)
    //      phi (angle by which ra is rotated)

    // uses global skyObjects

    // add the item groups
    var items = skyObjects.selectAll('g.' + groupClass)
                            .data(params.listData)
                            .enter()
                            .append('g')

    if (params.mode !== 'transition') {
        // keep a running count of visible objects -- for noting whether there are
        // planets visible. 
        var visibleItemCount = 0;

        // One label that just gets repurposed depending on moused-over item,
        // since we're never going to be showing more than one item label at once
        var itemLabel = skyObjects.append('text')
            .attr('class', params.classPrefix + '-label sky-label');

        var groupClass = params.classPrefix + '-group';
        items.attr('class', groupClass);
    }

    // add sub-elements for each star
    items.each(function(d) {

        var objParams = {group: d3.select(this),
                     mode: params.mode,
                     d: d,
                     radius: params.radiusFunction(d),
                     classPrefix: params.classPrefix 
        };

        if (params.mode !== 'transition') {
            objParams.itemLabel = itemLabel;
        }

        var outcome = renderSkyObject(objParams)
        if (params.mode !=='transition' && outcome !== undefined) {
            visibleItemCount++;
        }
    });

    if (params.mode !== 'transition') {
        return visibleItemCount;
    }
};

var renderSingleSkyObject = function(params) {
    // render a list of sky objects
    // for use in drawing stars and planets
    //
    // params is an object with these keys:
    //      d (e.g. sunData)
    //      classPrefix (e.g. sun)
    //      mode (e.g. transition)
    //      radius (eg sunMoonRadius)
    //      lambda (angle by which dec is rotated)
    //      phi (angle by which ra is rotated)

    // uses global skyObjects

    // make a group for this obj and its label

    var itemGroup = skyObjects.append('g')
                            .attr('class', params.classPrefix + '-group');

    // One label that just gets repurposed depending on moused-over item,
    // since we're never going to be showing more than one item label at once
    // TODO: make function for this for less repitition

    if (params.mode !== 'transition') {
        var itemLabel = itemGroup.append('text')
            .attr('class', params.classPrefix + '-label sky-label');
    }

    var objParams = {group: itemGroup,
                     mode: params.mode,
                     d: params.d,
                     radius: params.radius,
                     classPrefix: params.classPrefix,
                     itemLabel: itemLabel};

    return renderSkyObject(objParams);

};

var renderSkyObject = function(params) {
    // render one sky object
    // for use in drawing individual stars and planets, sun, moon
    //
    // params is an object with these keys:
    //      group (group to which to attach this item)
    //      mode (e.g. transition)
    //      classPrefix (class for individual object, e.g. star)
    //      d (data object, expected to have ra, dec, magnitude, name, color)
    //      radiusFunction (radius function for this object)
    //      itemLabel (svg text element for object label)
    //      lambda (angle by which dec is rotated)
    //      phi (angle by which ra is rotated)

    // for easier reference
    var d = params.d;

    // determine whether the obj is visible
    // var lambda_viz = d.dec < params.lambda + 180
    // var phi_viz = params.phi - 180 < d.ra || d.ra < params.phi + 180


    // don't bother drawing dim items during transition
    if (params.mode !== 'transition' || params.d.magnitude < 2.5) {
    // if (params.mode !== 'transition' || (lambda_viz && phi_viz)) {

        // console.log('accepting ' + d.ra + ', ' + d.dec)

        var itemPoint = {
            geometry: {
                type: 'Point',
                coordinates: [d.ra, d.dec]
            },
            type: 'Feature',
            properties: {
                radius: params.radius
            }
        };

        if (params.mode !== 'transition' && !isVisible(itemPoint)) {
            // remove the star if it's not visible and don't bother going on
            // skip this step if the mode is transition, as it slows things down a tad
            params.group.remove();

        } else {

            // circle to represent item
            // since we're in d3 geo world, this needs to be a path with a point
            // geometry, not an svg circle
            var itemCircle = params.group.append('path')
                                .datum(itemPoint)
                                .attr('d', function(d) {
                                    skyPath.pointRadius(d.properties.radius);
                                    return skyPath(d); })
                                .attr('data', {'radius': params.radius});

            // don't bother with opacity  and class during transition
            if (params.mode !== 'transition') {
                itemCircle.attr('class', params.classPrefix)
                          .style('opacity', d.magnitude < 0 ? 1 : (5 - d.magnitude) / 5); 
            }

            // color according to star color in day mode; night mode color in night mode
            if ($('body').hasClass('daymode')) {
                itemCircle.attr('fill', d.color)
            } else {
                // nightModeColor defined in star-page-control.js
                itemCircle.attr('fill', nightModeColor)
            }

            if (params.mode !== 'transition' && d.name !== null) {
                // make a fixed-width, larger surrounding circle for the
                // mouseover, as some items are too  small to mouse over
                // effectively
                var surroundingCircle = params.group.append('path')
                                .datum(itemPoint)
                                .attr('d', function(d){
                                    skyPath.pointRadius(params.radius < 4 ? 4 : params.radius);
                                    return skyPath(d); })
                                .attr('class', params.classPrefix + '-surround item-surround')
                                .style('opacity', 0);

                addInfoMouseOverAndClick(surroundingCircle, d, params.itemLabel);
            }
            // return the point for ease in telling whether it's visible
            return itemPoint;
        }
    }
    // } else {
    //     console.log('rejecting ' + d.ra + ', ' + d.dec);
    // }

};