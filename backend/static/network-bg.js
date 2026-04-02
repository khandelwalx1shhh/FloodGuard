/**
 * Network Background Animation
 * Creates a cybersecurity-themed network background effect
 */

document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("network-bg");
  const ctx = canvas.getContext("2d");

  // Set canvas to full window size
  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();

  // Node class
  class Node {
    constructor(x, y) {
      this.x = x;
      this.y = y;
      this.radius = Math.random() * 2 + 1;
      this.speed = Math.random() * 0.5 + 0.1;
      this.directionX = Math.random() * 2 - 1;
      this.directionY = Math.random() * 2 - 1;
      this.color = this.getRandomColor();
    }

    getRandomColor() {
      const colors = [
        "rgba(124, 58, 237, 0.7)", // purple
        "rgba(54, 215, 183, 0.7)", // teal
        "rgba(255, 58, 140, 0.6)", // pink
      ];
      return colors[Math.floor(Math.random() * colors.length)];
    }

    update() {
      // Bounce on edges
      if (this.x + this.radius > canvas.width || this.x - this.radius < 0) {
        this.directionX = -this.directionX;
      }
      if (this.y + this.radius > canvas.height || this.y - this.radius < 0) {
        this.directionY = -this.directionY;
      }

      // Update position
      this.x += this.directionX * this.speed;
      this.y += this.directionY * this.speed;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.fill();

      // Add glow effect
      ctx.shadowBlur = 10;
      ctx.shadowColor = this.color;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  // Network class
  class Network {
    constructor() {
      this.nodes = [];
      this.connectionDistance = 150;
      this.init();
    }

    init() {
      // Create nodes
      const nodeCount = Math.min(
        Math.floor((window.innerWidth * window.innerHeight) / 15000),
        150
      );

      for (let i = 0; i < nodeCount; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        this.nodes.push(new Node(x, y));
      }
    }

    // Draw connections between nodes
    drawConnections() {
      for (let i = 0; i < this.nodes.length; i++) {
        for (let j = i + 1; j < this.nodes.length; j++) {
          const dx = this.nodes[i].x - this.nodes[j].x;
          const dy = this.nodes[i].y - this.nodes[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < this.connectionDistance) {
            // Calculate opacity based on distance
            const opacity = 1 - distance / this.connectionDistance;

            // Get colors from nodes and blend them
            const color1 = this.nodes[i].color.replace(
              /[^,]+(?=\))/,
              opacity.toFixed(2)
            );

            ctx.beginPath();
            ctx.moveTo(this.nodes[i].x, this.nodes[i].y);
            ctx.lineTo(this.nodes[j].x, this.nodes[j].y);
            ctx.strokeStyle = color1;
            ctx.lineWidth = opacity * 1.5;
            ctx.stroke();

            // Add subtle glow to the lines
            if (opacity > 0.8) {
              ctx.shadowBlur = 5;
              ctx.shadowColor = this.nodes[i].color;
              ctx.stroke();
              ctx.shadowBlur = 0;
            }
          }
        }
      }
    }

    // Add occasional data packet animations
    addDataPacket() {
      if (this.nodes.length < 2 || Math.random() > 0.03) return;

      const sourceIndex = Math.floor(Math.random() * this.nodes.length);
      let targetIndex;

      do {
        targetIndex = Math.floor(Math.random() * this.nodes.length);
      } while (targetIndex === sourceIndex);

      const source = this.nodes[sourceIndex];
      const target = this.nodes[targetIndex];

      // Create a data packet that moves from source to target
      const packet = document.createElement("div");
      packet.className = "data-packet";
      packet.style.position = "absolute";
      packet.style.width = "4px";
      packet.style.height = "4px";
      packet.style.backgroundColor =
        Math.random() > 0.8 ? "#ff3a8c" : "#36d7b7";
      packet.style.borderRadius = "50%";
      packet.style.boxShadow = `0 0 10px ${packet.style.backgroundColor}`;
      packet.style.zIndex = "5";
      packet.style.opacity = "0.8";
      packet.style.transition =
        "all 1.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
      packet.style.left = source.x + "px";
      packet.style.top = source.y + "px";

      document.body.appendChild(packet);

      setTimeout(() => {
        packet.style.left = target.x + "px";
        packet.style.top = target.y + "px";
        packet.style.opacity = "0";
      }, 50);

      // Remove after animation completes
      setTimeout(() => {
        document.body.removeChild(packet);
      }, 2000);
    }

    update() {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update and draw nodes
      this.nodes.forEach((node) => {
        node.update();
        node.draw();
      });

      // Draw connections
      this.drawConnections();

      // Add occasional data packet
      this.addDataPacket();
    }

    // Handle window resize
    resize() {
      // Update distance based on window size
      this.connectionDistance = Math.max(
        100,
        Math.min(window.innerWidth, window.innerHeight) / 8
      );

      // Add or remove nodes based on new window size
      const idealNodeCount = Math.min(
        Math.floor((window.innerWidth * window.innerHeight) / 15000),
        150
      );

      if (idealNodeCount > this.nodes.length) {
        // Add more nodes
        for (let i = this.nodes.length; i < idealNodeCount; i++) {
          const x = Math.random() * canvas.width;
          const y = Math.random() * canvas.height;
          this.nodes.push(new Node(x, y));
        }
      } else if (idealNodeCount < this.nodes.length) {
        // Remove excess nodes
        this.nodes = this.nodes.slice(0, idealNodeCount);
      }
    }
  }

  // Initialize and run the network animation
  const network = new Network();

  // Add mouse interaction
  let mousePosition = {
    x: null,
    y: null,
  };

  canvas.addEventListener("mousemove", (e) => {
    mousePosition.x = e.x;
    mousePosition.y = e.y;

    // Create ripple effect on mouse move
    if (Math.random() > 0.92) {
      const ripple = document.createElement("div");
      ripple.className = "ripple";
      ripple.style.position = "absolute";
      ripple.style.width = "5px";
      ripple.style.height = "5px";
      ripple.style.borderRadius = "50%";
      ripple.style.border = "1px solid rgba(124, 58, 237, 0.5)";
      ripple.style.left = `${e.clientX}px`;
      ripple.style.top = `${e.clientY}px`;
      ripple.style.transform = "translate(-50%, -50%)";
      ripple.style.animation =
        "ripple 1s cubic-bezier(0, 0.2, 0.8, 1) forwards";
      document.body.appendChild(ripple);

      setTimeout(() => {
        document.body.removeChild(ripple);
      }, 1000);
    }
  });

  canvas.addEventListener("mouseleave", () => {
    mousePosition.x = null;
    mousePosition.y = null;
  });

  // Create additional nodes around mouse pointer
  function addNodeNearMouse() {
    if (mousePosition.x && Math.random() > 0.9) {
      const radius = 50;
      const angle = Math.random() * Math.PI * 2;
      const x = mousePosition.x + radius * Math.cos(angle);
      const y = mousePosition.y + radius * Math.sin(angle);

      // Add only if within canvas bounds
      if (x > 0 && x < canvas.width && y > 0 && y < canvas.height) {
        network.nodes.push(new Node(x, y));

        // Keep node count reasonable
        if (network.nodes.length > 200) {
          network.nodes.shift();
        }
      }
    }
  }

  // Handle window resize
  window.addEventListener("resize", () => {
    resizeCanvas();
    network.resize();
  });

  // Animation loop
  function animate() {
    network.update();
    addNodeNearMouse();
    requestAnimationFrame(animate);
  }

  animate();

  // Add CSS for ripple animation
  const style = document.createElement("style");
  style.textContent = `
    @keyframes ripple {
      0% { 
        width: 5px; 
        height: 5px; 
        opacity: 1; 
      }
      100% { 
        width: 100px; 
        height: 100px; 
        opacity: 0; 
      }
    }
    .data-packet {
      pointer-events: none;
    }
    .ripple {
      pointer-events: none;
      z-index: 10;
    }
  `;
  document.head.appendChild(style);
});
