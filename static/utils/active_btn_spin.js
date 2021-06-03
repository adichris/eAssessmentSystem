

var spin = `<span class="ml-2 spinner-border spinner-border-sm"></span>`

function spinOnClick (theTag){
    theTag.title = theTag.innerHTML
    theTag.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;
}
function appendSpinOnClick (theTag){
    pre_html = theTag.innerHTML

    theTag.innerHTML = `${pre_html} ${spin}`;

}