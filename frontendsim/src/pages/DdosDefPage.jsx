import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
import {
  Container,
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  Alert,
  Button
} from "@mui/material";
import ShieldIcon from "@mui/icons-material/Shield";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#3a86ff" },
    secondary: { main: "#ff006e" },
    background: { default: "#121212", paper: "#1e1e1e" },
    success: { main: "#00f5d4" },
  },
  typography: {
    fontFamily: "Arial, sans-serif",
  },
});

const DdosDefPage = () => {
  const [packets, setPackets] = useState([]);
  const [isProtected, setIsProtected] = useState(false);
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  const packetListRef = useRef(null);

  useEffect(() => {
    const newSocket = io("http://localhost:5000", {
      query: { pageType: "ddosdef" },
    });
    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!socket) return;

    socket.on("connect", () => {
      setIsConnected(true);
      fetch("http://localhost:5000/api/start-packets")
        .then((res) => res.json())
        .then((data) => console.log(data.message))
        .catch((err) => console.error("Error starting packets:", err));
    });

    socket.on("packet", (packet) => {
      setPackets((prev) => [...prev, packet].slice(-20));
      setTimeout(() => {
        if (packetListRef.current) {
          packetListRef.current.scrollTop = packetListRef.current.scrollHeight;
        }
      }, 100);
    });

    socket.on("ddos-prevention-activated", (data) => {
      setIsProtected(true);
    });

    socket.on("disconnect", () => {
      setIsConnected(false);
    });

    return () => {
      socket.off("connect");
      socket.off("packet");
      socket.off("ddos-prevention-activated");
      socket.off("disconnect");
    };
  }, [socket]);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center", py: 8, my: 4 }}>
          <ShieldIcon sx={{ fontSize: 64, color: "#3a86ff", filter: "drop-shadow(0px 4px 10px rgba(58, 134, 255, 0.5))", mb: 2 }} />
          <Typography variant="h3" sx={{ fontWeight: "bold", background: "linear-gradient(45deg, #3a86ff 30%, #8338ec 90%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", mb: 2 }}>
            Protected Server <br />(DDoS Defense Active)
          </Typography>

          {isConnected && !isProtected && (
            <Alert severity="info" sx={{ backgroundColor: "#1e1e1e", borderRadius: "12px", color: "#fff", mt: 2 }}>
              Receiving packets... ({packets.length} received)
            </Alert>
          )}

          {isProtected && (
            <Box sx={{ backgroundColor: "rgba(0, 245, 212, 0.2)", p: 3, borderRadius: "16px", boxShadow: "0px 4px 10px rgba(0, 245, 212, 0.5)", textAlign: "center", mt: 4 }}>
              <Typography variant="h6" sx={{ fontWeight: "bold", color: "#00f5d4" }}>DDoS Protection Activated!</Typography>
              <Typography sx={{ color: "#fff" }}>Unusual traffic detected. Incoming packets are now throttled.</Typography>
              <Button variant="contained" sx={{ mt: 2, backgroundColor: "#00f5d4", color: "#121212" }} href="/dashboard">Go to Dashboard</Button>
            </Box>
          )}

          <Paper sx={{ mt: 4, p: 3, borderRadius: "16px", width: "100%", maxWidth: "600px", backgroundColor: "#1e1e1e" }}>
            <Typography variant="h5" sx={{ mb: 2, color: "#3a86ff" }}>
              Received Packets Log
            </Typography>
            {packets.length === 0 ? (
              <Typography variant="body1" sx={{ color: "text.secondary", textAlign: "center" }}>
                No packets received yet...
              </Typography>
            ) : (
              <List ref={packetListRef} sx={{ maxHeight: "300px", overflowY: "auto", scrollbarWidth: "none", "&::-webkit-scrollbar": { display: "none" } }}>
                {packets.map((packet, index) => (
                  <ListItem key={index} sx={{ my: 1, p: 1.5, borderRadius: "12px", backgroundColor: "#1a1a1a", color: "#fff", display: "flex", justifyContent: "space-between" }}>
                    <Typography variant="body1">
                      <strong>Packet #{packet.id}</strong>
                    </Typography>
                    <Typography variant="body2">Size: {packet.size} bytes</Typography>
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Box>
      </Container>
    </ThemeProvider>
  );
};

export default DdosDefPage;
