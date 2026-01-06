const clickableElements = document.querySelectorAll(".open-value-modal");
const dialog = document.getElementById("cardDialog");
const form = document.getElementById("valueForm");

function openModal(event) {
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

clickableElements.forEach((element) => {
    element.addEventListener("click", openModal);
});

document.body.addEventListener("resourceValueAdded", function() {
    dialog.close();
    form.reset();
});
