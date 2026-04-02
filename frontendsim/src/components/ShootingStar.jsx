import React, { useEffect, useRef } from 'react';

const ShootingStar = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    handleResize();
    window.addEventListener('resize', handleResize);

    // Star configuration
    const stars = [];
    const numStars = 150;
    const shootingStars = [];
    const maxShootingStars = 3;

    // Create initial background stars
    for (let i = 0; i < numStars; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.5 + 0.5
      });
    }

    // Get random starting position from corners
    const getRandomCorner = () => {
      const corners = [
        // Increased speed and adjusted angles for smoother diagonals
        { x: 0, y: 0, dx: 8, dy: 8 },             // top-left
        { x: canvas.width, y: 0, dx: -8, dy: 8 },  // top-right
        { x: 0, y: canvas.height, dx: 8, dy: -8 }, // bottom-left
        { x: canvas.width, y: canvas.height, dx: -8, dy: -8 } // bottom-right
      ];
      return corners[Math.floor(Math.random() * corners.length)];
    };

    // Create shooting star
    const createShootingStar = () => {
      const corner = getRandomCorner();
      return {
        x: corner.x,
        y: corner.y,
        dx: corner.dx + (Math.random() * 2 - 1),
        dy: corner.dy + (Math.random() * 2 - 1),
        size: 4, // Reduced from 12 to 4
        opacity: 1
      };
    };

    // Animation loop
    const animate = () => {
      // Full opacity clear to prevent trails
      ctx.fillStyle = 'rgba(13, 13, 15, 1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw background stars
      stars.forEach(star => {
        ctx.beginPath();
        ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity})`;
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fill();
        star.opacity = 0.5 + Math.abs(Math.sin(Date.now() * 0.001) * 0.5);
      });

      // Create new shooting star
      if (shootingStars.length < maxShootingStars && Math.random() < 0.01) {
        shootingStars.push(createShootingStar());
      }

      // Update and draw shooting stars
      shootingStars.forEach((star, index) => {
        // Draw shooting star with gradient
        const tailLength = 20; // Reduced from 30 to 20
        const gradient = ctx.createLinearGradient(
          star.x, star.y,
          star.x - (star.dx * tailLength), star.y - (star.dy * tailLength)
        );
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.5)'); // Reduced opacity
        gradient.addColorStop(0.1, 'rgba(255, 255, 255, 0.3)'); // Lighter fade
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

        // Draw the tapered tail
        ctx.beginPath();
        ctx.lineCap = 'round';
        
        // Create multiple lines with decreasing width for taper effect
        const segments = 4; // Reduced segments
        for (let i = 0; i < segments; i++) {
          const segmentLength = tailLength / segments;
          const startX = star.x - (star.dx * segmentLength * i);
          const startY = star.y - (star.dy * segmentLength * i);
          const endX = star.x - (star.dx * segmentLength * (i + 1));
          const endY = star.y - (star.dy * segmentLength * (i + 1));
          
          ctx.beginPath();
          ctx.strokeStyle = gradient;
          ctx.lineWidth = star.size * (1 - (i / segments)) * 0.8; // Reduced width
          ctx.moveTo(startX, startY);
          ctx.lineTo(endX, endY);
          ctx.stroke();
        }

        // Add a bright front point
        ctx.beginPath();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'; // Slightly reduced brightness
        ctx.arc(star.x, star.y, star.size/4, 0, Math.PI * 2); // Smaller point
        ctx.fill();

        // Move star
        star.x += star.dx;
        star.y += star.dy;
        
        // Remove if out of bounds
        if (star.x < -50 || star.x > canvas.width + 50 || 
            star.y < -50 || star.y > canvas.height + 50) {
          shootingStars.splice(index, 1);
        }
      });

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full -z-10"
      style={{ backgroundColor: '#0d0d0f' }}
    />
  );
};

export default ShootingStar;