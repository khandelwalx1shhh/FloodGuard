/**
 * Authentication functionality
 * Handles login and registration forms
 */

document.addEventListener("DOMContentLoaded", function () {
  // Add cybersecurity themed background elements
  addCyberBackgroundElements();

  // Login form handling
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      const btnText = submitBtn.querySelector(".btn-text");

      // Store original button text
      const originalText = btnText.innerHTML;

      // Disable button and show loading state
      submitBtn.disabled = true;
      btnText.innerHTML =
        '<span class="spinner-border spinner-border-sm login-spinner"></span> Authenticating...';

      // Add success class after a small delay to simulate processing
      setTimeout(() => {
        // This is just visual feedback and doesn't impact actual form submission
        submitBtn.classList.add("btn-success");
      }, 300);

      // Error handling - if the form submission fails, reset the button
      // This would normally be handled by the server response
      loginForm.addEventListener(
        "invalid",
        function () {
          submitBtn.disabled = false;
          btnText.innerHTML = originalText;
          submitBtn.classList.remove("btn-success");
        },
        true
      );
    });
  }

  // Registration form handling
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", function (e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      const btnText = submitBtn.querySelector(".btn-text");

      // Store original button text
      const originalText = btnText.innerHTML;

      // Disable button and show loading state
      submitBtn.disabled = true;
      btnText.innerHTML =
        '<span class="spinner-border spinner-border-sm register-spinner"></span> Creating account...';

      // Add success class after a small delay
      setTimeout(() => {
        submitBtn.classList.add("btn-success");
      }, 300);

      // Error handling
      registerForm.addEventListener(
        "invalid",
        function () {
          submitBtn.disabled = false;
          btnText.innerHTML = originalText;
          submitBtn.classList.remove("btn-success");
        },
        true
      );
    });
  }

  // Password visibility toggle functionality
  const togglePasswordBtns = document.querySelectorAll(".toggle-password");
  togglePasswordBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const passwordInput = document.getElementById(
        this.getAttribute("data-target")
      );
      if (!passwordInput) return;

      const icon = this.querySelector("i");

      if (passwordInput.type === "password") {
        passwordInput.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
      } else {
        passwordInput.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
      }
    });
  });

  // Form validation enhancement
  const formInputs = document.querySelectorAll(".cyber-input");
  formInputs.forEach((input) => {
    input.addEventListener("input", function () {
      if (this.value.length > 0) {
        this.classList.add("is-valid");
      } else {
        this.classList.remove("is-valid");
      }
    });
  });
});

// Function to add cybersecurity themed background elements
function addCyberBackgroundElements() {
  const wrapper = document.querySelector(".auth-wrapper");
  if (!wrapper) return;

  // Add animated elements
  for (let i = 0; i < 8; i++) {
    const element = document.createElement("div");
    element.className = "cyber-element";

    // Random size between 50 and 300px
    const size = Math.floor(Math.random() * 250) + 50;
    element.style.width = `${size}px`;
    element.style.height = `${size}px`;

    // Random position
    element.style.top = `${Math.floor(Math.random() * 100)}%`;
    element.style.left = `${Math.floor(Math.random() * 100)}%`;

    // Random shape
    if (Math.random() > 0.5) {
      element.style.borderRadius = "50%";
    } else {
      element.style.borderRadius = `${Math.floor(Math.random() * 20)}px`;
    }

    // Random rotation and animation
    const duration = Math.floor(Math.random() * 20) + 20;
    element.style.animation = `float ${duration}s infinite linear`;

    wrapper.appendChild(element);
  }

  // Add keyframe animation if it doesn't exist
  if (!document.getElementById("cyber-animations")) {
    const styleSheet = document.createElement("style");
    styleSheet.id = "cyber-animations";
    styleSheet.textContent = `
            @keyframes float {
                0% { transform: translate(-50%, -50%) rotate(0deg) scale(1); }
                50% { transform: translate(-50%, -50%) rotate(180deg) scale(1.1); }
                100% { transform: translate(-50%, -50%) rotate(360deg) scale(1); }
            }
        `;
    document.head.appendChild(styleSheet);
  }
}
