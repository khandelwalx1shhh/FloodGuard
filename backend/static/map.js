// Function to initialize the world map visualization
function initializeMap() {
  const width = document.getElementById("map-container").offsetWidth;
  const height = 600;

  // Setup SVG
  const svg = d3
    .select("#world-map")
    .attr("width", width)
    .attr("height", height);

  // Create map projection
  const projection = d3
    .geoMercator()
    .scale(width / 2 / Math.PI)
    .translate([width / 2, height / 1.5]);

  const path = d3.geoPath().projection(projection);

  // Add background
  svg
    .append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", "#111927");

  // Load world map data
  d3.json(
    "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
  ).then(function (world) {
    // Draw map
    svg
      .append("g")
      .selectAll("path")
      .data(topojson.feature(world, world.objects.countries).features)
      .enter()
      .append("path")
      .attr("d", path)
      .attr("fill", "#1e293b")
      .attr("stroke", "#2c3e50")
      .attr("stroke-width", 0.5);

    // Add glow effect
    const defs = svg.append("defs");
    const filter = defs.append("filter").attr("id", "glow");

    filter
      .append("feGaussianBlur")
      .attr("stdDeviation", "3")
      .attr("result", "coloredBlur");

    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Generate attacks periodically
    setInterval(createAttack, 1000);
  });
}

// Helper function to create curved path
function curve(source, target) {
  const dx = target[0] - source[0];
  const dy = target[1] - source[1];
  const dr = Math.sqrt(dx * dx + dy * dy);
  const mid = [(source[0] + target[0]) / 2, (source[1] + target[1]) / 2];
  const curvature = 0.35;

  return `M${source[0]},${source[1]} 
            Q${mid[0]},${mid[1] - dr * curvature} 
            ${target[0]},${target[1]}`;
}

// Function to create attack
function createAttack() {
  const svg = d3.select("#world-map");
  const projection = d3
    .geoMercator()
    .scale(svg.attr("width") / 2 / Math.PI)
    .translate([svg.attr("width") / 2, svg.attr("height") / 1.5]);

  const sourceCity =
    MAJOR_CITIES[Math.floor(Math.random() * MAJOR_CITIES.length)];
  let targetCity;
  do {
    targetCity = MAJOR_CITIES[Math.floor(Math.random() * MAJOR_CITIES.length)];
  } while (targetCity === sourceCity);

  const attackType = Math.random() > 0.5 ? "ddos" : "botnet";
  const color = attackType === "ddos" ? "#ff3a8c" : "#36d7b7";

  const source = projection([sourceCity.lng, sourceCity.lat]);
  const target = projection([targetCity.lng, targetCity.lat]);

  // Create curved path
  const pathData = curve(source, target);

  // Add source glow
  const sourceGlow = svg
    .append("circle")
    .attr("cx", source[0])
    .attr("cy", source[1])
    .attr("r", 0)
    .attr("fill", color)
    .style("filter", "url(#glow)");

  sourceGlow
    .transition()
    .duration(500)
    .ease(d3.easeElastic)
    .attr("r", 4)
    .transition()
    .duration(1000)
    .attr("r", 2);

  // Create attack line with gradient
  const gradient = svg
    .append("linearGradient")
    .attr("id", `gradient-${Date.now()}`)
    .attr("gradientUnits", "userSpaceOnUse")
    .attr("x1", source[0])
    .attr("y1", source[1])
    .attr("x2", target[0])
    .attr("y2", target[1]);

  gradient
    .append("stop")
    .attr("offset", "0%")
    .attr("stop-color", color)
    .attr("stop-opacity", 1);

  gradient
    .append("stop")
    .attr("offset", "100%")
    .attr("stop-color", color)
    .attr("stop-opacity", 0);

  // Animated attack line
  const line = svg
    .append("path")
    .attr("class", "attack-line")
    .attr("d", pathData)
    .attr("stroke", `url(#gradient-${Date.now()})`)
    .attr("stroke-width", 2)
    .attr("opacity", 0)
    .style("filter", "url(#glow)");

  // Animate the line
  const pathLength = line.node().getTotalLength();

  line
    .attr("stroke-dasharray", pathLength)
    .attr("stroke-dashoffset", pathLength)
    .attr("opacity", 1)
    .transition()
    .duration(2000)
    .ease(d3.easePolyOut)
    .attr("stroke-dashoffset", 0)
    .transition()
    .duration(500)
    .attr("opacity", 0)
    .remove();

  // Add impact effect
  const impact = svg
    .append("circle")
    .attr("cx", target[0])
    .attr("cy", target[1])
    .attr("r", 0)
    .attr("fill", color)
    .style("filter", "url(#glow)")
    .attr("opacity", 0);

  impact
    .transition()
    .delay(1500)
    .duration(500)
    .attr("r", 8)
    .attr("opacity", 1)
    .transition()
    .duration(1000)
    .attr("r", 0)
    .attr("opacity", 0)
    .remove();

  // Add city labels with pop effect
  const label = svg
    .append("text")
    .attr("x", target[0])
    .attr("y", target[1] - 15)
    .attr("text-anchor", "middle")
    .attr("fill", color)
    .attr("font-size", "0px")
    .attr("class", "city-label")
    .text(`${sourceCity.name} → ${targetCity.name}`);

  label
    .transition()
    .delay(1500)
    .duration(500)
    .ease(d3.easeElastic)
    .attr("font-size", "12px")
    .transition()
    .delay(1000)
    .duration(500)
    .attr("font-size", "0px")
    .remove();
}
