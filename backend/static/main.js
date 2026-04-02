// Define major cities data
const MAJOR_CITIES = [
  { name: "New York", lat: 40.7128, lng: -74.006 },
  { name: "London", lat: 51.5074, lng: -0.1276 },
  { name: "Tokyo", lat: 35.6895, lng: 139.6917 },
  { name: "Beijing", lat: 39.9042, lng: 116.4074 },
  { name: "Mumbai", lat: 19.076, lng: 72.8777 },
  { name: "Moscow", lat: 55.7558, lng: 37.6173 },
  { name: "São Paulo", lat: -23.5505, lng: -46.6333 },
  { name: "Singapore", lat: 1.3521, lng: 103.8198 },
  { name: "Dubai", lat: 25.2048, lng: 55.2708 },
  { name: "Paris", lat: 48.8566, lng: 2.3522 },
  { name: "Berlin", lat: 52.52, lng: 13.405 },
  { name: "Toronto", lat: 43.6532, lng: -79.3832 },
  { name: "Seoul", lat: 37.5665, lng: 126.978 },
  { name: "Bangalore", lat: 12.9716, lng: 77.5946 },
  { name: "Sydney", lat: -33.8688, lng: 151.2093 },
];

// Initialize all components when DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize the map visualization
  initializeMap();
});
