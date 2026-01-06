let dialog = document.getElementById("cardDialog");
let form = document.getElementById("valueForm");
let clickableElements = null;

function refreshElements() {
    dialog = document.getElementById("cardDialog");
    form = document.getElementById("valueForm");
    clickableElements = document.querySelectorAll(".open-value-modal");
    clickableElements.forEach((element) => {
        element.addEventListener("click", openModal);
    });
}

function openModal(event) {
    if (!dialog || !form) return;

    const element = event.currentTarget;

    document.getElementById("modalName").textContent = element.dataset.name;
    const last_id = document.getElementById("item_id");
    if (last_id.value != element.dataset.id) form.reset();

    last_id.value = element.dataset.id;

    form.setAttribute("hx-target", `#resource-price-${element.dataset.id}`);
    let post_url = form.getAttribute("hx-post");
    post_url = post_url.replace(/\d+/, element.dataset.id);
    form.setAttribute("hx-post", post_url);

    htmx.process(form);

    dialog.showModal();
}

function closeModal() {
    dialog.close();
    form.reset();
}

refreshElements();

document.body.addEventListener("resourceValueAdded", function() {
    dialog.close();
    form.reset();
});

document.body.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "wanted-detail-container") refreshElements();
});
