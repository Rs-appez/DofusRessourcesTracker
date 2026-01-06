document.body.addEventListener("htmx:configRequest", function(event) {
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    event.detail.headers["X-CSRFToken"] = csrfToken;
});
