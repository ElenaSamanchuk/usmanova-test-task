function scrollToContact() {
  document.getElementById("contact")?.scrollIntoView({ behavior: "smooth" });
}

function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => {
    toast.hidden = true;
  }, 3200);
}

function validateForm(form) {
  let valid = true;
  form.querySelectorAll(".field-error").forEach((el) => el.classList.remove("field-error"));

  form.querySelectorAll("[required]").forEach((input) => {
    if (!String(input.value).trim()) {
      input.classList.add("field-error");
      valid = false;
    }
  });

  return valid;
}

function handleFormSubmit(form, statusEl, successMessage) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    statusEl.className = "form-status";
    statusEl.textContent = "";

    if (!validateForm(form)) {
      statusEl.textContent = "Заполните обязательные поля";
      statusEl.classList.add("is-error");
      return;
    }

    const data = Object.fromEntries(new FormData(form));
    console.info("Lead submitted (demo):", data);

    form.reset();
    statusEl.textContent = successMessage;
    statusEl.classList.add("is-success");
    showToast(successMessage);
  });
}

function initFaq() {
  document.querySelectorAll(".faq-question").forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest(".faq-item");
      const isActive = item.classList.contains("active");

      document.querySelectorAll(".faq-item").forEach((faqItem) => {
        faqItem.classList.remove("active");
        faqItem.querySelector(".faq-question")?.setAttribute("aria-expanded", "false");
      });

      if (!isActive) {
        item.classList.add("active");
        button.setAttribute("aria-expanded", "true");
      }
    });
  });
}

function initModal() {
  const modal = document.getElementById("program-modal");
  const modalTitle = document.getElementById("modal-title");
  const modalProgram = document.getElementById("modal-program");
  const modalForm = document.getElementById("modal-form");
  const modalStatus = document.getElementById("modal-status");

  function openModal(programName) {
    modalTitle.textContent = programName;
    modalProgram.value = programName;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    modal.querySelector(".field__input")?.focus();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = "";
    modalStatus.textContent = "";
    modalStatus.className = "form-status";
    modalForm.reset();
  }

  document.querySelectorAll(".program-detail-btn").forEach((button) => {
    button.addEventListener("click", () => {
      openModal(button.dataset.program || "Программа");
    });
  });

  modal.querySelectorAll("[data-close-modal]").forEach((el) => {
    el.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) closeModal();
  });

  handleFormSubmit(
    modalForm,
    modalStatus,
    "Спасибо! Мы свяжемся с вами и расскажем о программе."
  );
}

document.getElementById("hero-cta")?.addEventListener("click", scrollToContact);

handleFormSubmit(
  document.getElementById("contact-form"),
  document.getElementById("form-status"),
  "Заявка отправлена! Мы подберём программу и свяжемся с вами."
);

initFaq();
initModal();
