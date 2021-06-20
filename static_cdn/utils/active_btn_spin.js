

var spin = `<span class="ml-2 spinner-border spinner-border-sm"></span>`

function appendSpinOnClick (theTag){
    pre_html = theTag.innerText
    theTag.innerHTML = `${pre_html} ${spin}`;
}

function spinOnClick (theTag){
    // theTag.title = theTag.innerHTML
    // theTag.innerHTML = `${spin}</span>`;
    /* ADD append spin to all button text*/
    appendSpinOnClick(theTag)
}

function onBackSpin(theTag) {
    pre_html = "<i class='fa fa-chevron-left'></i>"
    theTag.innerHTML = `${pre_html} ${spin}`;
}


function windowHistoryBack() {
    window.history.back()
}