// CSPOPS - Interactive D3.js Cause-Effect Graph
// Fully interactive with zoom, pan, drag, and detailed tooltips

let graphData = null;
let simulation = null;
let svg = null;
let g = null;
let zoom = null;

/**
 * Initialize and render the interactive cause-effect graph
 */
function renderGraph(data) {
    graphData = data;
    
    if (!data || !data.nodes || data.nodes.length === 0) {
        document.getElementById('graph-container').innerHTML = `
            <div class="error-box">
                <i class="fas fa-exclamation-triangle fa-3x"></i>
                <h3>No Graph Data Available</h3>
                <p>Please collect data first, then generate the graph.</p>
            </div>
        `;
        return;
    }
    
    // Clear previous graph
    d3.select('#cause-effect-graph').html('');
    
    // Set up SVG
    const container = document.querySelector('.graph-visualization');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    svg = d3.select('#cause-effect-graph')
        .attr('width', width)
        .attr('height', height)
        .call(d3.zoom().scaleExtent([0.1, 4]).on('zoom', (event) => {
            g.attr('transform', event.transform);
        }))
        .on('dblclick.zoom', null); // Disable double-click zoom
    
    // Create a group for the graph
    g = svg.append('g');
    
    // Add arrowhead marker with unique ID
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead-' + Date.now())
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 32)
        .attr('refY', 0)
        .attr('markerWidth', 8)
        .attr('markerHeight', 8)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#999');
    
    // Create force simulation with better parameters to prevent clustering
    simulation = d3.forceSimulation()
        .force('charge', d3.forceManyBody().strength(-1000))  // Stronger repulsion
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('link', d3.forceLink().id(d => d.id).distance(250).strength(0.9))  // Longer links
        .force('collide', d3.forceCollide().radius(80))  // Larger collision radius
        .force('x', d3.forceX(width / 2).strength(0.05))  // Weaker center pull
        .force('y', d3.forceY(height / 2).strength(0.05))
        .force('manyBody', d3.forceManyBody().strength(-500))  // Additional repulsion
        .alpha(1)  // Start with high energy
        .alphaMin(0.01)  // Run longer
        .alphaDecay(0.02);  // Slow decay
    
    // Draw the graph
    drawGraph(data);
    
    // Update counts
    document.getElementById('node-count').textContent = data.nodes.length;
    document.getElementById('edge-count').textContent = data.edges.length;
    
    // Populate lists
    populateNodeList(data.nodes);
    populateEdgeList(data.edges);
    
    // Show insights
    if (data.insights) {
        displayInsights(data.insights);
    }
}

/**
 * Draw the graph elements with interactivity
 */
function drawGraph(data) {
    // Color scale for node groups
    const colorScale = d3.scaleOrdinal()
        .domain(['economic', 'sentiment', 'emotion', 'crisis', 'service'])
        .range(['#377eb8', '#4daf4a', '#984ea3', '#e41a1c', '#ff7f00']);
    
    // Draw links (edges) with descriptions
    const links = g.append('g')
        .attr('class', 'links')
        .selectAll('g')
        .data(data.edges)
        .enter()
        .append('g')
        .attr('class', 'link-group');
    
    // Draw link lines
    links.append('line')
        .attr('stroke', d => {
            // Color code by relationship type
            const colors = {
                'influences': '#377eb8',
                'affects': '#4daf4a',
                'triggers': '#e41a1c',
                'correlates_with': '#984ea3',
                'leads_to': '#ff7f00',
                'drives': '#999999'
            };
            return colors[d.label] || '#999';
        })
        .attr('stroke-width', d => Math.sqrt(d.strength || 0.5) * 3)
        .attr('marker-end', 'url(#arrowhead-' + Date.now() + ')')
        .style('opacity', 0.6);
    
    // Draw link labels (relationship type)
    const linkLabels = links.append('g')
        .attr('class', 'link-label');
    
    linkLabels.append('text')
        .text(d => d.label.replace(/_/g, ' '))
        .attr('text-anchor', 'middle')
        .attr('dy', -8)
        .attr('fill', '#666')
        .attr('font-size', '11px')
        .attr('font-weight', 'bold')
        .style('pointer-events', 'none');
    
    // Add description tooltip
    links.append('title')
        .text(d => {
            const desc = d.description || 'No description available';
            return `${d.from} → ${d.to}\nRelationship: ${d.label.replace(/_/g, ' ')}\nStrength: ${(d.strength || 0.5).toFixed(1)}/1.0\n\n${desc}`;
        });
    
    // Draw nodes with drag interaction
    const nodes = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(data.nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('dblclick', (event, d) => {
            // Double-click to highlight connections
            highlightConnections(d.id);
        });
    
    // Draw node circles with gradient
    nodes.append('circle')
        .attr('r', 30)
        .attr('fill', d => colorScale(d.group || 'economic'))
        .attr('stroke', 'white')
        .attr('stroke-width', 3)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            d3.select(this)
                .attr('r', 38)
                .attr('stroke', '#667eea')
                .attr('stroke-width', 4);
            
            // Highlight connected nodes and edges
            highlightNode(d.id);
        })
        .on('mouseout', function(event, d) {
            d3.select(this)
                .attr('r', 30)
                .attr('stroke', 'white')
                .attr('stroke-width', 3);
            
            // Remove highlights
            removeHighlights();
        });
    
    // Add node labels
    nodes.append('text')
        .text(d => truncateLabel(d.label))
        .attr('text-anchor', 'middle')
        .attr('dy', 5)
        .attr('fill', 'white')
        .attr('font-size', '10px')
        .attr('font-weight', 'bold')
        .attr('pointer-events', 'none')
        .style('text-shadow', '1px 1px 2px black');
    
    // Add value labels
    nodes.append('text')
        .text(d => d.value || '')
        .attr('text-anchor', 'middle')
        .attr('dy', 18)
        .attr('fill', 'white')
        .attr('font-size', '9px')
        .attr('font-weight', 'bold')
        .attr('pointer-events', 'none')
        .style('text-shadow', '1px 1px 2px black');
    
    // Node hover tooltip with detailed info
    nodes.append('title')
        .text(d => {
            let tooltip = `${d.label}\nGroup: ${d.group}\nValue: ${d.value || 'N/A'}`;
            if (d.trend) tooltip += `\nTrend: ${d.trend}`;
            if (d.prediction) tooltip += `\nPrediction: ${d.prediction}`;
            return tooltip;
        });
    
    // Update positions on each tick
    simulation
        .nodes(data.nodes)
        .on('tick', ticked);
    
    simulation
        .force('link')
        .links(data.edges);
    
    function ticked() {
        links
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        linkLabels
            .attr('transform', d => {
                const dx = d.target.x - d.source.x;
                const dy = d.target.y - d.source.y;
                const x = d.source.x + dx / 2;
                const y = d.source.y + dy / 2;
                return `translate(${x},${y})`;
            });
        
        nodes
            .attr('transform', d => `translate(${d.x},${d.y})`);
    }
}

/**
 * Highlight connected nodes and edges
 */
function highlightNode(selectedId) {
    // Get connected node IDs
    const connectedIds = new Set();
    graphData.edges.forEach(edge => {
        if (edge.from === selectedId) connectedIds.add(edge.to);
        if (edge.to === selectedId) connectedIds.add(edge.from);
    });
    connectedIds.add(selectedId);
    
    // Dim unconnected nodes
    d3.selectAll('.node')
        .transition().duration(200)
        .style('opacity', d => connectedIds.has(d.id) ? 1 : 0.2);
    
    // Highlight connected edges
    d3.selectAll('.link-group')
        .transition().duration(200)
        .style('opacity', d => 
            d.from === selectedId || d.to === selectedId ? 1 : 0.1
        );
}

/**
 * Remove all highlights
 */
function removeHighlights() {
    d3.selectAll('.node').transition().duration(200).style('opacity', 1);
    d3.selectAll('.link-group').transition().duration(200).style('opacity', 0.6);
}

/**
 * Highlight connections for a node
 */
function highlightConnections(nodeId) {
    // Center the view on the selected node
    const node = graphData.nodes.find(n => n.id === nodeId);
    if (node) {
        svg.transition().duration(750).call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(200, 150).scale(2)
        );
    }
    highlightNode(nodeId);
}

/**
 * Drag functions for node interaction
 */
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

/**
 * Truncate long labels
 */
function truncateLabel(label, maxLength = 12) {
    if (!label) return '';
    if (label.length <= maxLength) return label;
    return label.substring(0, maxLength - 2) + '...';
}

/**
 * Populate node list in details section
 */
function populateNodeList(nodes) {
    const container = document.getElementById('node-list');
    container.innerHTML = nodes.map(node => `
        <div class="node-item" style="border-left-color: ${getNodeColor(node.group)}">
            <strong>${node.label}</strong> (${node.group})<br>
            <small>Value: ${node.value || 'N/A'}</small>
            ${node.trend ? `<br><small>Trend: ${node.trend}</small>` : ''}
            ${node.prediction ? `<br><small>Prediction: ${node.prediction}</small>` : ''}
        </div>
    `).join('');
}

/**
 * Populate edge list with detailed descriptions
 */
function populateEdgeList(edges) {
    const container = document.getElementById('edge-list');
    container.innerHTML = edges.map(edge => `
        <div class="edge-item" style="border-left-color: ${getEdgeColor(edge.label)}">
            <strong>${edge.from}</strong> 
            <i class="fas fa-arrow-right"></i> 
            <strong>${edge.to}</strong><br>
            <small>
                <strong>Relationship:</strong> ${getRelationshipDescription(edge.label)}<br>
                <strong>Strength:</strong> ${(edge.strength || 0.5).toFixed(1)}/1.0
                ${getStrengthDescription(edge.strength)}<br>
                <strong>Description:</strong> ${edge.description || 'No description'}
            </small>
        </div>
    `).join('');
}

/**
 * Get color for node group
 */
function getNodeColor(group) {
    const colors = {
        'economic': '#377eb8',
        'sentiment': '#4daf4a',
        'emotion': '#984ea3',
        'crisis': '#e41a1c',
        'service': '#ff7f00'
    };
    return colors[group] || '#999999';
}

/**
 * Get color for edge type
 */
function getEdgeColor(label) {
    const colors = {
        'influences': '#377eb8',
        'affects': '#4daf4a',
        'triggers': '#e41a1c',
        'correlates_with': '#984ea3',
        'leads_to': '#ff7f00',
        'drives': '#999999'
    };
    return colors[label] || '#999999';
}

/**
 * Get human-readable relationship description
 */
function getRelationshipDescription(label) {
    const descriptions = {
        'influences': '🔵 Strongly influences',
        'causes': '🔴 Directly causes',
        'triggers': '⚡ Triggers or activates',
        'correlates_with': '📊 Statistically correlates with',
        'leads_to': '➡️ Leads to over time',
        'affects': '💫 Affects or impacts',
        'drives': '🚀 Drives or pushes'
    };
    return descriptions[label] || '🔗 Related to';
}

/**
 * Get strength description
 */
function getStrengthDescription(strength) {
    const s = strength || 0.5;
    if (s >= 0.8) return ' (Very Strong)';
    if (s >= 0.6) return ' (Strong)';
    if (s >= 0.4) return ' (Moderate)';
    return ' (Weak)';
}

/**
 * Display AI insights
 */
function displayInsights(insights) {
    const container = document.getElementById('graph-insights');
    container.innerHTML = `
        <h4><i class="fas fa-lightbulb"></i> AI-Discovered Insights</h4>
        <ol>
            ${insights.map(insight => `<li>${insight}</li>`).join('')}
        </ol>
    `;
}

/**
 * Download graph data as JSON
 */
function downloadGraph() {
    if (!graphData) return;
    
    const dataStr = JSON.stringify(graphData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `cause_effect_graph_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
