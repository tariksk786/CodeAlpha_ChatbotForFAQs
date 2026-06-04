/**
 * Analytics Dashboard JS for AI FAQ Chatbot
 * Fetches log aggregates and builds Chart.js canvases, stats cards, and lists.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error("Chart.js is not loaded. Analytics charts will be disabled.");
        return;
    }

    // Colors config to match premium theme
    const chartColors = {
        primary: '#4F46E5',
        secondary: '#7C3AED',
        accent: '#06B6D4',
        darkBg: '#1e293b',
        gridLine: 'rgba(255, 255, 255, 0.05)',
        text: '#94A3B8'
    };

    // Chart instances
    let trendsChart = null;
    let categoryChart = null;
    let topFaqsChart = null;

    // Load initial analytics
    loadAnalytics();

    // Fetch and draw analytics dashboard elements
    function loadAnalytics() {
        fetch('/api/analytics')
            .then(res => {
                if (!res.ok) throw new Error("HTTP error " + res.status);
                return res.json();
            })
            .then(data => {
                populateStatsCards(data.summary);
                buildTrendsChart(data.daily_trends);
                buildCategoryChart(data.categories);
                buildTopFaqsChart(data.top_questions);
                populateRecentLogsTable(data.recent_queries);
            })
            .catch(err => {
                console.error("Failed to load analytics data:", err);
                Swal.fire("Analytics Error", "Failed to retrieve statistics logs from database.", "error");
            });
    }

    // Populate the dashboard stats cards
    function populateStatsCards(summary) {
        document.getElementById('stat-total-queries').innerText = summary.total_queries || 0;
        document.getElementById('stat-avg-confidence').innerText = `${summary.avg_confidence || 0}%`;
        document.getElementById('stat-total-faqs').innerText = summary.total_faqs || 0;
        
        // Calculate feedback accuracy (Thumbs Up / Total Feedback)
        const totalFeedback = summary.positive_feedback + summary.negative_feedback;
        const feedbackRate = totalFeedback > 0 
            ? Math.round((summary.positive_feedback / totalFeedback) * 100)
            : 100;
        
        document.getElementById('stat-feedback-rate').innerText = `${feedbackRate}%`;
        document.getElementById('stat-feedback-subtext').innerText = `${summary.positive_feedback} Up / ${summary.negative_feedback} Down`;
    }

    // Build the Daily Query Volume Line Chart
    function buildTrendsChart(trends) {
        const ctx = document.getElementById('chart-trends');
        if (!ctx) return;

        // Extract labels and dataset values
        const labels = trends.map(t => t.date);
        const counts = trends.map(t => t.count);
        const confidences = trends.map(t => t.avg_confidence);

        if (trendsChart) trendsChart.destroy();

        trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Queries count',
                        data: counts,
                        borderColor: chartColors.accent,
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Avg Confidence (%)',
                        data: confidences,
                        borderColor: chartColors.secondary,
                        borderDash: [5, 5],
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: chartColors.text }
                    }
                },
                scales: {
                    x: {
                        grid: { color: chartColors.gridLine },
                        ticks: { color: chartColors.text }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: { color: chartColors.gridLine },
                        ticks: { color: chartColors.text, stepSize: 1 },
                        title: {
                            display: true,
                            text: 'Query Volume',
                            color: chartColors.text
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: chartColors.text, min: 0, max: 100 },
                        title: {
                            display: true,
                            text: 'Confidence Score (%)',
                            color: chartColors.text
                        }
                    }
                }
            }
        });
    }

    // Build Category Distribution Doughnut Chart
    function buildCategoryChart(categories) {
        const ctx = document.getElementById('chart-categories');
        if (!ctx) return;

        // Skip drawing if categories are empty
        if (categories.length === 0) {
            ctx.parentNode.innerHTML = `<div class="d-flex h-100 align-items-center justify-content-center text-muted">No category data logged yet.</div>`;
            return;
        }

        const labels = categories.map(c => c.category);
        const counts = categories.map(c => c.query_count);

        if (categoryChart) categoryChart.destroy();

        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        '#4F46E5', '#7C3AED', '#06B6D4', '#EC4899', '#10B981', '#F59E0B'
                    ],
                    borderWidth: 1,
                    borderColor: 'rgba(15, 23, 42, 0.5)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: chartColors.text, boxWidth: 12 }
                    }
                }
            }
        });
    }

    // Build Top Matched FAQs horizontal bar chart
    function buildTopFaqsChart(topFaqs) {
        const ctx = document.getElementById('chart-top-faqs');
        if (!ctx) return;

        if (topFaqs.length === 0) {
            ctx.parentNode.innerHTML = `<div class="d-flex h-100 align-items-center justify-content-center text-muted">No queries logged yet.</div>`;
            return;
        }

        // Truncate questions for labels to fit chart
        const labels = topFaqs.map(f => f.question.length > 30 ? f.question.slice(0, 30) + '...' : f.question);
        const counts = topFaqs.map(f => f.match_count);

        if (topFaqsChart) topFaqsChart.destroy();

        topFaqsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Match count',
                    data: counts,
                    backgroundColor: chartColors.secondary,
                    borderRadius: 6,
                    borderWidth: 0
                }]
            },
            options: {
                indexAxis: 'y', // Makes it horizontal
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: chartColors.gridLine },
                        ticks: { color: chartColors.text, stepSize: 1 }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: chartColors.text }
                    }
                }
            }
        });
    }

    // Populate query logs table
    function populateRecentLogsTable(queries) {
        const tableBody = document.getElementById('recent-logs-table-body');
        if (!tableBody) return;

        tableBody.innerHTML = '';

        if (queries.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-3">No query log records available.</td>
                </tr>
            `;
            return;
        }

        queries.forEach(log => {
            const tr = document.createElement('tr');
            
            // Format timestamp (YYYY-MM-DD HH:MM)
            let formattedTime = log.timestamp;
            try {
                const date = new Date(log.timestamp);
                formattedTime = date.toLocaleString();
            } catch(e) {}

            // Format confidence badge
            let confClass = 'confidence-low';
            if (log.confidence >= 75) confClass = 'confidence-high';
            else if (log.confidence >= 40) confClass = 'confidence-medium';
            
            const confBadge = `<span class="confidence-badge ${confClass}">${log.confidence}%</span>`;

            // Format feedback badge
            let feedbackIcon = '<span class="text-muted">-</span>';
            if (log.feedback === 1) {
                feedbackIcon = '<span class="text-success" title="Helpful"><i class="fas fa-thumbs-up"></i></span>';
            } else if (log.feedback === -1) {
                feedbackIcon = '<span class="text-danger" title="Unhelpful"><i class="fas fa-thumbs-down"></i></span>';
            }

            const matchedQuestion = log.matched_question 
                ? `<span class="text-truncate d-inline-block" style="max-width: 250px;">${escapeHtml(log.matched_question)}</span>` 
                : `<span class="text-muted font-italic">Fallback Response</span>`;

            tr.innerHTML = `
                <td><small class="text-muted">${formattedTime}</small></td>
                <td><strong class="text-truncate d-inline-block" style="max-width: 250px;">${escapeHtml(log.query_text)}</strong></td>
                <td>${matchedQuestion}</td>
                <td>${confBadge}</td>
                <td class="text-center">${feedbackIcon}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }
});
