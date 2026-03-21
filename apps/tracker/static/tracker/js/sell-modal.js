function refreshSellElements() {
    let sell_div = document.getElementById("sell_values");
    if (sell_div) sell_div.addEventListener("click", openSellModal);
}

function openSellModal(event) {
    let dialog = document.getElementById("sellDialog");
    if (dialog) dialog.showModal();
}

document.body.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "wanted-detail-container")
        refreshSellElements();
});
