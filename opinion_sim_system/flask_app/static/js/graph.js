// CSPOPS - D3.js Force-Directed Cause-Effect Graph
// Beautiful, interactive visualization with detailed edge descriptions

let graphData = null;
let simulation = null;
let svg = null;
let g = null;
let zoom = null;

/**
 * Initialize and render the cause-effect graph
 */
function renderGraph(data) {
    graphData = data;
    
    // Clear previous graph
    d3.select('#cause-effect-graph').html('');
    
    // Set up SVG
    const container = document.querySelector('.graph-visualization');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    svg = d3.select('#cause-effect-graph')
        .attr('width', width)
        .attr('height', height);
    
    // Add zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Create a group for the graph
    g = svg.append('g');
    
    // Add arrowhead marker
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 28)
        .attr('refY', 0)
        .attr('markerWidth', 8)
        .attr('markerHeight', 8)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#999');
    
    // Create force simulation
    simulation = d3.forceSimulation()
        .force('charge', d3.forceManyBody().strength(-500))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('link', d3.forceLink().id(d => d.id).distance(150))
        .force('collide', d3.forceCollide().radius(40));
    
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
 * Draw the graph elements
 */
function drawGraph(data) {
    // Color scale for node groups
    const colorScale = d3.scaleOrdinal()
        .domain(['economic', 'sentiment', 'emotion', 'crisis', 'service'])
        .range(['#377eb8', '#4daf4a', '#984ea3', '#e41a1c', '#ff7f00']);
    
    // Draw links (edges)
    const links = g.append('g')
        .attr('class', 'links')
        .selectAll('g')
        .data(data.edges)
        .enter()
        .append('g')
        .attr('class', 'link-group');
    
    // Draw link lines
    links.append('line')
        .attr('stroke', '#999')
        .attr('stroke-width', d => Math.sqrt(d.strength || 0.5) * 2)
        .attr('marker-end', 'url(#arrowhead)');
    
    // Draw link labels (relationship type)
    const linkLabels = links.append('g')
        .attr('class', 'link-label');
    
    linkLabels.append('text')
        .text(d => d.label || 'relates to')
        .attr('text-anchor', 'middle')
        .attr('dy', -5)
        .attr('fill', '#666')
        .attr('font-size', '11px')
        .attr('font-weight', 'bold');
    
    // Add strength indicator
    linkLabels.append('text')
        .text(d => `Strength: ${(d.strength || 0.5).toFixed(1)}`)
        .attr('text-anchor', 'middle')
        .attr('dy', 8)
        .attr('fill', '#999')
        .attr('font-size', '9px');
    
    // Link hover tooltip
    links.append('title')
        .text(d => `${d.from} → ${d.to}\nRelationship: ${d.label || 'relates to'}\nStrength: ${(d.strength || 0.5).toFixed(1)}`);
    
    // Draw nodes
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
            .on('end', dragended));
    
    // Draw node circles
    nodes.append('circle')
        .attr('r', 25)
        .attr('fill', d => colorScale(d.group || 'economic'))
        .attr('stroke', 'white')
        .attr('stroke-width', 3)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            d3.select(this).attr('r', 30);
        })
        .on('mouseout', function(event, d) {
            d3.select(this).attr('r', 25);
        });
    
    // Draw node labels
    nodes.append('text')
        .text(d => truncateLabel(d.label))
        .attr('text-anchor', 'middle')
        .attr('dy', 5)
        .attr('fill', 'white')
        .attr('font-size', '10px')
        .attr('font-weight', 'bold')
        .attr('pointer-events', 'none');
    
    // Node hover tooltip with detailed info
    nodes.append('title')
        .text(d => `${d.label}\nGroup: ${d.group}\nValue: ${d.value || 'N/A'}`);
    
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
 * Truncate long labels
 */
function truncateLabel(label, maxLength = 15) {
    if (!label) return '';
    if (label.length <= maxLength) return label;
    return label.substring(0, maxLength - 2) + '...';
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
 * Populate node list in details section
 */
function populateNodeList(nodes) {
    const container = document.getElementById('node-list');
    container.innerHTML = nodes.map(node => `
        <div class="node-item" style="border-left-color: ${getNodeColor(node.group)}">
            <strong>${node.label}</strong> (${node.group})<br>
            <small>Value: ${node.value || 'N/A'}</small>
        </div>
    `).join('');
}

/**
 * Populate edge list with detailed descriptions
 */
function populateEdgeList(edges) {
    const container = document.getElementById('edge-list');
    container.innerHTML = edges.map(edge => `
        <div class="edge-item">
            <strong>${edge.from}</strong> 
            <i class="fas fa-arrow-right"></i> 
            <strong>${edge.to}</strong><br>
            <small>
                <strong>Relationship:</strong> ${getRelationshipDescription(edge.label)}<br>
                <strong>Strength:</strong> ${(edge.strength || 0.5).toFixed(1)}/1.0
                ${getStrengthDescription(edge.strength)}
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
 * Get human-readable relationship description
 */
function getRelationshipDescription(label) {
    const descriptions = {
        'causes': '🔴 Directly causes',
        'influences': '🔵 Strongly influences',
        'triggers': '⚡ Triggers or activates',
        'correlates_with': '📊 Statistically correlates with',
        'leads_to': '➡️ Leads to over time',
        'affects': '💫 Affects or impacts',
        'drives': '🚀 Drives or pushes',
        'relates to': '🔗 Related to'
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
