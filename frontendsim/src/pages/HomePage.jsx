import { Box, Typography, Button, Container } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Shield } from "lucide-react";
import ShieldIcon from "@mui/icons-material/Shield";

import { Link } from "react-router-dom";

// Create a dark theme
const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#3a86ff",
    },
    secondary: {
      main: "#ff006e",
    },
    background: {
      default: "#121212",
      paper: "#1e1e1e",
    },
    success: {
      main: "#00f5d4",
    },
  },
});

const HomePage = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box
          sx={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            textAlign: "center",
            py: 8,
          }}
        >
          <ShieldIcon sx={{ fontSize: 64, color: "#3a86ff", filter: "drop-shadow(0px 4px 10px rgba(58, 134, 255, 0.5))", mb: 2 }} />

          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: "bold",
              background: "linear-gradient(45deg, #3a86ff 30%, #8338ec 90%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              mb: 2,
            }}
          >
          </Typography>

          <Typography
            variant="subtitle1"
            sx={{
              mb: 6,
              color: "text.secondary",
              maxWidth: "400px",
            }}
          >
            Advanced DDoS protection for your critical infrastructure
          </Typography>

          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              component={Link}
              to="/dashboard"
              sx={{
                px: 4,
                py: 1.5,
                borderRadius: 2,
                textTransform: "none",
                fontSize: "1rem",
                background: "linear-gradient(45deg, #3a86ff 30%, #8338ec 90%)",
                boxShadow: "0 3px 5px 2px rgba(58, 134, 255, .3)",
              }}
            >
              View Dashboard
            </Button>
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
};

export default HomePage;
