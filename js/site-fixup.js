(function () {
  "use strict";

  const COOKIE_KEY = "usmanova_cookies_accepted";

  function hideCookieBanner() {
    document.querySelectorAll(".cookies-notification").forEach((banner) => {
      banner.style.transition = "opacity 0.35s ease";
      banner.style.opacity = "0";
      window.setTimeout(() => banner.remove(), 350);
    });
  }

  function ensureFormAnchor() {
    if (document.getElementById("form")) return;
    const contact =
      document.getElementById("ltBlock2235774933") ||
      document.getElementById("ltBlock2235774935");
    if (!contact) return;
    const anchor = contact.querySelector(".lt-block-wrapper") || contact;
    anchor.id = "form";
  }

  function hydrateLazyImages() {
    document.querySelectorAll("img.lazyload[data-src], img[data-src]").forEach((img) => {
      const src = img.getAttribute("data-src");
      if (!src) return;
      if (!img.getAttribute("src") || img.getAttribute("src") === window.location.href) {
        img.setAttribute("src", src);
      }
      img.classList.remove("lazyload");
    });
  }

  function bindFaq() {
    document.querySelectorAll(".faq-question").forEach((question) => {
      if (question.dataset.faqBound) return;
      question.dataset.faqBound = "1";
      question.style.cursor = "pointer";
      question.addEventListener("click", () => {
        const item = question.closest(".faq-item");
        if (!item) return;
        const isActive = item.classList.contains("active");

        document.querySelectorAll(".faq-item").forEach((node) => {
          node.classList.remove("active");
          const icon = node.querySelector(".faq-icon");
          if (icon) icon.textContent = "+";
        });

        if (!isActive) {
          item.classList.add("active");
          const icon = item.querySelector(".faq-icon");
          if (icon) icon.textContent = "×";
        }
      });
    });
  }

  function bindCookieButton() {
    document.addEventListener(
      "click",
      (event) => {
        const button = event.target.closest(".js__accept_cookies_policy");
        if (!button) return;

        event.preventDefault();
        event.stopImmediatePropagation();
        localStorage.setItem(COOKIE_KEY, "1");
        hideCookieBanner();
      },
      true
    );
  }

  function init() {
    ensureFormAnchor();
    hydrateLazyImages();
    bindFaq();
    bindCookieButton();

    if (localStorage.getItem(COOKIE_KEY)) {
      hideCookieBanner();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
