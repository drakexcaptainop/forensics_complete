// Ensure Leaflet library is included in your HTML file:
// <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
// <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

const geojsonpath = "./ruta_completa.geojson"; // Ensure the file is in the same directory

// Initialize the map
const map = L.map('map').setView([0, 0], 2); // Default center and zoom level

// Add a tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Fetch and display the GeoJSON file
fetch(geojsonpath)
    .then(response => response.json())
    .then(data => {
        // Add GeoJSON layer to the map
        L.geoJSON(data, {
            onEachFeature: (feature, layer) => {
                // Add tooltips if "name" or "tooltip" property exists
                if (feature.properties) {
                    const tooltip = feature.properties.name || feature.properties.tooltip;
                    if (tooltip) {
                        layer.bindTooltip(tooltip);
                    }
                }
            }
        }).addTo(map);

        // Adjust the map view to fit the GeoJSON layer
        const bounds = L.geoJSON(data).getBounds();
        map.fitBounds(bounds);
    })
    .catch(error => {
        console.error("Error loading GeoJSON:", error);
    });
