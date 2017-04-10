// functions for navigation

    // Copyright (c) 2017 Bonnie Schulkin

    // This file is part of My Heavens.

    // My Heavens is free software: you can redistribute it and/or modify it under
    // the terms of the GNU Affero General Public License as published by the Free
    // Software Foundation, either version 3 of the License, or (at your option)
    // any later version.

    // My Heavens is distributed in the hope that it will be useful, but WITHOUT
    // ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    // FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
    // for more details.

    // You should have received a copy of the GNU Affero General Public License
    // along with My Heavens. If not, see <http://www.gnu.org/licenses/>.

"use strict";

// event listener
$('.tab-link').on('click', function() {
    closeNav();
    switchTab($(this).html());
});

function switchTab(tab) {
    // hide all other tabs but the requested one

    // debugger;

    // replace spaces
    tab = tab === 'Star&nbsp;Map' ? 'star-map' : tab.toLowerCase();

    // hide all tabs
    $('.tab-div').hide();

    // move the dateloc form, if necessary
    if (tab === 'home' || tab === 'star-map') {

        // define where the dateloc form needs to move
        var oldtab = tab == 'home' ? 'star-map' : 'home';

        // gather the existing contents
        var datelocFormContents = datelocForm.detach();

        // stick 'em in the other tab
        datelocFormContents.appendTo('#' + tab + ' .dateloc-form-container');

        // if it's the home tab, hide the cancel button and show the form; 
        // show the cancel button in the star-map tab but hide the form
        if (tab == 'home') {
            datelocFormCancel.hide();
            datelocForm.show();
        } else {
            datelocFormCancel.show();
            datelocForm.hide();
        }

    }

    // show requested tab
    $('#' + tab).show()

    // (re)set the svg dimensions if necessary
    if (tab === 'star-map' && skyRadius !== getSkyRadius()) {
        svgSetDimensions();
    }

}

// openNav and closeNav adapted from
// https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_sidenav
function openNav() {
    $('#main-sidenav').css('width', '200px');
    $('#main-sidenav').css('height', '200px');
}

function closeNav() {
    $('#main-sidenav').css('width', '0');
    $('#main-sidenav').css('height', '0');
}
