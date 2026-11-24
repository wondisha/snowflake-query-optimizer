"""
Enhanced Dashboard for Snowflake Optimizer
Provides web interface for analysis results
"""

from flask import Flask, jsonify, render_template_string
from datetime import datetime
import json

app = Flask(__name__)

# Sample dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Snowflake Optimization Dashboard</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .header { background: #1a73e8; color: white; padding: 20px; border-radius: 5px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .metric { display: inline-block; width: 23%; margin: 1%; text-align: center; }
        .metric-value { font-size: 32px; font-weight: bold; color: #1a73e8; }
        .metric-label { font-size: 12px; color: #666; }
        .issue { background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }
        .recommendation { background: #d1ecf1; padding: 10px; margin: 5px 0; border-left: 4px solid #17a2b8; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f9f9f9; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Snowflake Optimization Dashboard</h1>
            <p>Real-time analysis and recommendations</p>
        </div>

        <div class="card">
            <h2>Quick Metrics</h2>
            <div class="metric">
                <div class="metric-value" id="tables">80</div>
                <div class="metric-label">Tables Analyzed</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="size">29.9TB</div>
                <div class="metric-label">Total Size</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="issues">0</div>
                <div class="metric-label">Issues Found</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="savings">$0</div>
                <div class="metric-label">Potential Savings</div>
            </div>
        </div>

        <div class="card">
            <h2>Recent Analysis Results</h2>
            <p>Last run: <span id="lastrun">Never</span></p>
            <table>
                <tr>
                    <th>Database</th>
                    <th>Tables</th>
                    <th>Size</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>SNOWFLAKE_SAMPLE_DATA</td>
                    <td>80</td>
                    <td>29.9 TB</td>
                    <td>✓ Analyzed</td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>Top Recommendations</h2>
            <div class="recommendation">
                <strong>Add Clustering Keys</strong>
                <p>5 tables larger than 1GB would benefit from clustering keys on date/customer_id</p>
            </div>
            <div class="recommendation">
                <strong>Optimize Storage</strong>
                <p>Archive data older than 90 days to reduce storage costs by 20-30%</p>
            </div>
            <div class="recommendation">
                <strong>Query Optimization</strong>
                <p>Review top 10 queries using QUERY_HISTORY for performance improvements</p>
            </div>
        </div>

        <div class="card">
            <h2>Settings</h2>
            <p>
                <label>Analysis Frequency: 
                    <select>
                        <option>Hourly</option>
                        <option selected>Daily</option>
                        <option>Weekly</option>
                    </select>
                </label>
            </p>
            <p>
                <label>
                    <input type="checkbox" checked> Send Email Alerts
                </label>
            </p>
            <p>
                <label>
                    <input type="checkbox" checked> Send Slack Notifications
                </label>
            </p>
            <button onclick="saveSettings()">Save Settings</button>
        </div>
    </div>

    <script>
        // Fetch data from API
        fetch('/api/status')
            .then(r => r.json())
            .then(data => {
                document.getElementById('tables').textContent = data.tables || 0;
                document.getElementById('size').textContent = data.size || '0TB';
                document.getElementById('issues').textContent = data.issues || 0;
                document.getElementById('savings').textContent = '$' + (data.savings || 0);
                document.getElementById('lastrun').textContent = data.lastrun || 'Never';
            });

        function saveSettings() {
            alert('Settings saved!');
            // Send to backend
        }
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    return jsonify({
        'tables': 80,
        'size': '29.9TB',
        'issues': 0,
        'savings': 0,
        'lastrun': datetime.now().isoformat()
    })

@app.route('/api/recommendations')
def api_recommendations():
    return jsonify({
        'recommendations': [
            {'type': 'clustering', 'impact': 'high', 'savings': 1000},
            {'type': 'archiving', 'impact': 'medium', 'savings': 500}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
