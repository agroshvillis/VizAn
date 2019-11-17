function IsMetabolite(parent) {
    return parent.getElementsByClassName('node-label label').length > 0;
}

function ShowTooltip(parent, evt) {
    HideTooltip();

    var zoom = window.outerWidth / window.innerWidth;
    var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
    if (isChrome) {
        zoom = 1;
    }

    var tooltip = document.getElementById('thepopup');

    tooltip.setAttribute("x", (evt.clientX + window.scrollX) * zoom);
    tooltip.setAttribute("y", (evt.clientY + window.scrollY) * zoom);

    var tooltipabbr = document.getElementById('tooltip-abbr');
    var tooltipname = document.getElementById('tooltip-name');
    var tooltipdata = document.getElementById('tooltip-data');
    var tooltiptype = document.getElementById('tooltip-type');
    var tooltiplink = document.getElementById('tooltip-link');

    var barParent = document.getElementById('chart-1');
    var ell;
    if (IsMetabolite(parent)) {
        barParent.style.display = 'none';
        tooltipabbr.innerHTML = GetTextValueForPopup(parent.getElementsByClassName('node-label label')[0].textContent);
        tooltiptype.innerHTML = 'Metabolite';
        tooltipname.innerHTML = 'Name: ' + GetTextValueForPopup(parent.getAttribute("Name"));
        tooltipdata.innerHTML = 'Formula: ' + GetTextValueForPopup(parent.getAttribute("Formula"));

        if (IsScrumpyFile()) {
            var metId = ClearElementData(parent.getAttribute("id_metabolite"));
            tooltiplink.action = 'http://bigg.ucsd.edu/universal/metabolites/' + metId;

        } else {
            ell = ClearElementData(parent.getAttribute("id_metabolite"));
            tooltiplink.action = 'http://identifiers.org/biocyc/META:' + ell;
        }
    } else {
        if (IsFVAFile(parent)) {
            InitBar(parent, barParent);
            barParent.style.display = 'block';
        } else {
            barParent.style.display = 'none';
        }
        tooltipabbr.innerHTML = GetTextValueForPopup(parent.getAttribute("id"));
        tooltiptype.innerHTML = 'Reaction';
        tooltipname.innerHTML = 'Name: ' + GetTextValueForPopup(parent.getAttribute("Name"));

        tooltipdata.innerText = 'Stoichiometry: ' + GetTextValueForPopup(parent.getAttribute("Stoichiometry"));

        if (IsScrumpyFile()) {
            ell = ClearElementData(parent.getAttribute("id"));
            tooltiplink.action = 'http://bigg.ucsd.edu/universal/reactions/' + ell;
        } else {
            ell = ClearElementData(parent.getAttribute("id"));
            tooltiplink.action = 'http://identifiers.org/biocyc/META:' + ell;
        }
    }
    tooltip.style.display = 'inline';
}

function IsScrumpyFile() {
    return !document.getElementById("svg2");
}

function GetTextValueForPopup(inputText) {
    return (inputText == '') ? 'Not specified' : ClearElementData(inputText);
}

function ClearElementData(inputElement) {
    return inputElement.replace(/_Plas/g, '').replace(/_Cyto/g, '').replace(/_Mitop/g, '').replace(/_Vaco/g, '').replace(/_tx/g, '').replace(/_c/g, '').replace(/_p/g, '').replace(/_e/g, '');
}

function HideTooltip() {
    var tooltip = document.getElementById('thepopup');
    tooltip.style.display = 'none';
    console.log('close pressed ');
}

function IsFVAFile(parent) {
    if (parent.getElementsByClassName('reaction-label label').length > 0) {
        innerHTML = parent.getElementsByClassName('reaction-label label')[0].textContent.trim().split(' ');
        return innerHTML.length > 2;
    } else {
        return false;
    }
}

function InitBar(parent, barParent) {
    innerHTML = parent.getElementsByClassName('reaction-label label')[0].textContent.trim().split(' ');
    lowValue = Math.round(innerHTML[1] / 10) * 10;
    highValue = Math.round(innerHTML[2] / 10) * 10;

    var maxFlux = parseFloat(innerHTML[2]);
    var minFlux = parseFloat(innerHTML[1]);

    var barMaxPx = 128;

    var maxValue = Math.max(Math.abs(lowValue), Math.abs(highValue));

    if (maxValue == 0) {
        maxValue = 10
    }

    var barMiddlePoint = barMaxPx / 2;
    var bottomPositionDefault = 50;
    var topPositionDefault = 10;
    var barStepsPx = barMaxPx / 2 / maxValue;

    var top = topPositionDefault + (maxValue - Math.abs(maxFlux)) * barStepsPx
    var bottom = bottomPositionDefault + (maxValue - Math.abs(minFlux)) * barStepsPx;
    var bar = document.getElementsByClassName('x-axis-bar primary')[0];
    bar.style.top = top + 'px';
    bar.style.bottom = bottom + 'px';
    valueStep = (maxValue * 2) / 4;

    barLinesArray = barParent.getElementsByClassName('y-axis-label');
    barLinesArray[0].innerText = Math.round(maxValue - valueStep * 4);
    barLinesArray[1].innerText = Math.round(maxValue - valueStep * 3);
    barLinesArray[2].innerText = Math.round(maxValue - valueStep * 2);
    barLinesArray[3].innerText = Math.round(maxValue - valueStep * 1);
    barLinesArray[4].innerText = Math.round(maxValue - valueStep * 0);
}