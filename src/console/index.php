<?php
/**
 * =============================================================================
 * CENTRAL MULTI-TENANT FLEET CONTROL PLANE WEB CONSOLE
 * =============================================================================
 * Single-file, enterprise-grade responsive control dashboard providing fleet
 * observability, attack telemetry, node health, and policy administration.
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * =============================================================================
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Universal Security Vaccine | Enterprise Fleet Console</title>
    <style>
        :root {
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-border: #334155;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --accent: #38bdf8;
            --success: #22c55e;
            --danger: #ef4444;
            --warning: #f59e0b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--bg); color: var(--text-main); min-height: 100vh; padding: 24px; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--surface-border); padding-bottom: 20px; margin-bottom: 28px; }
        .logo-area { display: flex; align-items: center; gap: 14px; }
        .logo-badge { background: linear-gradient(135deg, #0284c7, #38bdf8); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; }
        h1 { font-size: 22px; font-weight: 700; }
        .tagline { color: var(--text-sub); font-size: 13px; margin-top: 2px; }
        .top-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; margin-bottom: 28px; }
        .stat-card { background: var(--surface); border: 1px solid var(--surface-border); border-radius: 10px; padding: 20px; }
        .stat-label { font-size: 12px; text-transform: uppercase; color: var(--text-sub); letter-spacing: 0.5px; font-weight: 600; }
        .stat-val { font-size: 28px; font-weight: 800; margin: 8px 0 4px; }
        .stat-desc { font-size: 12px; color: var(--text-sub); }
        .card-table { background: var(--surface); border: 1px solid var(--surface-border); border-radius: 10px; overflow: hidden; margin-bottom: 28px; }
        .card-header { padding: 18px 24px; border-bottom: 1px solid var(--surface-border); display: flex; justify-content: space-between; align-items: center; }
        .card-title { font-size: 16px; font-weight: 700; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
        th { background: #182234; padding: 14px 24px; color: var(--text-sub); font-weight: 600; border-bottom: 1px solid var(--surface-border); }
        td { padding: 14px 24px; border-bottom: 1px solid var(--surface-border); color: #e2e8f0; }
        .status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        .status-badge.green { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
        .status-badge.amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        code { background: #0b1120; padding: 2px 6px; border-radius: 4px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, monospace; color: #38bdf8; }
        footer { text-align: center; color: var(--text-sub); font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>

    <header>
        <div class="logo-area">
            <div class="logo-badge">🛡️</div>
            <div>
                <h1>PHP Universal Security Vaccine Fleet Console</h1>
                <div class="tagline">Enterprise Ambient Runtime Protection & Central Fleet Control Plane</div>
            </div>
        </div>
        <div>
            <span class="status-badge green">● Active Fleet Defense</span>
        </div>
    </header>

    <div class="top-stats">
        <div class="stat-card">
            <div class="stat-label">Inoculated Fleet Nodes</div>
            <div class="stat-val" style="color: var(--accent);">3 / 3</div>
            <div class="stat-desc">100% Fleet Compliance</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Attacks Neutralized</div>
            <div class="stat-val" style="color: var(--danger);">17,761</div>
            <div class="stat-desc">Real-Time In-Band 403 Drops</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Mean Inspection Latency</div>
            <div class="stat-val" style="color: var(--success);">15.81 µs</div>
            <div class="stat-desc">Overhead < 0.02ms (Sub-Microsecond)</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Availability SLA</div>
            <div class="stat-val" style="color: #a855f7;">99.999%</div>
            <div class="stat-desc">Zero Application Disruption</div>
        </div>
    </div>

    <div class="card-table">
        <div class="card-header">
            <div class="card-title">Enrolled Fleet Instances</div>
            <a href="api.php?action=fleet" target="_blank" style="color: var(--accent); font-size: 12px; text-decoration: none;">View Fleet JSON API &rarr;</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Node ID</th>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>PHP Runtime</th>
                    <th>Guardrail Status</th>
                    <th>Policy Mode</th>
                    <th>Attacks Blocked</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>node-aws-us-east-1a-01</code></td>
                    <td>prod-web-01.infra.corp</td>
                    <td>10.0.1.45</td>
                    <td>PHP 8.2.14</td>
                    <td><span class="status-badge green">● Inoculated</span></td>
                    <td><code>ENFORCE</code></td>
                    <td style="font-weight: 700; color: #f87171;">1,420</td>
                </tr>
                <tr>
                    <td><code>node-aws-us-east-1b-02</code></td>
                    <td>prod-web-02.infra.corp</td>
                    <td>10.0.2.18</td>
                    <td>PHP 7.4.33-EOL</td>
                    <td><span class="status-badge amber">● Inoculated (Legacy)</span></td>
                    <td><code>ENFORCE</code></td>
                    <td style="font-weight: 700; color: #f87171;">3,891</td>
                </tr>
                <tr>
                    <td><code>node-onprem-dc1-03</code></td>
                    <td>legacy-billing-app.corp</td>
                    <td>192.168.10.12</td>
                    <td>PHP 5.6.40-EOL</td>
                    <td><span class="status-badge amber">● Inoculated (Legacy)</span></td>
                    <td><code>ENFORCE</code></td>
                    <td style="font-weight: 700; color: #f87171;">12,450</td>
                </tr>
            </tbody>
        </table>
    </div>

    <footer>
        PHP Universal Security Vaccine v1.3.0-ENTERPRISE &bull; Maintained by Ayush Pandey (<a href="https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL" target="_blank" style="color: var(--accent);">GitHub Repository</a>)
    </footer>

</body>
</html>
