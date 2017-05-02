var populateInfoDiv = function(d) {
    // reveal and populate the info div when someone clicks on an item
    //
    // make sure the terms are clickable by running addDefinitionOnclick
    
    // show the info div
    celestialInfoDiv.show();

    // hide the definition div
    celestialDefDiv.hide();

    // populate the headers
    var celType = d.name === d.celestialType ? null : d.celestialType;
    addInfoDivHeader(celestialInfoHeader, d.name, celType);

    // empty the info table
    celestialInfoTable.empty();

    // populate table info
    if (d.constellation !== null) {
        addCelestialTableRow('Constellation', d.constellation);
    }
    addCelestialTableRow('<span class="term">Magnitude</span>', d.magnitude);
    if (d.celestialType === 'star' && d.name !== 'Sun') {
        addCelestialTableRow('<span class="term">Absolute Magnitude</span>', d.absMagnitude);
        addCelestialTableRow('<span class="term">Spectral Class</span>', d.specClass);
    }
    addCelestialTableRow('Distance', d.distance + ' <span class="term">' + d.distanceUnits + '</span>');

    if (d.celestialType === 'planet' || d.celestialType === 'moon') {
        addCelestialTableRow('Phase', d.phase + '% lit'); }

    if (d.celestialType !== 'star' || d.name === 'Sun') {
        addCelestialTableRow('Rose at', d.prevRise);
        addCelestialTableRow('Will set at', d.nextSet);
    }

};

var addInfoDivHeader = function(infoHeaderDiv, header, subHeader) {
    // add a header and subheader to an info table

    infoHeaderDiv.empty();

    var headerClass = ' class="text-center info-header" ';
    infoHeaderDiv.append('<h3' + headerClass + '>' + header + '</h3>');

    if (subHeader !== null && subHeader !== undefined) {
        infoHeaderDiv.append('<h5' + headerClass + '>' + subHeader + '</h5>');
    }

};

var addCelestialTableRow = function(rowName, rowValue) {
    // to avoid visual clutter
    addInfoTableRow(celestialInfoTable, rowName, rowValue);
};

// var addDatelocTableRow = function(rowName, rowValue) {
//     addInfoTableRow(datelocInfoTable, rowName, rowValue);
// };

var addInfoTableRow = function(infoTable, rowName, rowValue) {
    // add a row to the info table (celestialInfoTable)

    var rowString = '<tr><td class="info-table-name text-right">';
    rowString += rowName;
    rowString += '</td><td>';
    rowString += rowValue;
    rowString += '</td></tr>';

    infoTable.append(rowString);

};