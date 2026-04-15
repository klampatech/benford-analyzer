// Benford's Law Analyzer - Client-side JavaScript

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

            const verdictClass = result.is_suspicious ? 'suspicious' : 'normal';
            const tableRows = generateFrequencyTable(digitPos, result);
            
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
                    
                    ${tableRows}
                    
                    <div class="explanation">
                        <strong>Explanation:</strong> ${result.explanation}
                    </div>
                </div>
            `;
        }

        resultsDiv.classList.remove('hidden');
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
