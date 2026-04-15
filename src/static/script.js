// Benford's Law Analyzer - Client-side JavaScript with Chart.js

let benfordChart = null; // Store chart instance for cleanup

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyzeForm');
    const textSection = document.getElementById('textInputSection');
    const urlSection = document.getElementById('urlInputSection');
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsDiv = document.getElementById('results');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Toggle between text and URL input
    document.querySelectorAll('input[name="input_type"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'text') {
                textSection.classList.remove('hidden');
                urlSection.classList.add('hidden');
            } else {
                textSection.classList.add('hidden');
                urlSection.classList.remove('hidden');
            }
        });
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous results
        errorDiv.classList.add('hidden');
        resultsDiv.classList.add('hidden');
        loading.classList.remove('hidden');
        analyzeBtn.disabled = true;

        const inputType = document.querySelector('input[name="input_type"]:checked').value;
        const digits = Array.from(document.querySelectorAll('input[name="digits"]:checked'))
            .map(cb => parseInt(cb.value));

        let content, source;

        if (inputType === 'text') {
            content = document.getElementById('content').value.trim();
            if (content.length < 10) {
                showError('Please enter some text to analyze.');
                return;
            }
            source = 'article';
        } else {
            content = document.getElementById('url').value.trim();
            if (!content) {
                showError('Please enter a URL to analyze.');
                return;
            }
            source = 'url';
        }

        if (digits.length === 0) {
            showError('Please select at least one digit position to analyze.');
            return;
        }

        try {
            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    source: source,
                    digits: digits
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Analysis failed');
            }

            displayResults(data);
        } catch (err) {
            showError(err.message);
        } finally {
            loading.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function showError(message) {
        loading.classList.add('hidden');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }

    function displayResults(data) {
        document.getElementById('numbersFound').textContent = data.numbers_found;
        document.getElementById('contentPreview').textContent = 
            data.content_preview ? data.content_preview.substring(0, 100) + '...' : '-';

        const detailsDiv = document.getElementById('analysisDetails');
        detailsDiv.innerHTML = '';

        // Calculate aggregate authenticity score and collect flags
        let totalChiSq = 0;
        let analysisCount = 0;
        let isSuspiciousOverall = false;
        let allFlags = [];

        for (const [digitPos, result] of Object.entries(data.results)) {
            if (result.error) {
                detailsDiv.innerHTML += `
                    <div class="analysis-block">
                        <h3>Digit Position ${digitPos}</h3>
                        <p class="error">${result.error}</p>
                    </div>
                `;
                continue;
            }

            totalChiSq += result.chi_squared;
            analysisCount++;
            if (result.is_suspicious) {
                isSuspiciousOverall = true;
            }

            // Identify flags for this digit position
            const digitFlags = findFlags(digitPos, result);
            allFlags = allFlags.concat(digitFlags);

            // Calculate authenticity score for this digit position
            const digitAuthScore = calculateAuthScore(result);
            result.digitAuthScore = digitAuthScore;

            const verdictClass = result.is_suspicious ? 'suspicious' : 'normal';
            const tableRows = generateFrequencyTable(digitPos, result);
            const chartId = `chart-${digitPos}`;
            
            detailsDiv.innerHTML += `
                <div class="analysis-block">
                    <h3>
                        Digit Position ${digitPos}
                        <span class="verdict ${verdictClass}">${result.verdict}</span>
                    </h3>
                    
                    <div class="stats-row">
                        <div class="stat">
                            <span class="stat-label">Sample Size:</span>
                            <span class="stat-value">${result.sample_size}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Chi-squared:</span>
                            <span class="stat-value">${result.chi_squared}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">p-value:</span>
                            <span class="stat-value">${result.p_value}</span>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="${chartId}"></canvas>
                    </div>
                    
                    ${tableRows}
                    
                    <div class="explanation">
                        <strong>Explanation:</strong> ${result.explanation}
                    </div>
                </div>
            `;

            // Render the chart after adding the canvas
            renderChart(chartId, digitPos, result);
        }

        // Add verdict panel
        const avgChiSq = analysisCount > 0 ? totalChiSq / analysisCount : 0;
        const overallAuthScore = calculateOverallAuthScore(avgChiSq, isSuspiciousOverall);
        const verdictText = isSuspiciousOverall ? 'Distribution appears unusual' : 'Distribution appears normal';
        const verdictSubtitle = isSuspiciousOverall 
            ? 'This data may have been manipulated or is not naturally occurring'
            : 'This data follows the expected Benford distribution';

        detailsDiv.innerHTML = `
            <div class="verdict-panel">
                <div class="auth-score ${isSuspiciousOverall ? 'suspicious' : 'normal'}">${overallAuthScore}%</div>
                <div class="verdict-text">${verdictText}</div>
                <div class="verdict-subtitle">${verdictSubtitle}</div>
            </div>
        ` + detailsDiv.innerHTML;

        // Add flag list if there are any flags
        if (allFlags.length > 0) {
            const flagsHtml = allFlags.map(flag => `
                <div class="flag-item">
                    <header onclick="this.parentElement.classList.toggle('expanded')">
                        <span class="flag-title">${flag.title}</span>
                        <span class="flag-toggle">▼</span>
                    </header>
                    <div class="flag-detail">${flag.detail}</div>
                </div>
            `).join('');
            
            detailsDiv.innerHTML += `
                <div class="flag-list">
                    <h3>Detailed Anomalies</h3>
                    ${flagsHtml}
                </div>
            `;
        }

        resultsDiv.classList.remove('hidden');
    }

    function renderChart(canvasId, digitPos, result) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const digitLabels = digitPos === '1' 
            ? ['1', '2', '3', '4', '5', '6', '7', '8', '9']
            : ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if any
        if (benfordChart) {
            benfordChart.destroy();
        }

        benfordChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: digitLabels,
                datasets: [
                    {
                        label: 'Expected',
                        data: result.expected.map(e => (e * 100).toFixed(1)),
                        backgroundColor: 'rgba(37, 99, 235, 0.7)',
                        borderColor: 'rgba(37, 99, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Observed',
                        data: result.observed.map(o => (o * 100).toFixed(1)),
                        backgroundColor: 'rgba(249, 115, 22, 0.7)',
                        borderColor: 'rgba(249, 115, 22, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: `Digit Position ${digitPos} Distribution`
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency (%)'
                        }
                    }
                }
            }
        });
    }

    function calculateAuthScore(result) {
        // Map chi-squared to authenticity score (0-100)
        // Lower chi-squared = higher authenticity
        // chi-squared of 0 = 100% authentic, chi-squared of 20+ = lower authenticity
        const score = Math.max(0, Math.min(100, 100 - (result.chi_squared * 2)));
        return Math.round(score);
    }

    function calculateOverallAuthScore(avgChiSq, isSuspicious) {
        // Average chi-squared across all digit positions
        let score = Math.max(0, Math.min(100, 100 - (avgChiSq * 2)));
        
        // If any suspicious, reduce score
        if (isSuspicious) {
            score = Math.min(score, 70);
        }
        
        return Math.round(score);
    }

    function findFlags(digitPos, result) {
        const flags = [];
        const digitLabels = digitPos === '1' 
            ? [1, 2, 3, 4, 5, 6, 7, 8, 9]
            : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

        result.expected.forEach((exp, i) => {
            const obs = result.observed[i];
            const diff = (obs - exp) * 100;
            const absDiff = Math.abs(diff);

            // Flag if difference is more than 3%
            if (absDiff > 3) {
                const digit = digitLabels[i];
                const direction = diff > 0 ? 'more' : 'less';
                const pct = Math.abs(diff).toFixed(1);
                
                flags.push({
                    title: `Digit ${digit} appears ${pct}% ${direction} than expected`,
                    detail: `Expected: ${(exp * 100).toFixed(1)}%, Observed: ${(obs * 100).toFixed(1)}%. ` +
                            `This digit appears ${digitLabels[i]}% of the time when it should appear ${(exp * 100).toFixed(1)}% of the time.`
                });
            }
        });

        return flags;
    }

    function generateFrequencyTable(digitPos, result) {
        const digits = digitPos === '1' ? [1,2,3,4,5,6,7,8,9] : [0,1,2,3,4,5,6,7,8,9];
        
        let tableHTML = `
            <table class="frequency-table">
                <thead>
                    <tr>
                        <th>Digit</th>
                        ${digits.map(d => `<th>${d}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Expected %</strong></td>
                        ${result.expected.map(e => `<td>${(e * 100).toFixed(1)}%</td>`).join('')}
                    </tr>
                    <tr>
                        <td><strong>Observed %</strong></td>
                        ${result.observed.map((o, i) => `<td>${(o * 100).toFixed(1)}%</td>`).join('')}
                    </tr>
                    <tr>
                        <td><strong>Difference</strong></td>
                        ${result.expected.map((e, i) => {
                            const diff = (result.observed[i] - e) * 100;
                            const diffClass = diff > 0 ? 'diff-positive' : diff < 0 ? 'diff-negative' : '';
                            const sign = diff > 0 ? '+' : '';
                            return `<td class="${diffClass}">${sign}${diff.toFixed(1)}%</td>`;
                        }).join('')}
                    </tr>
                </tbody>
            </table>
        `;
        
        return tableHTML;
    }
});
