// functions for navigation

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
    if (tab == 'home' || tab == 'star-map') {

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
}

// openNav and closeNav adapted from
// https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_sidenav
function openNav() {
    $('#main-sidenav').css('width', '150px');
    $('#main-sidenav').css('height', '150px');
}

function closeNav() {
    $('#main-sidenav').css('width', '0');
    $('#main-sidenav').css('height', '0');
}
