function disableButton(button) {
    button.disabled = true;
}

function enableButton(button) {
    button.disabled = false;
}

function setupPriceColor(element) {
    const elem = document.getElementById(element.id);
    const currentPriceDiv = elem.getElementsByClassName("current-price")[0];
    const currentPrice = parseFloat(currentPriceDiv.dataset.currentPrice);
    const medianPriceDiv = elem.getElementsByClassName("median-price")[0];
    const medianPrice = parseFloat(medianPriceDiv.dataset.medianPrice);

    if (currentPrice < medianPrice - medianPrice * 0.2) {
        currentPriceDiv.classList.add("good-price");
        currentPriceDiv.classList.remove("bad-price");
    } else if (currentPrice > medianPrice + medianPrice * 0.2) {
        currentPriceDiv.classList.add("bad-price");
        currentPriceDiv.classList.remove("good-price");
    } else {
        currentPriceDiv.classList.remove("good-price", "bad-price");
    }
}

function setupPriceColors() {
    const priceElements = document.querySelectorAll(".card-price");
    priceElements.forEach(setupPriceColor);
}
function onRequest(event) {
    if (["buy-all-cards-btn"].includes(event.target.id)) {
        disableButton(event.target);
    }
}

function onResponse(event) {
    if (["buy-all-cards-btn"].includes(event.detail.requestConfig.elt.id)) {
        enableButton(event.detail.requestConfig.elt);
    } else if (event.target.id === "wanted-detail-container") {
        setupPriceColors();
    } else if (event.detail.target.className.includes("card-price")) {
        setupPriceColor(event.detail.target);
    }
}

document.body.addEventListener("htmx:beforeRequest", onRequest);
document.body.addEventListener("htmx:afterSwap", onResponse);
