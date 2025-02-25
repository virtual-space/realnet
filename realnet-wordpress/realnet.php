<?php
/**
 * Plugin Name: Realnet Integration
 * Plugin URI: https://github.com/realnet/wordpress-plugin
 * Description: Integrates WordPress with Realnet as the content source
 * Version: 1.0.0
 * Author: Realnet
 * Author URI: https://realnet.local
 * License: GPL v2 or later
 */

if (!defined('ABSPATH')) {
    exit;
}

class RealnetIntegration {
    private $api_url;
    private $api_token;

    public function __construct() {
        $this->api_url = defined('REALNET_API_URL') ? REALNET_API_URL : 'http://localhost:8080';
        $this->api_token = defined('REALNET_API_TOKEN') ? REALNET_API_TOKEN : '';

        // Hook into WordPress
        add_action('init', array($this, 'init'));
        add_action('template_redirect', array($this, 'handle_request'));
        add_filter('template_include', array($this, 'override_template'));
    }

    public function init() {
        // Register REST API endpoints
        add_action('rest_api_init', function() {
            register_rest_route('realnet/v1', '/sync', array(
                'methods' => 'POST',
                'callback' => array($this, 'handle_sync'),
                'permission_callback' => array($this, 'verify_realnet_request')
            ));
        });
    }

    public function verify_realnet_request($request) {
        $auth_header = $request->get_header('X-Realnet-Token');
        return $auth_header === $this->api_token;
    }

    public function handle_sync($request) {
        $params = $request->get_params();
        $type = $params['type'] ?? '';
        $action = $params['action'] ?? '';
        $data = $params['data'] ?? array();

        switch ($type) {
            case 'website':
                return $this->sync_website($action, $data);
            case 'page':
                return $this->sync_page($action, $data);
            case 'post':
                return $this->sync_post($action, $data);
            default:
                return new WP_Error('invalid_type', 'Invalid content type', array('status' => 400));
        }
    }

    private function sync_website($action, $data) {
        switch ($action) {
            case 'create':
            case 'update':
                $site_id = $data['id'] ?? 0;
                $domain = $data['domain'] ?? '';
                $title = $data['title'] ?? '';
                $theme = $data['theme'] ?? '';

                if (!$domain || !$title) {
                    return new WP_Error('missing_data', 'Missing required data', array('status' => 400));
                }

                // Update site settings
                update_blog_option($site_id, 'blogname', $title);
                if ($theme && wp_get_theme($theme)->exists()) {
                    switch_theme($theme);
                }

                return array(
                    'success' => true,
                    'site_id' => $site_id
                );

            case 'delete':
                $site_id = $data['id'] ?? 0;
                if (!$site_id) {
                    return new WP_Error('missing_id', 'Missing site ID', array('status' => 400));
                }

                if (is_main_site($site_id)) {
                    return new WP_Error('cannot_delete_main', 'Cannot delete main site', array('status' => 400));
                }

                wpmu_delete_blog($site_id, true);
                return array('success' => true);

            default:
                return new WP_Error('invalid_action', 'Invalid action', array('status' => 400));
        }
    }

    private function sync_page($action, $data) {
        switch ($action) {
            case 'create':
            case 'update':
                $page_data = array(
                    'post_type' => 'page',
                    'post_title' => $data['title'],
                    'post_content' => $data['content'],
                    'post_status' => $data['status'],
                    'post_name' => $data['path'],
                    'meta_input' => $data['meta'] ?? array()
                );

                if ($action === 'update' && !empty($data['id'])) {
                    $page_data['ID'] = $data['id'];
                    $post_id = wp_update_post($page_data);
                } else {
                    $post_id = wp_insert_post($page_data);
                }

                if (is_wp_error($post_id)) {
                    return $post_id;
                }

                return array(
                    'success' => true,
                    'page_id' => $post_id
                );

            case 'delete':
                $page_id = $data['id'] ?? 0;
                if (!$page_id) {
                    return new WP_Error('missing_id', 'Missing page ID', array('status' => 400));
                }

                $result = wp_delete_post($page_id, true);
                return array('success' => (bool)$result);

            default:
                return new WP_Error('invalid_action', 'Invalid action', array('status' => 400));
        }
    }

    private function sync_post($action, $data) {
        switch ($action) {
            case 'create':
            case 'update':
                $post_data = array(
                    'post_type' => 'post',
                    'post_title' => $data['title'],
                    'post_content' => $data['content'],
                    'post_status' => $data['status'],
                    'post_name' => $data['path'],
                    'post_excerpt' => $data['excerpt'] ?? '',
                    'meta_input' => $data['meta'] ?? array()
                );

                if (!empty($data['author'])) {
                    $post_data['post_author'] = $data['author'];
                }

                if ($action === 'update' && !empty($data['id'])) {
                    $post_data['ID'] = $data['id'];
                    $post_id = wp_update_post($post_data);
                } else {
                    $post_id = wp_insert_post($post_data);
                }

                if (is_wp_error($post_id)) {
                    return $post_id;
                }

                // Set categories and tags
                if (!empty($data['categories'])) {
                    wp_set_post_categories($post_id, $data['categories']);
                }
                if (!empty($data['tags'])) {
                    wp_set_post_tags($post_id, $data['tags']);
                }

                return array(
                    'success' => true,
                    'post_id' => $post_id
                );

            case 'delete':
                $post_id = $data['id'] ?? 0;
                if (!$post_id) {
                    return new WP_Error('missing_id', 'Missing post ID', array('status' => 400));
                }

                $result = wp_delete_post($post_id, true);
                return array('success' => (bool)$result);

            default:
                return new WP_Error('invalid_action', 'Invalid action', array('status' => 400));
        }
    }

    public function handle_request() {
        global $wp;
        $current_url = home_url($wp->request);
        
        // Get content from Realnet
        $response = wp_remote_get($this->api_url . '/api/content', array(
            'headers' => array(
                'X-Website-Domain' => $_SERVER['HTTP_HOST'],
                'X-Content-Path' => $wp->request
            )
        ));

        if (is_wp_error($response)) {
            return;
        }

        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        if (!empty($data)) {
            // Store the Realnet content for template use
            $GLOBALS['realnet_content'] = $data;
        }
    }

    public function override_template($template) {
        if (!empty($GLOBALS['realnet_content'])) {
            $content_type = $GLOBALS['realnet_content']['type'] ?? '';
            $custom_template = '';

            switch ($content_type) {
                case 'page':
                    $custom_template = locate_template('realnet-page.php');
                    break;
                case 'post':
                    $custom_template = locate_template('realnet-post.php');
                    break;
            }

            if ($custom_template) {
                return $custom_template;
            }

            // Fall back to default templates in plugin
            $template_file = plugin_dir_path(__FILE__) . 'templates/realnet-' . $content_type . '.php';
            if (file_exists($template_file)) {
                return $template_file;
            }
        }

        return $template;
    }
}

// Initialize the plugin
new RealnetIntegration();
