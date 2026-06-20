document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('button.btn.f-btn').forEach((button) => {
    if (button.dataset.bound) return;
    button.dataset.bound = "1";
    button.addEventListener("click", (event) => {
      event.preventDefault();
      const isMobile = window.matchMedia("(max-width: 1020px)").matches;
      if (isMobile) {
        const baseUrl = "https://usmanovafit.gymteam.ru/partnerregistration";
        const query = window.location.search;
        window.location.href = !query || query === "?" ? baseUrl : baseUrl + query;
        return;
      }
      const form = document.getElementById("ltBlock2235774933");
      (form || document.getElementById("ltBlock2235774935"))?.scrollIntoView({ behavior: "smooth" });
    });
  });

  document.querySelectorAll('img[data-src]').forEach((img) => {
    if (!img.getAttribute("src")) img.setAttribute("src", img.getAttribute("data-src"));
  });
});
