function scrollToForm() {
  document.getElementById("form")?.scrollIntoView({ behavior: "smooth" });
}

function goPartnerRegistration() {
  const baseUrl = "https://usmanovafit.gymteam.ru/partnerregistration";
  const query = window.location.search;
  window.location.href = !query || query === "?" ? baseUrl : baseUrl + query;
}

document.getElementById("hero-cta-desktop")?.addEventListener("click", scrollToForm);
document.getElementById("hero-cta-mobile")?.addEventListener("click", goPartnerRegistration);
