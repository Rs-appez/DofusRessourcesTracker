let sellDialog;
let sellForm;

function refreshSellElements() {
    sellDialog = document.getElementById("sellDialog");
    sellForm = document.getElementById("sellForm");
    let sellDiv = document.getElementById("sell_values");
    if (sellDiv) sellDiv.addEventListener("click", openSellModal);
}

function openSellModal(event) {
    if (sellDialog) sellDialog.showModal();
}

function closeSellModal() {
    sellDialog.close();
    sellForm.reset();
}

document.body.addEventListener("resourceSellValueAdded", function() {
    closeSellModal();
});

document.body.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "wanted-detail-container")
        refreshSellElements();
});
