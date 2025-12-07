<?php
// backend/config/config.php

// Environment: development, staging, production
define('ENVIRONMENT', 'development');

// Database Configuration
define('DB_HOST', 'localhost');
define('DB_NAME', 'ahat_database');
define('DB_USER', 'root');
define('DB_PASS', ''); // Set your MySQL password here

// Security Configuration
define('SECRET_KEY', 'your-secret-key-change-in-production');
define('API_KEY_SALT', 'your-api-key-salt-change-this');

// SixSevenDeals API Configuration (if using external API)
define('SIXSEVENDEALS_API_KEY', '');
define('SIXSEVENDEALS_API_URL', 'https://sixsevendeals.com/api/v1');

// CORS Configuration
$allowed_origins = [
    'http://localhost:3000',
    'http://localhost:8080',
    'http://localhost:8000'
];

// Rate Limiting
define('RATE_LIMIT_REQUESTS', 100); // Requests per minute
define('RATE_LIMIT_TIME', 60); // Time in seconds

// Development Settings
if (ENVIRONMENT === 'development') {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
    ini_set('log_errors', 1);
    ini_set('error_log', __DIR__ . '/../logs/php-error.log');
    
    // Create logs directory if it doesn't exist
    if (!is_dir(__DIR__ . '/../logs')) {
        mkdir(__DIR__ . '/../logs', 0755, true);
    }
} else {
    error_reporting(0);
    ini_set('display_errors', 0);
}

// Helper function to get configuration
function get_config($key, $default = null) {
    $config = [
        'environment' => ENVIRONMENT,
        'db_host' => DB_HOST,
        'db_name' => DB_NAME,
        'db_user' => DB_USER,
        'db_pass' => DB_PASS,
        'api_base_url' => 'http://localhost:8000',
        'frontend_url' => 'http://localhost:3000',
        'pwa_url' => 'http://localhost:8080'
    ];
    
    return $config[$key] ?? $default;
}
?>