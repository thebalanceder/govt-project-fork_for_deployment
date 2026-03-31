// CSPOPS - Main Application JavaScript

// API Base URL
const API_BASE = '';

// Tab navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        
        // Add active class to clicked
        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

/**
 * Collect real-time data from all sources with detailed progress
 */
async function collectData() {
    const collectionTab = document.getElementById('collection');
    const progressBox = document.getElementById('collection-progress');
    const resultBox = document.getElementById('collection-result');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    // Switch to collection tab
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="collection"]').classList.add('active');
    collectionTab.classList.add('active');
    
    // Show progress
    progressBox.style.display = 'block';
    resultBox.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/collect`, { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            // Update UI
            document.getElementById('no-data-prompt').style.display = 'none';
            document.getElementById('dashboard-content').style.display = 'block';
            document.getElementById('live-badge').style.display = 'inline-block';

            // Update last update time
            document.getElementById('last-update').textContent = new Date().toLocaleString();

            // Load all data
            await loadAllData();

            // Show result - unified collection with economic, political, cultural
            const summary = result.summary || {};
            const total = summary.total_all || 
                         ((summary.total_economic || 0) + (summary.total_political || 0) + (summary.total_cultural || 0));
            const sourcesCount = (summary.sources_used || []).length;

            progressBox.style.display = 'none';
            resultBox.style.display = 'block';
            resultBox.innerHTML = `
                <h3><i class="fas fa-check-circle" style="color: #28a745;"></i> Collection Complete!</h3>
                <p><strong>Total Items:</strong> ${total} from ${sourcesCount} sources</p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    <div class="stat-card" style="border-left: 4px solid #4CAF50;">
                        <div class="stat-value">${summary.total_economic || 0}</div>
                        <div class="stat-label">📈 Economic</div>
                    </div>
                    <div class="stat-card" style="border-left: 4px solid #2196F3;">
                        <div class="stat-value">${summary.total_political || 0}</div>
                        <div class="stat-label">🏛️ Political</div>
                    </div>
                    <div class="stat-card" style="border-left: 4px solid #9C27B0;">
                        <div class="stat-value">${summary.total_cultural || 0}</div>
                        <div class="stat-label">🎭 Cultural</div>
                    </div>
                </div>
                ${summary.sources_used && summary.sources_used.length > 0 ? `
                    <div style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                        <strong>📡 Sources Used:</strong>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                            ${summary.sources_used.slice(0, 8).map(s => `<span class="badge">${s}</span>`).join('')}
                            ${summary.sources_used.length > 8 ? `<span class="badge">+${summary.sources_used.length - 8} more</span>` : ''}
                        </div>
                    </div>
                ` : ''}
                <button class="btn-primary" onclick="viewDashboard()" style="margin-top: 1.5rem;">
                    <i class="fas fa-chart-line"></i> View Dashboard
                </button>
            `;
        } else {
            progressBox.style.display = 'none';
            resultBox.style.display = 'block';
            resultBox.innerHTML = `<h3><i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i> Error</h3><p>${result.error || 'Unknown error'}</p>`;
        }
    } catch (error) {
        progressBox.style.display = 'none';
        resultBox.style.display = 'block';
        resultBox.innerHTML = `<h3><i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i> Network Error</h3><p>${error.message || 'Unknown error'}</p>`;
    }
}

/**
 * View dashboard after collection
 */
function viewDashboard() {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="dashboard"]').classList.add('active');
    document.getElementById('dashboard').classList.add('active');
}

/**
 * Load all data for tabs
 */
async function loadAllData() {
    await loadSentiment();
    await loadEconomy();
    await loadPolitics();
    await loadCulture();
    await loadAgents();
}

/**
 * Load sentiment data
 */
async function loadSentiment() {
    try {
        const response = await fetch(`${API_BASE}/api/sentiment`);
        const sentiment = await response.json();

        if (sentiment.overall_sentiment) {
            updateSentimentCards(sentiment.overall_sentiment);
        }

        if (sentiment.emotion_breakdown) {
            renderEmotionChart(sentiment.emotion_breakdown);
            updateDominantEmotion(sentiment.emotion_breakdown);
        }
    } catch (error) {
        console.error('Sentiment fetch error:', error);
    }
}

/**
 * Load political news data
 */
async function loadPolitics() {
    try {
        const response = await fetch(`${API_BASE}/api/data`);
        const data = await response.json();

        const container = document.getElementById('politics-content');
        if (!container) return;

        if (data.political && data.political.length > 0) {
            let html = `
                <div class="data-grid">
                    <h3><i class="fas fa-landmark"></i> Political News Articles</h3>
                    <div class="news-grid">
            `;

            for (const item of data.political.slice(0, 30)) {
                const sourceName = item.source || 'Unknown';
                const title = item.title || 'Untitled';
                const text = (item.text || '').substring(0, 200);
                const url = item.url || '#';
                const date = item.timestamp ? new Date(item.timestamp).toLocaleDateString() : '';

                html += `
                    <div class="news-card">
                        <div class="news-source">${sourceName}</div>
                        <h4 class="news-title">${title}</h4>
                        <p class="news-excerpt">${text}...</p>
                        <div class="news-meta">
                            <span class="news-date">${date}</span>
                            ${url !== '#' ? `<a href="${url}" target="_blank" class="news-link">Read More →</a>` : ''}
                        </div>
                    </div>
                `;
            }

            html += `</div></div>`;
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="prompt-box">
                    <i class="fas fa-info-circle fa-2x"></i>
                    <h3>No Political Data</h3>
                    <p>Collect data to see political news and analysis.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Politics fetch error:', error);
    }
}

/**
 * Load cultural news data
 */
async function loadCulture() {
    try {
        const response = await fetch(`${API_BASE}/api/data`);
        const data = await response.json();

        const container = document.getElementById('culture-content');
        if (!container) return;

        if (data.cultural && data.cultural.length > 0) {
            let html = `
                <div class="data-grid">
                    <h3><i class="fas fa-theater-masks"></i> Cultural News & Events</h3>
                    <div class="news-grid">
            `;

            for (const item of data.cultural.slice(0, 30)) {
                const sourceName = item.source || 'Unknown';
                const title = item.title || 'Untitled';
                const text = (item.text || '').substring(0, 200);
                const url = item.url || '#';
                const date = item.timestamp ? new Date(item.timestamp).toLocaleDateString() : '';

                html += `
                    <div class="news-card">
                        <div class="news-source">${sourceName}</div>
                        <h4 class="news-title">${title}</h4>
                        <p class="news-excerpt">${text}...</p>
                        <div class="news-meta">
                            <span class="news-date">${date}</span>
                            ${url !== '#' ? `<a href="${url}" target="_blank" class="news-link">Read More →</a>` : ''}
                        </div>
                    </div>
                `;
            }

            html += `</div></div>`;
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="prompt-box">
                    <i class="fas fa-info-circle fa-2x"></i>
                    <h3>No Cultural Data</h3>
                    <p>Collect data to see cultural news and events.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Culture fetch error:', error);
    }
}

/**
 * Load AI agent discussion results
 */
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/api/agents`);
        
        if (response.status === 404) {
            // No agent data available
            document.getElementById('agents-prompt').style.display = 'block';
            document.getElementById('agents-display').style.display = 'none';
            return;
        }
        
        const data = await response.json();
        
        // Show agent display
        document.getElementById('agents-prompt').style.display = 'none';
        document.getElementById('agents-display').style.display = 'block';
        
        // Load agent cards for economic topic
        const agentGrid = document.getElementById('agent-grid');
        const economicData = data.economic || {};
        const forecasts = economicData.agent_forecasts || {};
        
        const agentInfo = {
            'Dr. Lim Wei Chen': { title: 'Chief Economist', icon: '👨‍💼' },
            'Datin Sri Aisha binti Abdullah': { title: 'Policy Advisor', icon: '👩‍💼' },
            'Encik Razak bin Ibrahim': { title: 'Business Leader', icon: '👨‍💼' },
            'Dr. Muthu a/l Krishnan': { title: 'Sociologist', icon: '👨‍🔬' },
            'Ms. Wong Li Ming': { title: 'IR Expert', icon: '👩‍💼' },
            'Ahmad bin Hassan': { title: 'Public Representative', icon: '👤' }
        };
        
        agentGrid.innerHTML = `
            <h3 style="margin-bottom: 1.5rem;"><i class="fas fa-users"></i> 6 Expert AI Agents - Economic Analysis</h3>
            <div class="agent-cards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
                ${Object.entries(forecasts).map(([name, forecast]) => {
                    const info = agentInfo[name] || { title: 'Analyst', icon: '👤' };
                    const sentimentClass = forecast.sentiment > 0.1 ? 'positive' : forecast.sentiment < -0.1 ? 'negative' : 'neutral';
                    const sentimentLabel = forecast.sentiment > 0.1 ? 'Optimistic' : forecast.sentiment < -0.1 ? 'Concerned' : 'Neutral';
                    const sentimentColor = forecast.sentiment > 0.1 ? '#4CAF50' : forecast.sentiment < -0.1 ? '#f44336' : '#9E9E9E';
                    
                    return `
                    <div class="agent-card" style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: var(--shadow); border-left: 4px solid ${sentimentColor};">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <span style="font-size: 2rem; margin-right: 0.75rem;">${info.icon}</span>
                            <div>
                                <h4 style="margin: 0; font-size: 1rem;">${name}</h4>
                                <div style="font-size: 0.85rem; color: #666;">${info.title}</div>
                            </div>
                        </div>
                        <div class="sentiment-badge" style="display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; background: ${sentimentColor}; color: white; font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem;">
                            ${sentimentLabel} (${forecast.sentiment.toFixed(2)})
                        </div>
                        <div class="forecast" style="font-size: 0.9rem; color: #666;">
                            <div style="margin-bottom: 0.5rem;"><strong>7-day:</strong> ${forecast.forecast_7d.toFixed(2)}</div>
                            <div style="margin-bottom: 0.5rem;"><strong>30-day:</strong> ${forecast.forecast_30d.toFixed(2)}</div>
                            <div><strong>Confidence:</strong> ${(forecast.confidence * 100).toFixed(0)}%</div>
                        </div>
                    </div>
                `;
                }).join('')}
            </div>
        `;
        
        // Load consensus cards
        const consensusCards = document.getElementById('consensus-cards');
        const topics = ['economic', 'political', 'cultural'];
        const topicIcons = { economic: '📈', political: '🏛️', cultural: '🎭' };
        const topicLabels = { economic: 'Economic', political: 'Political', cultural: 'Cultural' };
        
        consensusCards.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                ${topics.map(topic => {
                    const topicData = data[topic] || {};
                    const consensus = topicData.final_consensus || 0;
                    const convergence = topicData.convergence_rate || 0;
                    const consensusLabel = consensus > 0.1 ? 'Positive' : consensus < -0.1 ? 'Negative' : 'Neutral';
                    const consensusColor = consensus > 0.1 ? '#4CAF50' : consensus < -0.1 ? '#f44336' : '#9E9E9E';
                    
                    return `
                    <div class="consensus-card" style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: var(--shadow);">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">${topicIcons[topic]} ${topicLabels[topic]}</div>
                        <div class="consensus-value" style="font-size: 1.8rem; font-weight: bold; color: ${consensusColor}; margin-bottom: 0.5rem;">
                            ${consensus.toFixed(2)} (${consensusLabel})
                        </div>
                        <div class="convergence" style="font-size: 0.9rem; color: #666;">
                            <strong>Convergence:</strong> ${(convergence * 100).toFixed(0)}%
                            <div style="background: #e0e0e0; border-radius: 10px; height: 8px; margin-top: 0.5rem;">
                                <div style="background: ${consensusColor}; border-radius: 10px; height: 100%; width: ${(convergence * 100).toFixed(0)}%;"></div>
                            </div>
                        </div>
                    </div>
                `;
                }).join('')}
            </div>
        `;
        
        // Load explanation
        const explanationContent = document.getElementById('explanation-content');
        const explanation = economicData.explanation || 'No detailed explanation available.';
        
        // Load indicator explanations
        const indicatorExplanations = economicData.indicator_explanations || {};
        
        explanationContent.innerHTML = `
            <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: var(--shadow); margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 1rem;"><i class="fas fa-lightbulb"></i> AI Insights</h4>
                <div style="white-space: pre-line; line-height: 1.8;">${explanation}</div>
            </div>
            
            <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: var(--shadow);">
                <h4 style="margin-bottom: 1rem;"><i class="fas fa-info-circle"></i> Key Indicators Explained</h4>
                <div class="indicator-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                    ${Object.entries(indicatorExplanations).slice(0, 6).map(([key, value]) => `
                        <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 3px solid #667eea;">
                            <div style="font-weight: 600; color: #667eea; margin-bottom: 0.5rem; text-transform: capitalize;">
                                ${key.replace(/_/g, ' ')}
                            </div>
                            <div style="font-size: 0.9rem; color: #666; line-height: 1.6;">
                                ${value}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Agents fetch error:', error);
    }
}

/**
 * Load economy data
 */
async function loadEconomy() {
    try {
        const response = await fetch(`${API_BASE}/api/data`);
        const data = await response.json();

        const container = document.getElementById('economy-content');
        if (!container) return;

        if (data.economic && data.economic.length > 0) {
            let html = `
                <div class="data-grid">
                    <h3><i class="fas fa-chart-line"></i> Economic Indicators & News</h3>
                    <div class="news-grid">
            `;

            // Show economic indicators first (items with values)
            const indicators = data.economic.filter(item => item.value !== null && item.value !== undefined);
            const articles = data.economic.filter(item => item.value === null || item.value === undefined);

            if (indicators.length > 0) {
                html += `
                    <div class="indicators-section" style="grid-column: 1 / -1;">
                        <h4 style="margin-bottom: 1rem;"><i class="fas fa-chart-bar"></i> Key Economic Indicators</h4>
                        <div class="indicators-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                `;
                for (const item of indicators.slice(0, 6)) {
                    const sourceName = item.source || 'Unknown';
                    const title = item.title || 'Economic Indicator';
                    const value = typeof item.value === 'number' ? item.value.toFixed(2) : item.value;
                    html += `
                        <div class="indicator-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                            <div class="indicator-source" style="font-size: 0.85rem; opacity: 0.9;">${sourceName}</div>
                            <div class="indicator-value" style="font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;">${value}</div>
                            <div class="indicator-title" style="font-size: 0.9rem;">${title}</div>
                        </div>
                    `;
                }
                html += `</div></div>`;
            }

            // Show articles
            for (const item of articles.slice(0, 20)) {
                const sourceName = item.source || 'Unknown';
                const title = item.title || 'Untitled';
                const text = (item.text || '').substring(0, 200);
                const url = item.url || '#';
                const date = item.timestamp ? new Date(item.timestamp).toLocaleDateString() : '';

                html += `
                    <div class="news-card">
                        <div class="news-source">${sourceName}</div>
                        <h4 class="news-title">${title}</h4>
                        <p class="news-excerpt">${text}...</p>
                        <div class="news-meta">
                            <span class="news-date">${date}</span>
                            ${url !== '#' ? `<a href="${url}" target="_blank" class="news-link">Read More →</a>` : ''}
                        </div>
                    </div>
                `;
            }

            html += `</div></div>`;
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="prompt-box">
                    <i class="fas fa-info-circle fa-2x"></i>
                    <h3>No Economic Data</h3>
                    <p>Collect data to see economic indicators and news.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Economy fetch error:', error);
        const container = document.getElementById('economy-content');
        if (container) {
            container.innerHTML = `<p class="error"><i class="fas fa-exclamation-triangle"></i> Error loading economy data: ${error.message}</p>`;
        }
    }
}

/**
 * Load news data
 */
async function loadNews() {
    try {
        const response = await fetch(`${API_BASE}/api/news`);
        const data = await response.json();
        
        const container = document.getElementById('news-content');
        if (!container) return;
        
        if (data.news && data.news.length > 0) {
            // Group by source
            const bySource = {};
            data.news.forEach(item => {
                const source = item.source || 'Unknown';
                if (!bySource[source]) bySource[source] = [];
                bySource[source].push(item);
            });
            
            let html = `<h3><i class="fas fa-newspaper"></i> Malaysian News Sources</h3>`;
            
            for (const [source, articles] of Object.entries(bySource)) {
                html += `
                    <div class="source-section">
                        <h4><i class="fas fa-bullhorn"></i> ${source} (${articles.length} articles)</h4>
                        <ul class="article-list">
                `;
                
                articles.slice(0, 10).forEach(article => {
                    html += `
                        <li class="article-item">
                            <div class="article-title">${article.title || article.text?.substring(0, 100) || 'No title'}</div>
                            <div class="article-meta">
                                <span class="article-time">${new Date(article.timestamp).toLocaleString()}</span>
                                ${article.url ? `<a href="${article.url}" target="_blank" class="article-link"><i class="fas fa-external-link-alt"></i> Read more</a>` : ''}
                            </div>
                        </li>
                    `;
                });
                
                html += `
                        </ul>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="no-data"><i class="fas fa-info-circle"></i> No news data collected yet</p>';
        }
    } catch (error) {
        console.error('News fetch error:', error);
        const container = document.getElementById('news-content');
        if (container) {
            container.innerHTML = `<p class="error"><i class="fas fa-exclamation-triangle"></i> Error loading news data: ${error.message}</p>`;
        }
    }
}

/**
 * Load social media data - Clean display without redundant comments
 */
async function loadSocial() {
    try {
        const response = await fetch(`${API_BASE}/api/social`);
        const data = await response.json();
        
        const container = document.getElementById('sentiment-content');
        if (!container) return;
        
        if (data.social_media && data.social_media.length > 0) {
            // Group by platform
            const byPlatform = {};
            data.social_media.forEach(item => {
                const platform = item.source || 'Unknown';
                if (!byPlatform[platform]) byPlatform[platform] = [];
                byPlatform[platform].push(item);
            });
            
            let html = `<h3><i class="fas fa-comments"></i> Social Media Sentiment</h3>`;
            
            for (const [platform, posts] of Object.entries(byPlatform)) {
                html += `
                    <div class="platform-section">
                        <h4><i class="fas fa-share-alt"></i> ${platform} (${posts.length} posts)</h4>
                        <div class="post-grid">
                `;
                
                posts.slice(0, 12).forEach(post => {
                    const sentimentHint = post.metadata?.sentiment_hint || 'neutral';
                    const sentimentIcon = sentimentHint === 'positive' ? '😊' : sentimentHint === 'negative' ? '😞' : '😐';
                    
                    html += `
                        <div class="post-card sentiment-${sentimentHint}">
                            <div class="post-header">
                                <span class="sentiment-emoji">${sentimentIcon}</span>
                                <span class="post-time">${new Date(post.timestamp).toLocaleString()}</span>
                            </div>
                            <div class="post-text">${post.text || 'No content'}</div>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="no-data"><i class="fas fa-info-circle"></i> No social media data collected yet</p>';
        }
    } catch (error) {
        console.error('Social fetch error:', error);
        const container = document.getElementById('sentiment-content');
        if (container) {
            container.innerHTML = `<p class="error"><i class="fas fa-exclamation-triangle"></i> Error: ${error.message}</p>`;
        }
    }
}

/**
 * Load government services with AI explanations
 */
async function loadGovernment() {
    try {
        const response = await fetch(`${API_BASE}/api/services`);
        const data = await response.json();
        
        const container = document.getElementById('services-content');
        if (!container) return;
        
        if (data.government && data.government.length > 0) {
            let html = `<h3><i class="fas fa-building"></i> Government Services - AI Analysis</h3>`;
            
            // Show AI explanations by agency
            for (const [agency, explanation] of Object.entries(data.agency_explanations || {})) {
                const datasets = data.by_agency[agency] || [];
                
                html += `
                    <div class="agency-section">
                        <h4><i class="fas fa-landmark"></i> ${agency}</h4>
                        <div class="ai-explanation">
                            <div class="explanation-performance">
                                <strong><i class="fas fa-chart-bar"></i> Performance:</strong>
                                ${explanation.performance}
                            </div>
                            <div class="explanation-analysis">
                                <strong><i class="fas fa-brain"></i> AI Analysis:</strong>
                                ${explanation.analysis}
                            </div>
                            <div class="explanation-recommendation">
                                <strong><i class="fas fa-lightbulb"></i> Recommendation:</strong>
                                ${explanation.recommendation}
                            </div>
                        </div>
                        <div class="dataset-list">
                `;
                
                datasets.forEach(dataset => {
                    const value = dataset.value !== null ? dataset.value : 'N/A';
                    const unit = dataset.metadata?.unit || '';
                    
                    html += `
                        <div class="dataset-card">
                            <div class="dataset-name">${dataset.title || dataset.text?.substring(0, 80) || 'Unknown'}</div>
                            <div class="dataset-value">${value} ${unit}</div>
                            <div class="dataset-source">${dataset.metadata?.source_url || 'data.gov.my'}</div>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="no-data"><i class="fas fa-info-circle"></i> No government data collected yet</p>';
        }
    } catch (error) {
        console.error('Government fetch error:', error);
        const container = document.getElementById('services-content');
        if (container) {
            container.innerHTML = `<p class="error"><i class="fas fa-exclamation-triangle"></i> Error: ${error.message}</p>`;
        }
    }
}

/**
 * Load crises data
 */
async function loadCrises() {
    try {
        const response = await fetch(`${API_BASE}/api/crises`);
        const data = await response.json();
        
        const container = document.getElementById('crises-content');
        if (!container) return;
        
        if (data.crises && data.crises.length > 0) {
            let html = `<h3><i class="fas fa-exclamation-triangle"></i> Crisis Monitoring & Alerts</h3>`;
            
            for (const crisis of data.crises) {
                const severityColor = crisis.severity === 'warning' ? '#dc3545' : crisis.severity === 'info' ? '#ffc107' : '#28a745';
                const severityIcon = crisis.severity === 'warning' ? '⚠️' : crisis.severity === 'info' ? 'ℹ️' : '✅';
                
                html += `
                    <div class="crisis-card" style="border-left: 4px solid ${severityColor}">
                        <div class="crisis-header">
                            <span class="crisis-icon">${severityIcon}</span>
                            <span class="crisis-type">${crisis.type}</span>
                            <span class="crisis-title">${crisis.title}</span>
                        </div>
                        <div class="crisis-description">${crisis.description}</div>
                        <div class="crisis-recommendation">
                            <strong>Recommendation:</strong> ${crisis.recommendation}
                        </div>
                        <div class="crisis-time">${new Date(crisis.timestamp).toLocaleString()}</div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="no-data"><i class="fas fa-info-circle"></i> No crisis data available</p>';
        }
    } catch (error) {
        console.error('Crises fetch error:', error);
        const container = document.getElementById('crises-content');
        if (container) {
            container.innerHTML = `<p class="error"><i class="fas fa-exclamation-triangle"></i> Error: ${error.message}</p>`;
        }
    }
}

/**
 * Fetch dashboard status
 */
async function fetchStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const status = await response.json();
        
        if (status.collected) {
            document.getElementById('last-update').textContent = status.last_update;
        }
    } catch (error) {
        console.error('Status fetch error:', error);
    }
}

/**
 * Load sentiment analysis data
 */
async function loadSentiment() {
    try {
        const response = await fetch(`${API_BASE}/api/sentiment`);
        const sentiment = await response.json();
        
        if (sentiment.overall_sentiment) {
            updateSentimentCards(sentiment.overall_sentiment);
        }
        
        if (sentiment.emotion_breakdown) {
            renderEmotionChart(sentiment.emotion_breakdown);
            updateDominantEmotion(sentiment.emotion_breakdown);
        }
    } catch (error) {
        console.error('Sentiment fetch error:', error);
    }
}

/**
 * Update sentiment cards
 */
function updateSentimentCards(sentiment) {
    const score = sentiment.average_score || 0;
    const classification = sentiment.classification || 'neutral';
    const positivePct = (sentiment.positive_percentage || 0) * 100;
    const negativePct = (sentiment.negative_percentage || 0) * 100;
    const neutralPct = 100 - positivePct - negativePct;
    
    // Overall sentiment card
    const emoji = score > 0.1 ? '😊' : score < -0.1 ? '😞' : '😐';
    const color = score > 0.1 ? '#28a745' : score < -0.1 ? '#dc3545' : '#ffc107';
    
    document.getElementById('overall-emoji').textContent = emoji;
    document.getElementById('overall-score').textContent = (score > 0 ? '+' : '') + score.toFixed(2);
    document.getElementById('overall-score').style.color = color;
    document.getElementById('overall-class').textContent = classification.toUpperCase();
    document.getElementById('overall-class').style.background = color + '33';
    document.getElementById('overall-class').style.color = color;
    
    // Percentage cards
    document.getElementById('positive-pct').textContent = positivePct.toFixed(0) + '%';
    document.getElementById('negative-pct').textContent = negativePct.toFixed(0) + '%';
    document.getElementById('neutral-pct').textContent = neutralPct.toFixed(0) + '%';
}

/**
 * Render emotion bar chart using Plotly
 */
function renderEmotionChart(emotions) {
    const labels = Object.keys(emotions);
    const values = labels.map(l => emotions[l] * 100);
    
    const colors = labels.map(l => {
        const colorMap = {
            'joy': '#28a745',
            'anger': '#dc3545',
            'fear': '#6f42c1',
            'sadness': '#17a2b8',
            'surprise': '#fd7e14',
            'disgust': '#ffc107',
            'neutral': '#6c757d'
        };
        return colorMap[l.toLowerCase()] || '#999999';
    });
    
    const trace = {
        x: labels,
        y: values,
        type: 'bar',
        marker: { color: colors },
        text: values.map(v => v.toFixed(1) + '%'),
        textposition: 'outside'
    };
    
    const layout = {
        title: 'Dominant Emotions in Public Discourse',
        xaxis: { title: 'Emotion' },
        yaxis: { title: 'Percentage', range: [0, Math.max(...values) * 1.2] },
        height: 350,
        showlegend: false,
        margin: { t: 50, b: 50, l: 50, r: 20 }
    };
    
    Plotly.newPlot('emotion-bar-chart', [trace], layout);
}

/**
 * Update dominant emotion highlight
 */
function updateDominantEmotion(emotions) {
    const dominant = Object.entries(emotions).reduce((a, b) => a[1] > b[1] ? a : b);
    const name = dominant[0];
    const pct = dominant[1] * 100;
    
    const emojiMap = {
        'joy': '😊',
        'anger': '😠',
        'fear': '😨',
        'sadness': '😢',
        'surprise': '😲',
        'disgust': '🤢',
        'neutral': '😐'
    };
    
    const insightMap = {
        'joy': '✅ Positive public mood - good time for policy announcements',
        'anger': '⚠️ High anger levels - consider proactive communication',
        'fear': '⚠️ Public anxiety detected - address concerns directly',
        'sadness': 'ℹ️ Sadness detected - empathy-focused messaging recommended',
        'surprise': 'ℹ️ High surprise - ensure clear communication on developments',
        'disgust': '⚠️ Disgust detected - investigate source of negative reaction',
        'neutral': 'ℹ️ Mixed emotions - monitor for trends'
    };
    
    document.querySelector('.highlight-emoji').textContent = emojiMap[name.toLowerCase()] || '😐';
    document.getElementById('dominant-emotion-name').textContent = name;
    document.getElementById('dominant-emotion-pct').textContent = pct.toFixed(0) + '%';
    document.getElementById('emotion-insight').textContent = insightMap[name.toLowerCase()] || insightMap['neutral'];
}

/**
 * Generate AI cause-effect graph
 */
async function generateGraph() {
    const btn = document.getElementById('generate-graph-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI is Analyzing...';
    
    // Show loading, hide results
    document.getElementById('graph-loading').style.display = 'block';
    document.getElementById('graph-container').style.display = 'none';
    
    // Switch to graph tab
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="graph"]').classList.add('active');
    document.getElementById('graph').classList.add('active');
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-graph`, { method: 'POST' });
        const graphData = await response.json();
        
        if (response.ok && graphData.nodes) {
            // Hide loading, show graph
            document.getElementById('graph-loading').style.display = 'none';
            document.getElementById('graph-container').style.display = 'block';
            
            // Render the D3.js graph
            renderGraph(graphData);
            
            btn.innerHTML = '<i class="fas fa-redo"></i> Regenerate Graph';
        } else {
            alert('✗ Error: ' + (graphData.error || 'Failed to generate graph'));
            btn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Cause-Effect Map';
        }
    } catch (error) {
        alert('✗ Network error: ' + error.message);
        btn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Cause-Effect Map';
    } finally {
        btn.disabled = false;
    }
}

/**
 * Generate executive summary
 */
async function generateSummary() {
    const btn = event.target.closest('button');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    
    try {
        const response = await fetch(`${API_BASE}/api/summary`);
        const result = await response.json();
        
        if (response.ok) {
            document.getElementById('summary-display').style.display = 'block';
            document.getElementById('summary-content').textContent = result.summary;
        } else {
            alert('✗ Error: ' + result.error);
        }
    } catch (error) {
        alert('✗ Network error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-file-alt"></i> Generate Executive Summary';
    }
}

/**
 * Send chat message
 */
async function sendChat() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addChatMessage(message, 'user');
    input.value = '';
    
    // Get AI response
    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            addChatMessage(result.response, 'ai');
        } else {
            addChatMessage('Error: ' + result.error, 'ai');
        }
    } catch (error) {
        addChatMessage('Network error: ' + error.message, 'ai');
    }
}

/**
 * Add message to chat
 */
function addChatMessage(text, sender) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-message ${sender}`;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

/**
 * Handle chat input Enter key
 */
function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChat();
    }
}

/**
 * Download graph data
 */
function downloadGraph() {
    if (typeof window.downloadGraph === 'function') {
        window.downloadGraph();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
});
