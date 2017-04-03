// functions for navigation

// event listener
$('.tab-link').on('click', function() {
    closeNav();
    switchTab($(this).html());
});

function switchTab(tab) {
    // hide all other tabs but the requested one

    // replace spaces
    tab = tab === 'Star&nbsp;Map' ? 'star-map' : tab.toLowerCase();

    // hide all tabs
    $('.tab-div').hide()

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
