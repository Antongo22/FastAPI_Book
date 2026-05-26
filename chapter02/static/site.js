document.querySelectorAll("[data-tab-target]").forEach((button) => {
    button.addEventListener("click", () => {
        const target = button.getAttribute("data-tab-target");
        document.querySelectorAll("[data-tab-target]").forEach((item) => item.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
        button.classList.add("active");
        document.querySelector(target).classList.add("active");
    });
});
