$(document).ready(function () {
    $('#dtBasicExample').DataTable();
    $('.dataTables_length').addClass('bs-select');
});

function copyToClipboard() {
    /* Get the text field */
    var copyText = document.getElementById("page-link");

    /* Select the text field */
    copyText.select();
    copyText.setSelectionRange(0, 99999); /* For mobile devices */

    /* Copy the text inside the text field */
    document.execCommand("copy");

}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Used by load spinner
async function loading() {
    await sleep(500)
    $("#loading").show();
    $("#content").hide();
}

$(function () {
    $('.select-search').selectpicker();
});