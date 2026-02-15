// Handle dynamic behaviors such as theme toggles, filters, and form interactions.
document.addEventListener("DOMContentLoaded", function () {
  const filterButtons = document.querySelectorAll("[data-category-filter]");
  const cards = document.querySelectorAll("[data-category]");

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const category = button.getAttribute("data-category-filter");

      filterButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");

      cards.forEach((card) => {
        const matches = category === "all" || card.getAttribute("data-category") === category;
        card.classList.toggle("d-none", !matches);
      });
    });
  });

  const scrollButtons = document.querySelectorAll("[data-scroll-target]");
  scrollButtons.forEach((scrollButton) => {
    scrollButton.addEventListener("click", (event) => {
      const targetSelector = scrollButton.getAttribute("data-scroll-target");
      const targetElement = document.querySelector(targetSelector);
      if (targetElement) {
        event.preventDefault();
        targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
});
