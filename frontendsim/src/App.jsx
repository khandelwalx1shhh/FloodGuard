import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import NodefPage from './pages/NodefPage';
import DdosDefPage from './pages/DdosDefPage';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ShootingStar from './components/ShootingStar';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#3a86ff' },
    secondary: { main: '#ff006e' },
    background: { default: '#121212', paper: '#1e1e1e' },
    success: { main: '#00f5d4', dark: '#0a2e2a', contrastText: '#ffffff' },
    info: { main: '#8338ec' },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: '0px', // Hide scrollbar in Firefox
          '&::-webkit-scrollbar': {
            display: 'none', // Hide scrollbar in Chrome, Safari, and Edge
          },
          msOverflowStyle: 'none', // Hide scrollbar in IE and Edge
          overflowX: 'hidden', // Prevent horizontal scrolling
        },
      },
    },
  },
});


function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        
          <ShootingStar />
          <Navbar />

          <Routes>
            <Route
              path="/"
              element={<HomePage />
              }
            />
            <Route path="/no-protection" element={<NodefPage />} />
            <Route path="/ddos-protection" element={<DdosDefPage />} />
          </Routes>
        
      </Router>
    </ThemeProvider>
  );
}

export default App;
