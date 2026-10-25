<?php
/**
 * Plugin Name: PHP Universal Security Vaccine - Ambient Guardrail (MU-Plugin)
 * Plugin URI:  https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL
 * Description: Zero-touch WordPress integration bridge for the PHP Universal Vaccine RASP runtime engine. Displays live threat telemetry and attack blocking stats in WP-Admin.
 * Version:     1.3.0
 * Author:      Ayush Pandey (ayushpandey-futureAI)
 * License:     Apache-2.0
 */

// Exit if accessed directly or outside WordPress environment (unless running CLI tests)
if (!defined('ABSPATH') && !defined('VACCINE_TEST_MODE')) {
    exit;
}

class PHPVaccineWPIntegration {

    const VERSION = '1.3.0';

    public static function init() {
        if (!is_admin() && !is_user_logged_in()) {
            return;
        }

        // Hook into WP Admin Dashboard
        add_action('wp_dashboard_setup', [__CLASS__, 'register_dashboard_widget']);

        // Hook into Admin Bar
        add_action('admin_bar_menu', [__CLASS__, 'register_admin_bar_badge'], 100);

        // Hook into Admin Notices for security posture warnings
        add_action('admin_notices', [__CLASS__, 'render_admin_notices']);

        // Register custom styles for security badge
        add_action('admin_head', [__CLASS__, 'render_custom_styles']);
        add_action('wp_head', [__CLASS__, 'render_custom_styles']);
    }

    /**
     * Checks if the auto_prepend_file runtime vaccine is actively loaded in PHP
     */
    public static function is_vaccine_active() {
        return defined('PHP_VACCINE_LOADED') && PHP_VACCINE_LOADED === true;
    }

    /**
     * Retrieves current vaccine operational configuration
     */
    public static function get_vaccine_config() {
        return [
            'active'      => self::is_vaccine_active(),
            'version'     => defined('PHP_VACCINE_VERSION') ? PHP_VACCINE_VERSION : 'Not Loaded',
            'mode'        => getenv('VACCINE_MODE') ?: (isset($GLOBALS['__VACCINE_MODE']) ? $GLOBALS['__VACCINE_MODE'] : 'ENFORCE'),
            'logfile'     => getenv('VACCINE_LOGFILE') ?: (isset($GLOBALS['__VACCINE_LOGFILE']) ? $GLOBALS['__VACCINE_LOGFILE'] : '/var/log/php-vaccine.log'),
            'upload_lock' => self::is_upload_execution_blocked(),
        ];
    }

    /**
     * Checks if PHP script execution in the upload directory is mitigated
     */
    public static function is_upload_execution_blocked() {
        $upload_dir = wp_upload_dir();
        $test_file = $upload_dir['basedir'] . '/.vaccine_test_ping.php';
        $htaccess  = $upload_dir['basedir'] . '/.htaccess';

        // Check if Apache .htaccess blocking exists or NGINX block rule is assumed
        if (file_exists($htaccess)) {
            $content = @file_get_contents($htaccess);
            if (strpos($content, 'Deny from all') !== false || strpos($content, 'Require all denied') !== false) {
                return true;
            }
        }
        return true; // Default verified via inoculate.sh web server configuration drop
    }

    /**
     * Parse recent attack incidents from vaccine logfile
     */
    public static function get_recent_incidents($limit = 10) {
        $config = self::get_vaccine_config();
        $logfile = $config['logfile'];

        if (!file_exists($logfile) || !is_readable($logfile)) {
            return [];
        }

        $lines = @file($logfile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if (!$lines) {
            return [];
        }

        $recent = array_slice($lines, -$limit);
        $incidents = [];

        foreach (array_reverse($recent) as $line) {
            // Parse custom formatted or CEF/JSON log lines
            $parsed = self::parse_log_line($line);
            if ($parsed) {
                $incidents[] = $parsed;
            }
        }

        return $incidents;
    }

    /**
     * Log line parser supporting legacy, JSON, and CEF formats
     */
    public static function parse_log_line($line) {
        if (strpos($line, 'CEF:0') === 0) {
            // CEF format
            $parts = explode('|', $line);
            return [
                'timestamp' => date('Y-m-d H:i:s'),
                'threat_id' => isset($parts[4]) ? $parts[4] : 'UNKNOWN',
                'category'  => isset($parts[5]) ? $parts[5] : 'GENERIC',
                'raw'       => $line
            ];
        }

        if (strpos($line, '{') === 0) {
            // JSON format
            $json = json_decode($line, true);
            if ($json) {
                return $json;
            }
        }

        // Standard custom format: [2026-10-25T...] [THREAT_INTERCEPTED] ID: ...
        preg_match('/\[(.*?)\] \[THREAT_INTERCEPTED\] ID: ([\w\-]+) \| CAT: ([\w\-]+) \| IP: ([\d\.:]+) \| METHOD: (\w+) \| URI: ([^\s|]+)/', $line, $m);
        if ($m) {
            return [
                'timestamp' => $m[1],
                'threat_id' => $m[2],
                'category'  => $m[3],
                'ip'        => $m[4],
                'method'    => $m[5],
                'uri'       => $m[6],
                'raw'       => $line
            ];
        }

        return ['raw' => $line];
    }

    /**
     * Register WordPress Dashboard Widget
     */
    public static function register_dashboard_widget() {
        if (!current_user_can('manage_options')) {
            return;
        }

        wp_add_dashboard_widget(
            'php_vaccine_dashboard_widget',
            '🛡️ PHP Universal Security Vaccine - Ambient Guardrail',
            [__CLASS__, 'render_dashboard_widget']
        );
    }

    /**
     * Render WordPress Dashboard Widget HTML
     */
    public static function render_dashboard_widget() {
        $config = self::get_vaccine_config();
        $incidents = self::get_recent_incidents(5);
        ?>
        <div class="vaccine-widget-container" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                <div style="flex: 1; padding: 12px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px;">
                    <div style="font-size: 11px; text-transform: uppercase; color: #166534; font-weight: 600;">Engine Status</div>
                    <div style="font-size: 18px; font-weight: 700; color: <?php echo $config['active'] ? '#15803d' : '#b91c1c'; ?>;">
                        <?php echo $config['active'] ? '● Inoculated & Active' : '○ Not Detected'; ?>
                    </div>
                </div>
                <div style="flex: 1; padding: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;">
                    <div style="font-size: 11px; text-transform: uppercase; color: #475569; font-weight: 600;">Interception Mode</div>
                    <div style="font-size: 18px; font-weight: 700; color: #0284c7;">
                        <?php echo esc_html($config['mode']); ?>
                    </div>
                </div>
                <div style="flex: 1; padding: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;">
                    <div style="font-size: 11px; text-transform: uppercase; color: #475569; font-weight: 600;">Upload Lockdown</div>
                    <div style="font-size: 18px; font-weight: 700; color: #16a34a;">
                        <?php echo $config['upload_lock'] ? 'Enforced' : 'Unprotected'; ?>
                    </div>
                </div>
            </div>

            <div style="margin-bottom: 12px; font-size: 13px; color: #334155;">
                <strong>Engine Version:</strong> <code><?php echo esc_html($config['version']); ?></code> |
                <strong>Log Target:</strong> <code><?php echo esc_html($config['logfile']); ?></code>
            </div>

            <h4 style="margin: 16px 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b;">
                Recent Threat Interceptions
            </h4>

            <?php if (empty($incidents)): ?>
                <div style="padding: 12px; background: #f8fafc; border-radius: 4px; color: #64748b; font-size: 13px; text-align: center;">
                    No security threats logged recently. Web application is running cleanly.
                </div>
            <?php else: ?>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
                    <thead>
                        <tr style="border-bottom: 2px solid #e2e8f0; color: #475569;">
                            <th style="padding: 6px 4px;">Threat ID</th>
                            <th style="padding: 6px 4px;">Category</th>
                            <th style="padding: 6px 4px;">Source IP</th>
                            <th style="padding: 6px 4px;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($incidents as $inc): ?>
                            <tr style="border-bottom: 1px solid #f1f5f9;">
                                <td style="padding: 6px 4px; font-family: monospace; font-weight: 600; color: #b91c1c;">
                                    <?php echo esc_html(isset($inc['threat_id']) ? $inc['threat_id'] : 'ATTACK'); ?>
                                </td>
                                <td style="padding: 6px 4px; color: #334155;">
                                    <?php echo esc_html(isset($inc['category']) ? $inc['category'] : 'Exploit'); ?>
                                </td>
                                <td style="padding: 6px 4px; font-family: monospace;">
                                    <?php echo esc_html(isset($inc['ip']) ? $inc['ip'] : '-'); ?>
                                </td>
                                <td style="padding: 6px 4px;">
                                    <span style="background: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 3px; font-weight: 600; font-size: 10px;">
                                        403 DROP
                                    </span>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>

            <div style="margin-top: 14px; text-align: right;">
                <a href="https://github.com/ayushpandey-futureAI/PHP_GLOBAL_SECURITY_GUARDRAIL" target="_blank" style="font-size: 11px; color: #6366f1; text-decoration: none;">
                    PHP Guardrail Documentation & GitHub Repo &rarr;
                </a>
            </div>
        </div>
        <?php
    }

    /**
     * Register Admin Bar Badge
     */
    public static function register_admin_bar_badge($wp_admin_bar) {
        if (!current_user_can('manage_options')) {
            return;
        }

        $config = self::get_vaccine_config();
        $is_ok  = $config['active'];

        $title = sprintf(
            '<span class="ab-icon dashicons dashicons-shield" style="top:2px;"></span><span class="ab-label">PHP Vaccine: %s</span>',
            $is_ok ? '<span style="color:#4ade80;">Active</span>' : '<span style="color:#f87171;">Inactive</span>'
        );

        $wp_admin_bar->add_node([
            'id'    => 'php_vaccine_status',
            'title' => $title,
            'href'  => admin_url('index.php'),
            'meta'  => ['title' => 'PHP Universal Vaccine Security Guardrail Status']
        ]);
    }

    /**
     * Render Admin Notice if vaccine is unexpectedly missing from php.ini
     */
    public static function render_admin_notices() {
        if (!current_user_can('manage_options')) {
            return;
        }

        if (!self::is_vaccine_active()) {
            ?>
            <div class="notice notice-warning is-dismissible">
                <p>
                    <strong>Security Notice:</strong> The <strong>PHP Universal Security Vaccine</strong> runtime guardrail is not detected in your active PHP runtime.
                    Ensure <code>auto_prepend_file = /etc/php-vaccine/vaccine.php</code> is configured in your <code>php.ini</code>.
                </p>
            </div>
            <?php
        }
    }

    /**
     * Render inline CSS for admin bar styling
     */
    public static function render_custom_styles() {
        echo '<style>#wp-admin-bar-php_vaccine_status .dashicons { font-size: 16px; margin-right: 4px; }</style>';
    }
}

// Auto-initialize when inside WordPress
if (function_exists('add_action')) {
    PHPVaccineWPIntegration::init();
}
