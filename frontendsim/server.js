import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';

const app = express();
app.use(cors());
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Track connections and packet counts
const connections = new Map();
const DDOS_THRESHOLD = 50;
const NORMAL_THRESHOLD = 70;

io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);
  
  // Get the page type from the query parameter
  const pageType = socket.handshake.query.pageType;
  connections.set(socket.id, { 
    packetCount: 0, 
    pageType: pageType,
    blocked: false
  });

  // Random cooldown before starting packet transmission (between 3 to 5 seconds)
  const cooldownTime = Math.floor(Math.random() * 2000) + 3000; // Random between 3000-5000ms
  console.log(`Cooldown for ${socket.id}: ${cooldownTime}ms`);

  setTimeout(() => {
    console.log(`Starting packet transmission for ${socket.id} after cooldown`);

    // Send packets every few milliseconds
    const packetInterval = setInterval(() => {
      const connection = connections.get(socket.id);
      
      if (!connection) {
        clearInterval(packetInterval);
        return;
      }
      
      // Check if DDOS prevention is active
      if (connection.pageType === 'ddosdef' && connection.packetCount >= DDOS_THRESHOLD && !connection.blocked) {
        socket.emit('ddos-prevention-activated', { message: 'DDOS Prevention Activated' });
        connection.blocked = true;
        console.log(`DDOS prevention activated for ${socket.id}`);
        return;
      }
      
      // Check if normal page has crashed
      if (connection.pageType === 'nodef' && connection.packetCount >= NORMAL_THRESHOLD && !connection.blocked) {
        socket.emit('server-overload', { message: 'Server Overload Error' });
        connection.blocked = true;
        console.log(`Server overload for ${socket.id}`);
        return;
      }
      
      // If not blocked, send a packet
      if (!connection.blocked) {
        const packetSize = Math.floor(Math.random() * 1000) + 100; // Random packet size between 100-1100 bytes
        const packet = {
          id: connection.packetCount,
          size: packetSize,
          timestamp: Date.now(),
          data: generateRandomString(packetSize)
        };
        
        socket.emit('packet', packet);
        connection.packetCount++;
        console.log(`Sent packet #${connection.packetCount} to ${socket.id} (${connection.pageType})`);
      }
    }, 100); // Fast packet sending for demonstration

    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
      connections.delete(socket.id);
      clearInterval(packetInterval);
    });

  }, cooldownTime); // Apply cooldown

});

// Helper function to generate random string data
function generateRandomString(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
