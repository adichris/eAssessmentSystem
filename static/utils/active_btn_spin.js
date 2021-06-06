

var spin = `<span class="ml-2 spinner-border spinner-border-sm"></span>`

function spinOnClick (theTag){
    theTag.title = theTag.innerHTML
    theTag.innerHTML = `${spin}</span>`;
}
function appendSpinOnClick (theTag){
    pre_html = theTag.innerHTML
    theTag.innerHTML = `${pre_html} ${spin}`;
}


function onBackSpin(theTag) {
    pre_html = "<i class='fa fa-chevron-left'></i>"
    theTag.innerHTML = `${pre_html} ${spin}`;
}