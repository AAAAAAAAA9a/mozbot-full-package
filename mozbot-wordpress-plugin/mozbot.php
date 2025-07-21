<?php
/**
 * Plugin Name: MozBot Chat Widget
 * Plugin URI: https://mozbot.com/wordpress-plugin
 * Description: Add AI-powered chatbot to your WordPress website with MozBot. Easy setup, full customization, and seamless integration.
 * Version: 1.0.0
 * Author: MozBot Team
 * Author URI: https://mozbot.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: mozbot
 * Domain Path: /languages
 * Requires at least: 5.0
 * Tested up to: 6.4
 * Requires PHP: 7.4
 * Network: false
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('MOZBOT_VERSION', '1.0.0');
define('MOZBOT_PLUGIN_URL', plugin_dir_url(__FILE__));
define('MOZBOT_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('MOZBOT_PLUGIN_BASENAME', plugin_basename(__FILE__));

/**
 * Main MozBot Plugin Class
 */
class MozBot_Plugin {
    
    /**
     * Constructor
     */
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'admin_init'));
        add_action('wp_footer', array($this, 'add_widget_to_frontend'));
        add_action('admin_enqueue_scripts', array($this, 'admin_enqueue_scripts'));
        add_action('wp_enqueue_scripts', array($this, 'frontend_enqueue_scripts'));
        
        // Plugin activation/deactivation hooks
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }
    
    /**
     * Initialize plugin
     */
    public function init() {
        load_plugin_textdomain('mozbot', false, dirname(MOZBOT_PLUGIN_BASENAME) . '/languages');
    }
    
    /**
     * Plugin activation
     */
    public function activate() {
        // Set default options
        $default_options = array(
            'enabled' => false,
            'bot_id' => '',
            'api_key' => '',
            'bot_name' => 'MozBot Assistant',
            'welcome_message' => 'Hello! How can I help you today?',
            'primary_color' => '#3B82F6',
            'position' => 'bottom-right',
            'show_on_pages' => array('all'),
            'exclude_pages' => array(),
            'custom_css' => ''
        );
        
        add_option('mozbot_settings', $default_options);
    }
    
    /**
     * Plugin deactivation
     */
    public function deactivate() {
        // Clean up if needed
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_menu_page(
            __('MozBot Settings', 'mozbot'),
            __('MozBot', 'mozbot'),
            'manage_options',
            'mozbot-settings',
            array($this, 'admin_page'),
            'data:image/svg+xml;base64,' . base64_encode('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>'),
            30
        );
        
        add_submenu_page(
            'mozbot-settings',
            __('Widget Settings', 'mozbot'),
            __('Widget Settings', 'mozbot'),
            'manage_options',
            'mozbot-settings',
            array($this, 'admin_page')
        );
        
        add_submenu_page(
            'mozbot-settings',
            __('Analytics', 'mozbot'),
            __('Analytics', 'mozbot'),
            'manage_options',
            'mozbot-analytics',
            array($this, 'analytics_page')
        );
    }
    
    /**
     * Initialize admin settings
     */
    public function admin_init() {
        register_setting('mozbot_settings_group', 'mozbot_settings', array($this, 'sanitize_settings'));
        
        // General Settings Section
        add_settings_section(
            'mozbot_general_section',
            __('General Settings', 'mozbot'),
            array($this, 'general_section_callback'),
            'mozbot-settings'
        );
        
        // Appearance Settings Section
        add_settings_section(
            'mozbot_appearance_section',
            __('Appearance Settings', 'mozbot'),
            array($this, 'appearance_section_callback'),
            'mozbot-settings'
        );
        
        // Display Settings Section
        add_settings_section(
            'mozbot_display_section',
            __('Display Settings', 'mozbot'),
            array($this, 'display_section_callback'),
            'mozbot-settings'
        );
        
        // Add settings fields
        $this->add_settings_fields();
    }
    
    /**
     * Add settings fields
     */
    private function add_settings_fields() {
        // General fields
        add_settings_field('enabled', __('Enable Widget', 'mozbot'), array($this, 'enabled_field'), 'mozbot-settings', 'mozbot_general_section');
        add_settings_field('bot_id', __('Bot ID', 'mozbot'), array($this, 'bot_id_field'), 'mozbot-settings', 'mozbot_general_section');
        add_settings_field('api_key', __('API Key', 'mozbot'), array($this, 'api_key_field'), 'mozbot-settings', 'mozbot_general_section');
        
        // Appearance fields
        add_settings_field('bot_name', __('Bot Name', 'mozbot'), array($this, 'bot_name_field'), 'mozbot-settings', 'mozbot_appearance_section');
        add_settings_field('welcome_message', __('Welcome Message', 'mozbot'), array($this, 'welcome_message_field'), 'mozbot-settings', 'mozbot_appearance_section');
        add_settings_field('primary_color', __('Primary Color', 'mozbot'), array($this, 'primary_color_field'), 'mozbot-settings', 'mozbot_appearance_section');
        add_settings_field('position', __('Widget Position', 'mozbot'), array($this, 'position_field'), 'mozbot-settings', 'mozbot_appearance_section');
        
        // Display fields
        add_settings_field('show_on_pages', __('Show on Pages', 'mozbot'), array($this, 'show_on_pages_field'), 'mozbot-settings', 'mozbot_display_section');
        add_settings_field('custom_css', __('Custom CSS', 'mozbot'), array($this, 'custom_css_field'), 'mozbot-settings', 'mozbot_display_section');
    }
    
    /**
     * Section callbacks
     */
    public function general_section_callback() {
        echo '<p>' . __('Configure your MozBot connection settings.', 'mozbot') . '</p>';
    }
    
    public function appearance_section_callback() {
        echo '<p>' . __('Customize the appearance of your chat widget.', 'mozbot') . '</p>';
    }
    
    public function display_section_callback() {
        echo '<p>' . __('Control where and how the widget is displayed.', 'mozbot') . '</p>';
    }
    
    /**
     * Settings field callbacks
     */
    public function enabled_field() {
        $options = get_option('mozbot_settings');
        $enabled = isset($options['enabled']) ? $options['enabled'] : false;
        echo '<input type="checkbox" name="mozbot_settings[enabled]" value="1" ' . checked(1, $enabled, false) . ' />';
        echo '<label for="mozbot_settings[enabled]">' . __('Enable the MozBot widget on your website', 'mozbot') . '</label>';
    }
    
    public function bot_id_field() {
        $options = get_option('mozbot_settings');
        $bot_id = isset($options['bot_id']) ? $options['bot_id'] : '';
        echo '<input type="text" name="mozbot_settings[bot_id]" value="' . esc_attr($bot_id) . '" class="regular-text" />';
        echo '<p class="description">' . __('Your unique Bot ID from MozBot dashboard', 'mozbot') . '</p>';
    }
    
    public function api_key_field() {
        $options = get_option('mozbot_settings');
        $api_key = isset($options['api_key']) ? $options['api_key'] : '';
        echo '<input type="password" name="mozbot_settings[api_key]" value="' . esc_attr($api_key) . '" class="regular-text" />';
        echo '<p class="description">' . __('Your API key from MozBot dashboard', 'mozbot') . '</p>';
    }
    
    public function bot_name_field() {
        $options = get_option('mozbot_settings');
        $bot_name = isset($options['bot_name']) ? $options['bot_name'] : 'MozBot Assistant';
        echo '<input type="text" name="mozbot_settings[bot_name]" value="' . esc_attr($bot_name) . '" class="regular-text" />';
    }
    
    public function welcome_message_field() {
        $options = get_option('mozbot_settings');
        $welcome_message = isset($options['welcome_message']) ? $options['welcome_message'] : 'Hello! How can I help you today?';
        echo '<textarea name="mozbot_settings[welcome_message]" rows="3" class="large-text">' . esc_textarea($welcome_message) . '</textarea>';
    }
    
    public function primary_color_field() {
        $options = get_option('mozbot_settings');
        $primary_color = isset($options['primary_color']) ? $options['primary_color'] : '#3B82F6';
        echo '<input type="color" name="mozbot_settings[primary_color]" value="' . esc_attr($primary_color) . '" />';
        echo '<p class="description">' . __('Choose the primary color for your chat widget', 'mozbot') . '</p>';
    }
    
    public function position_field() {
        $options = get_option('mozbot_settings');
        $position = isset($options['position']) ? $options['position'] : 'bottom-right';
        $positions = array(
            'bottom-right' => __('Bottom Right', 'mozbot'),
            'bottom-left' => __('Bottom Left', 'mozbot'),
            'top-right' => __('Top Right', 'mozbot'),
            'top-left' => __('Top Left', 'mozbot')
        );
        
        echo '<select name="mozbot_settings[position]">';
        foreach ($positions as $value => $label) {
            echo '<option value="' . esc_attr($value) . '" ' . selected($position, $value, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select>';
    }
    
    public function show_on_pages_field() {
        $options = get_option('mozbot_settings');
        $show_on_pages = isset($options['show_on_pages']) ? $options['show_on_pages'] : array('all');
        
        echo '<label><input type="radio" name="mozbot_settings[show_on_pages][]" value="all" ' . (in_array('all', $show_on_pages) ? 'checked' : '') . ' /> ' . __('All pages', 'mozbot') . '</label><br>';
        echo '<label><input type="radio" name="mozbot_settings[show_on_pages][]" value="home" ' . (in_array('home', $show_on_pages) ? 'checked' : '') . ' /> ' . __('Homepage only', 'mozbot') . '</label><br>';
        echo '<label><input type="radio" name="mozbot_settings[show_on_pages][]" value="specific" ' . (in_array('specific', $show_on_pages) ? 'checked' : '') . ' /> ' . __('Specific pages', 'mozbot') . '</label>';
    }
    
    public function custom_css_field() {
        $options = get_option('mozbot_settings');
        $custom_css = isset($options['custom_css']) ? $options['custom_css'] : '';
        echo '<textarea name="mozbot_settings[custom_css]" rows="10" class="large-text code">' . esc_textarea($custom_css) . '</textarea>';
        echo '<p class="description">' . __('Add custom CSS to style your chat widget', 'mozbot') . '</p>';
    }
    
    /**
     * Sanitize settings
     */
    public function sanitize_settings($input) {
        $sanitized = array();
        
        $sanitized['enabled'] = isset($input['enabled']) ? true : false;
        $sanitized['bot_id'] = sanitize_text_field($input['bot_id']);
        $sanitized['api_key'] = sanitize_text_field($input['api_key']);
        $sanitized['bot_name'] = sanitize_text_field($input['bot_name']);
        $sanitized['welcome_message'] = sanitize_textarea_field($input['welcome_message']);
        $sanitized['primary_color'] = sanitize_hex_color($input['primary_color']);
        $sanitized['position'] = sanitize_text_field($input['position']);
        $sanitized['show_on_pages'] = isset($input['show_on_pages']) ? array_map('sanitize_text_field', $input['show_on_pages']) : array('all');
        $sanitized['custom_css'] = wp_strip_all_tags($input['custom_css']);
        
        return $sanitized;
    }
    
    /**
     * Admin page
     */
    public function admin_page() {
        include MOZBOT_PLUGIN_PATH . 'admin/admin-page.php';
    }
    
    /**
     * Analytics page
     */
    public function analytics_page() {
        include MOZBOT_PLUGIN_PATH . 'admin/analytics-page.php';
    }
    
    /**
     * Enqueue admin scripts
     */
    public function admin_enqueue_scripts($hook) {
        if (strpos($hook, 'mozbot') === false) {
            return;
        }
        
        wp_enqueue_style('mozbot-admin-css', MOZBOT_PLUGIN_URL . 'admin/css/admin.css', array(), MOZBOT_VERSION);
        wp_enqueue_script('mozbot-admin-js', MOZBOT_PLUGIN_URL . 'admin/js/admin.js', array('jquery'), MOZBOT_VERSION, true);
        
        wp_localize_script('mozbot-admin-js', 'mozbot_admin', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('mozbot_admin_nonce')
        ));
    }
    
    /**
     * Enqueue frontend scripts
     */
    public function frontend_enqueue_scripts() {
        $options = get_option('mozbot_settings');
        
        if (!isset($options['enabled']) || !$options['enabled']) {
            return;
        }
        
        // Check if widget should be displayed on current page
        if (!$this->should_display_widget()) {
            return;
        }
        
        wp_enqueue_script('mozbot-widget-js', MOZBOT_PLUGIN_URL . 'assets/js/widget.js', array(), MOZBOT_VERSION, true);
        
        // Pass settings to JavaScript
        wp_localize_script('mozbot-widget-js', 'mozbot_config', array(
            'bot_id' => $options['bot_id'],
            'bot_name' => $options['bot_name'],
            'welcome_message' => $options['welcome_message'],
            'primary_color' => $options['primary_color'],
            'position' => $options['position'],
            'api_url' => 'https://api.mozbot.com/v1'
        ));
        
        // Add custom CSS if provided
        if (!empty($options['custom_css'])) {
            wp_add_inline_style('mozbot-widget-css', $options['custom_css']);
        }
    }
    
    /**
     * Add widget to frontend
     */
    public function add_widget_to_frontend() {
        $options = get_option('mozbot_settings');
        
        if (!isset($options['enabled']) || !$options['enabled']) {
            return;
        }
        
        if (!$this->should_display_widget()) {
            return;
        }
        
        echo '<div id="mozbot-widget-container"></div>';
    }
    
    /**
     * Check if widget should be displayed on current page
     */
    private function should_display_widget() {
        $options = get_option('mozbot_settings');
        $show_on_pages = isset($options['show_on_pages']) ? $options['show_on_pages'] : array('all');
        
        if (in_array('all', $show_on_pages)) {
            return true;
        }
        
        if (in_array('home', $show_on_pages) && is_front_page()) {
            return true;
        }
        
        // Add more specific page logic here
        
        return false;
    }
}

// Initialize the plugin
new MozBot_Plugin();

