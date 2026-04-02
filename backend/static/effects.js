// Animate counters and other visual effects
document.addEventListener("DOMContentLoaded", function () {
  // Counter animation function
  const counters = document.querySelectorAll(".counter");
  const speed = 200;

  counters.forEach((counter) => {
    const animate = () => {
      const value = +counter.innerText.replace(/[^\d.]/g, "");
      const data = +counter.getAttribute("data-target");
      const time = data / speed;

      if (value < data) {
        counter.innerText = Math.ceil(value + time);
        setTimeout(animate, 1);
      } else {
        counter.innerText = counter
          .getAttribute("data-format")
          .replace("{value}", data);
      }
    };

    const target = counter.innerText;
    counter.setAttribute("data-target", target.replace(/[^\d.]/g, ""));
    counter.setAttribute("data-format", target);
    counter.innerText = "0";

    // Start animation when element is in viewport
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animate();
          observer.unobserve(entry.target);
        }
      });
    });

    observer.observe(counter);
  });

  // Add parallax effect to glass cards
  const glassCards = document.querySelectorAll(".glass-card");

  glassCards.forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = (y - centerY) / 20;
      const rotateY = (centerX - x) / 20;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform =
        "perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)";
    });
  });
});
