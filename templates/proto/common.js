
function reloadForm(form, element) {
    disablePage();
    if (!form) form = document.forms[0];
    //if (form.focused_element && element)
    //    form.focused_element.value = element.id;
    form.action = '?';
    if (element && element.name) {
        form.action += '#'+element.name;
    }
    form.submit();
}

function disablePage() {
    $('#__disabled').height($(document).height()).show();
}

function enablePage() {
    $('#__disabled').height(0).hide();
}

function updateMultiChoice(element, name, key, history){
    var multi = document.getElementById(name);
    var curVal = JSON.parse(multi.value);
    curVal[key] = element.checked ? (history ? element.value : true) : (history ? null : false);
    multi.value = JSON.stringify(curVal);
}
