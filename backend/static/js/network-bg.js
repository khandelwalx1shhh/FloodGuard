document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('network-bg');
    const ctx = canvas.getContext('2d');
    let particleArray = [];
    
    // Configuration
    const numberOfParticles = 100;
    const particleSize = 2;
    const connectionDistance = 100;
    const moveSpeed = 0.5;
    
    // Resize canvas to full window size
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    // Create particle class
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.velocityX = (Math.random() - 0.5) * moveSpeed;
            this.velocityY = (Math.random() - 0.5) * moveSpeed;
        }
        
        update() {
            // Move particle
            this.x += this.velocityX;
            this.y += this.velocityY;
            
            // Bounce off edges
            if (this.x < 0 || this.x > canvas.width) this.velocityX *= -1;
            if (this.y < 0 || this.y > canvas.height) this.velocityY *= -1;
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, particleSize, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(23, 162, 184, 0.5)'; // Accent color with opacity
            ctx.fill();
        }
    }
    
    // Initialize particles
    function init() {
        particleArray = [];
        for (let i = 0; i < numberOfParticles; i++) {
            particleArray.push(new Particle());
        }
    }
    
    // Draw connections between particles
    function connect() {
        for (let i = 0; i < particleArray.length; i++) {
            for (let j = i + 1; j < particleArray.length; j++) {
                const dx = particleArray[i].x - particleArray[j].x;
                const dy = particleArray[i].y - particleArray[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < connectionDistance) {
                    const opacity = (1 - distance / connectionDistance) * 0.2; // Reduced opacity
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(23, 162, 184, ${opacity})`;
                    ctx.lineWidth = 1;
                    ctx.moveTo(particleArray[i].x, particleArray[i].y);
                    ctx.lineTo(particleArray[j].x, particleArray[j].y);
                    ctx.stroke();
                }
            }
        }
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update and draw particles
        particleArray.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        connect();
        requestAnimationFrame(animate);
    }
    
    // Handle window resize
    window.addEventListener('resize', resizeCanvas);
    
    // Initialize
    resizeCanvas();
    init();
    animate();
}); 