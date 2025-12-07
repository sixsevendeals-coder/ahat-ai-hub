<?php
// backend/api/products.php

// Set headers for JSON response and CORS
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key');

// Load configuration
require_once __DIR__ . '/../config/config.php';

// Enable error reporting for development
if (ENVIRONMENT === 'development') {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
}

// Handle preflight CORS requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Get request method
$method = $_SERVER['REQUEST_METHOD'];

// Main router
$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$request_path = str_replace('/api', '', $request_uri);

try {
    // Route based on request method and path
    switch (true) {
        case $method === 'GET' && preg_match('/^\/products(\/|$)/', $request_path):
            handleGetProducts();
            break;
            
        case $method === 'GET' && preg_match('/^\/products\/([a-zA-Z0-9_-]+)$/', $request_path, $matches):
            handleGetProductById($matches[1]);
            break;
            
        case $method === 'POST' && $request_path === '/products/sync':
            handleSyncProducts();
            break;
            
        case $method === 'POST' && $request_path === '/products/import':
            handleImportProducts();
            break;
            
        case $method === 'GET' && $request_path === '/products/categories':
            handleGetCategories();
            break;
            
        case $method === 'GET' && $request_path === '/products/stats':
            handleGetStats();
            break;
            
        default:
            http_response_code(404);
            echo json_encode([
                'success' => false,
                'error' => 'Endpoint not found',
                'path' => $request_path
            ]);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Internal server error',
        'message' => ENVIRONMENT === 'development' ? $e->getMessage() : 'An error occurred'
    ]);
}

/**
 * Handle GET /api/products
 */
function handleGetProducts() {
    // Get query parameters
    $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 20;
    $page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
    $category = $_GET['category'] ?? null;
    $search = $_GET['search'] ?? null;
    $sort = $_GET['sort'] ?? 'newest';
    $min_price = isset($_GET['min_price']) ? (float)$_GET['min_price'] : null;
    $max_price = isset($_GET['max_price']) ? (float)$_GET['max_price'] : null;
    
    // Validate parameters
    $limit = min(max($limit, 1), 100); // Limit between 1 and 100
    $page = max($page, 1);
    
    // For development: return mock data
    if (ENVIRONMENT === 'development') {
        $products = generateMockProducts($limit, $page, $category, $search, $sort);
        
        echo json_encode([
            'success' => true,
            'data' => $products,
            'pagination' => [
                'page' => $page,
                'limit' => $limit,
                'total' => count($products),
                'pages' => ceil(count($products) / $limit),
                'has_more' => count($products) === $limit
            ],
            'meta' => [
                'source' => 'mock',
                'timestamp' => time(),
                'environment' => ENVIRONMENT
            ]
        ]);
        return;
    }
    
    // Production: Connect to real database
    try {
        $db = getDatabaseConnection();
        $products = fetchProductsFromDatabase($db, [
            'limit' => $limit,
            'page' => $page,
            'category' => $category,
            'search' => $search,
            'sort' => $sort,
            'min_price' => $min_price,
            'max_price' => $max_price
        ]);
        
        $total = countProducts($db, [
            'category' => $category,
            'search' => $search,
            'min_price' => $min_price,
            'max_price' => $max_price
        ]);
        
        echo json_encode([
            'success' => true,
            'data' => $products,
            'pagination' => [
                'page' => $page,
                'limit' => $limit,
                'total' => $total,
                'pages' => ceil($total / $limit),
                'has_more' => ($page * $limit) < $total
            ],
            'meta' => [
                'source' => 'database',
                'timestamp' => time(),
                'environment' => ENVIRONMENT
            ]
        ]);
        
    } catch (Exception $e) {
        throw new Exception("Database error: " . $e->getMessage());
    }
}

/**
 * Handle GET /api/products/{id}
 */
function handleGetProductById($id) {
    // For development: return mock product
    if (ENVIRONMENT === 'development') {
        $product = generateMockProduct($id);
        
        if ($product) {
            echo json_encode([
                'success' => true,
                'data' => $product
            ]);
        } else {
            http_response_code(404);
            echo json_encode([
                'success' => false,
                'error' => 'Product not found'
            ]);
        }
        return;
    }
    
    // Production: Fetch from database
    try {
        $db = getDatabaseConnection();
        $product = fetchProductById($db, $id);
        
        if ($product) {
            echo json_encode([
                'success' => true,
                'data' => $product
            ]);
        } else {
            http_response_code(404);
            echo json_encode([
                'success' => false,
                'error' => 'Product not found'
            ]);
        }
    } catch (Exception $e) {
        throw new Exception("Database error: " . $e->getMessage());
    }
}

/**
 * Handle POST /api/products/sync - Sync with SixSevenDeals
 */
function handleSyncProducts() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    // Check if we have a valid API key for SixSevenDeals
    $apiKey = $input['api_key'] ?? SIXSEVENDEALS_API_KEY;
    
    if (empty($apiKey) && ENVIRONMENT !== 'development') {
        http_response_code(401);
        echo json_encode([
            'success' => false,
            'error' => 'API key required for sync'
        ]);
        return;
    }
    
    // For development: simulate sync
    if (ENVIRONMENT === 'development') {
        $count = $input['count'] ?? 10;
        $newProducts = generateMockProducts($count, 1, null, null, 'newest');
        
        echo json_encode([
            'success' => true,
            'data' => [
                'synced' => $count,
                'new_products' => $newProducts,
                'updated' => 0,
                'skipped' => 0,
                'failed' => 0
            ],
            'message' => 'Development mode: Mock sync completed'
        ]);
        return;
    }
    
    // Production: Sync with SixSevenDeals API
    try {
        $syncResult = syncWithSixSevenDeals($apiKey, $input);
        echo json_encode([
            'success' => true,
            'data' => $syncResult
        ]);
    } catch (Exception $e) {
        throw new Exception("Sync failed: " . $e->getMessage());
    }
}

/**
 * Handle POST /api/products/import - Import products to Ahat database
 */
function handleImportProducts() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['products']) || !is_array($input['products'])) {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'error' => 'Products array is required'
        ]);
        return;
    }
    
    // For development: simulate import
    if (ENVIRONMENT === 'development') {
        $imported = [];
        $skipped = [];
        
        foreach ($input['products'] as $product) {
            if (!isset($product['id'])) {
                $skipped[] = ['product' => $product, 'reason' => 'Missing ID'];
                continue;
            }
            
            $imported[] = [
                'id' => $product['id'],
                'status' => 'imported',
                'ahat_id' => 'AHAT-' . uniqid()
            ];
        }
        
        echo json_encode([
            'success' => true,
            'data' => [
                'total' => count($input['products']),
                'imported' => count($imported),
                'skipped' => count($skipped),
                'details' => [
                    'imported' => $imported,
                    'skipped' => $skipped
                ]
            ]
        ]);
        return;
    }
    
    // Production: Import to database
    try {
        $db = getDatabaseConnection();
        $importResult = importProductsToDatabase($db, $input['products']);
        echo json_encode([
            'success' => true,
            'data' => $importResult
        ]);
    } catch (Exception $e) {
        throw new Exception("Import failed: " . $e->getMessage());
    }
}

/**
 * Handle GET /api/products/categories
 */
function handleGetCategories() {
    // For development: return mock categories
    if (ENVIRONMENT === 'development') {
        $categories = [
            ['id' => 1, 'name' => 'Electronics', 'count' => 45, 'icon' => '💻'],
            ['id' => 2, 'name' => 'Home & Kitchen', 'count' => 32, 'icon' => '🏠'],
            ['id' => 3, 'name' => 'Fashion', 'count' => 28, 'icon' => '👕'],
            ['id' => 4, 'name' => 'Beauty', 'count' => 21, 'icon' => '💄'],
            ['id' => 5, 'name' => 'Books', 'count' => 18, 'icon' => '📚'],
            ['id' => 6, 'name' => 'Sports', 'count' => 15, 'icon' => '⚽'],
            ['id' => 7, 'name' => 'Toys & Games', 'count' => 12, 'icon' => '🎮'],
            ['id' => 8, 'name' => 'Automotive', 'count' => 8, 'icon' => '🚗']
        ];
        
        echo json_encode([
            'success' => true,
            'data' => $categories,
            'total' => count($categories)
        ]);
        return;
    }
    
    // Production: Fetch categories from database
    try {
        $db = getDatabaseConnection();
        $categories = fetchCategories($db);
        echo json_encode([
            'success' => true,
            'data' => $categories,
            'total' => count($categories)
        ]);
    } catch (Exception $e) {
        throw new Exception("Failed to fetch categories: " . $e->getMessage());
    }
}

/**
 * Handle GET /api/products/stats
 */
function handleGetStats() {
    // For development: return mock stats
    if (ENVIRONMENT === 'development') {
        $stats = [
            'total_products' => 179,
            'active_products' => 156,
            'categories_count' => 8,
            'average_price' => 89.99,
            'average_discount' => 32.5,
            'trending_score_avg' => 72.3,
            'last_sync' => date('Y-m-d H:i:s', time() - 3600), // 1 hour ago
            'top_categories' => [
                ['name' => 'Electronics', 'count' => 45],
                ['name' => 'Home & Kitchen', 'count' => 32],
                ['name' => 'Fashion', 'count' => 28]
            ],
            'price_ranges' => [
                ['range' => '$0-50', 'count' => 42],
                ['range' => '$50-100', 'count' => 67],
                ['range' => '$100-200', 'count' => 45],
                ['range' => '$200+', 'count' => 25]
            ]
        ];
        
        echo json_encode([
            'success' => true,
            'data' => $stats
        ]);
        return;
    }
    
    // Production: Calculate stats from database
    try {
        $db = getDatabaseConnection();
        $stats = calculateProductStats($db);
        echo json_encode([
            'success' => true,
            'data' => $stats
        ]);
    } catch (Exception $e) {
        throw new Exception("Failed to calculate stats: " . $e->getMessage());
    }
}

/**
 * Generate mock products for development
 */
function generateMockProducts($limit, $page, $category = null, $search = null, $sort = 'newest') {
    $categories = ['Electronics', 'Home & Kitchen', 'Fashion', 'Beauty', 'Books', 'Sports', 'Toys & Games', 'Automotive'];
    $brands = ['Sony', 'Apple', 'Samsung', 'Amazon', 'Nike', 'Adidas', 'Lego', 'Dyson', 'Philips', 'Logitech'];
    $products = [];
    
    $offset = ($page - 1) * $limit;
    
    for ($i = 0; $i < $limit; $i++) {
        $productId = $offset + $i + 1;
        $categoryName = $category ?: $categories[array_rand($categories)];
        $brand = $brands[array_rand($brands)];
        
        // Apply search filter
        if ($search && stripos($brand . ' ' . $categoryName, $search) === false) {
            continue;
        }
        
        $price = rand(1999, 29999) / 100; // $19.99 to $299.99
        $discount = rand(10, 60);
        $discountedPrice = round($price * (100 - $discount) / 100, 2);
        $rating = round(rand(30, 50) / 10, 1); // 3.0 to 5.0
        
        $products[] = [
            'id' => 'AHAT-MOCK-' . $productId,
            'source_id' => 'SSD-' . $productId,
            'asin' => 'B0' . str_pad(rand(1000000, 9999999), 9, '0'),
            'title' => $brand . ' ' . $categoryName . ' Product ' . $productId,
            'description' => 'Premium ' . $categoryName . ' product from ' . $brand . ' with advanced features and excellent performance.',
            'price' => [
                'original' => $price,
                'discounted' => $discountedPrice,
                'currency' => 'AUD',
                'discount_percentage' => $discount,
                'savings' => round($price - $discountedPrice, 2)
            ],
            'category' => $categoryName,
            'subcategory' => 'Premium ' . $categoryName,
            'brand' => $brand,
            'rating' => $rating,
            'review_count' => rand(5, 2500),
            'image' => 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
            'affiliate_link' => 'https://amazon.com.au/dp/B0' . str_pad(rand(1000000, 9999999), 9, '0') . '?tag=ahat-20',
            'ai_optimization' => [
                'tags' => [$categoryName, $brand, 'Amazon AU', 'Affiliate'],
                'video_angles' => [
                    'Unboxing and first impressions',
                    'Comparison with similar products',
                    'Long-term review after 30 days'
                ],
                'hashtags' => ['#' . str_replace(' ', '', $categoryName), '#' . $brand, '#AmazonFinds', '#AffiliateMarketing'],
                'thumbnail_ideas' => ['Product with price tag', 'Product in use', 'Comparison shot']
            ],
            'trending_score' => rand(50, 95),
            'deal_score' => rand(60, 95),
            'status' => 'active',
            'created_at' => date('Y-m-d H:i:s', time() - rand(0, 30 * 24 * 3600)),
            'updated_at' => date('Y-m-d H:i:s', time() - rand(0, 7 * 24 * 3600))
        ];
    }
    
    // Apply sorting
    usort($products, function($a, $b) use ($sort) {
        switch ($sort) {
            case 'price_asc':
                return $a['price']['discounted'] <=> $b['price']['discounted'];
            case 'price_desc':
                return $b['price']['discounted'] <=> $a['price']['discounted'];
            case 'rating':
                return $b['rating'] <=> $a['rating'];
            case 'discount':
                return $b['price']['discount_percentage'] <=> $a['price']['discount_percentage'];
            default: // 'newest'
                return strtotime($b['created_at']) <=> strtotime($a['created_at']);
        }
    });
    
    return $products;
}

/**
 * Generate a single mock product
 */
function generateMockProduct($id) {
    $categories = ['Electronics', 'Home & Kitchen', 'Fashion', 'Beauty', 'Books', 'Sports'];
    $brands = ['Sony', 'Apple', 'Samsung', 'Amazon', 'Nike', 'Adidas'];
    
    $category = $categories[array_rand($categories)];
    $brand = $brands[array_rand($brands)];
    $price = rand(1999, 19999) / 100;
    $discount = rand(10, 50);
    $discountedPrice = round($price * (100 - $discount) / 100, 2);
    
    return [
        'id' => $id,
        'source_id' => 'SSD-' . rand(1000, 9999),
        'asin' => 'B0' . str_pad(rand(1000000, 9999999), 9, '0'),
        'title' => $brand . ' ' . $category . ' - Premium Edition',
        'description' => 'This is a premium ' . $category . ' from ' . $brand . ' with exceptional quality and performance. Perfect for everyday use.',
        'price' => [
            'original' => $price,
            'discounted' => $discountedPrice,
            'currency' => 'AUD',
            'discount_percentage' => $discount,
            'savings' => round($price - $discountedPrice, 2)
        ],
        'category' => $category,
        'brand' => $brand,
        'rating' => round(rand(35, 50) / 10, 1),
        'review_count' => rand(10, 5000),
        'image' => 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
        'affiliate_link' => 'https://amazon.com.au/dp/B0' . str_pad(rand(1000000, 9999999), 9, '0') . '?tag=ahat-20',
        'features' => [
            'High-quality materials',
            'Easy to use',
            'Long battery life',
            'Compact design'
        ],
        'ai_optimization' => [
            'tags' => [$category, $brand, 'Amazon', 'Deal'],
            'video_angles' => [
                'Unboxing experience',
                'Feature showcase',
                'Real-world usage'
            ],
            'hashtags' => ['#' . str_replace(' ', '', $category), '#' . $brand, '#Unboxing', '#Review'],
            'thumbnail_ideas' => ['Product with glowing effect', 'Before/after comparison', 'Size comparison']
        ],
        'trending_score' => rand(60, 90),
        'deal_score' => rand(65, 95),
        'status' => 'active',
        'created_at' => date('Y-m-d H:i:s', time() - rand(1, 30) * 24 * 3600),
        'updated_at' => date('Y-m-d H:i:s', time() - rand(0, 7) * 24 * 3600)
    ];
}

/**
 * Get database connection
 */
function getDatabaseConnection() {
    $host = DB_HOST;
    $dbname = DB_NAME;
    $username = DB_USER;
    $password = DB_PASS;
    
    try {
        $dsn = "mysql:host=$host;dbname=$dbname;charset=utf8mb4";
        $pdo = new PDO($dsn, $username, $password, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false
        ]);
        return $pdo;
    } catch (PDOException $e) {
        throw new Exception("Database connection failed: " . $e->getMessage());
    }
}

/**
 * These are placeholder functions for database operations.
 * You'll need to implement them based on your actual database schema.
 */

function fetchProductsFromDatabase($db, $params) {
    // TODO: Implement based on your database schema
    // This is a placeholder that returns mock data
    return generateMockProducts(
        $params['limit'], 
        1, 
        $params['category'], 
        $params['search'], 
        $params['sort']
    );
}

function countProducts($db, $filters) {
    // TODO: Implement counting based on filters
    return 100; // Placeholder
}

function fetchProductById($db, $id) {
    // TODO: Implement fetching a single product by ID
    return generateMockProduct($id);
}

function syncWithSixSevenDeals($apiKey, $params) {
    // TODO: Implement actual sync with SixSevenDeals API
    return [
        'synced' => 25,
        'new_products' => 10,
        'updated' => 15,
        'skipped' => 0,
        'failed' => 0
    ];
}

function importProductsToDatabase($db, $products) {
    // TODO: Implement database import logic
    return [
        'total' => count($products),
        'imported' => count($products),
        'skipped' => 0,
        'failed' => 0
    ];
}

function fetchCategories($db) {
    // TODO: Implement category fetching from database
    return [
        ['id' => 1, 'name' => 'Electronics', 'count' => 25],
        ['id' => 2, 'name' => 'Home & Kitchen', 'count' => 18],
        ['id' => 3, 'name' => 'Fashion', 'count' => 12]
    ];
}

function calculateProductStats($db) {
    // TODO: Implement stats calculation from database
    return [
        'total_products' => 150,
        'active_products' => 135,
        'categories_count' => 6,
        'average_price' => 124.75,
        'average_discount' => 28.3
    ];
}
?>