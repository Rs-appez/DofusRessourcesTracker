function disableButton(button) {
    button.disabled = true;
}

function enableButton(button) {
    button.disabled = false;
}

function onRequest(event) {
    if (["buy-all-cards-btn"].includes(event.target.id)) {
        disableButton(event.target);
    }
}

function onResponse(event) {
    console.log("event : ", event);
    if (["buy-all-cards-btn"].includes(event.detail.requestConfig.elt.id)) {
        enableButton(event.detail.requestConfig.elt);
    }
}

document.body.addEventListener("htmx:beforeRequest", onRequest);
document.body.addEventListener("htmx:afterSwap", onResponse);
