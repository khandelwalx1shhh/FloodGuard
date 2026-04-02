/**
 * Handle sending alert notifications via email
 */
document.addEventListener("DOMContentLoaded", function () {
  // Set up event listener for send alert button
  const sendAlertBtn = document.getElementById("send-alert-btn");
  if (sendAlertBtn) {
    sendAlertBtn.addEventListener("click", sendAlertEmail);
  }
});

function sendAlertEmail() {
  // Show loading state
  const sendBtn = document.getElementById("send-alert-btn");
  const btnText = sendBtn.querySelector(".btn-text");
  const originalText = btnText.innerHTML;

  sendBtn.disabled = true;
  btnText.innerHTML =
    '<span class="spinner-border spinner-border-sm"></span> Sending...';

  // Get recipient email if there's an input field
  let recipient = "";
  const recipientInput = document.getElementById("alert-recipient");
  if (recipientInput) {
    recipient = recipientInput.value;
  }

  // Send the request
  fetch("/send-alert", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      alert_type: "DDoS Alert",
      message: "Potential DDoS attack detected on your network",
      recipient: recipient,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Show result
      const resultEl = document.getElementById("alert-result");
      if (resultEl) {
        if (data.success) {
          resultEl.innerHTML = `<div class="alert alert-success"><i class="fas fa-check-circle"></i> ${data.message}</div>`;
        } else {
          resultEl.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> ${data.message}</div>`;
        }
      }

      // Reset button
      setTimeout(() => {
        sendBtn.disabled = false;
        btnText.innerHTML = originalText;
      }, 1000);
    })
    .catch((error) => {
      console.error("Error:", error);
      const resultEl = document.getElementById("alert-result");
      if (resultEl) {
        resultEl.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle"></i> Error sending notification: ${error}</div>`;
      }

      // Reset button
      sendBtn.disabled = false;
      btnText.innerHTML = originalText;
    });
}
