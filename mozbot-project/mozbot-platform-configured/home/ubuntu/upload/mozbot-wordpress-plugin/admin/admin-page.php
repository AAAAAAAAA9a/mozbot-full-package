<?php
// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

$options = get_option('mozbot_settings');
?>

<div class="wrap">
    <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
    
    <div class="mozbot-admin-header">
        <div class="mozbot-logo">
            <h2><?php _e('MozBot Chat Widget', 'mozbot'); ?></h2>
            <p><?php _e('Add AI-powered chatbot to your WordPress website', 'mozbot'); ?></p>
        </div>
        <div class="mozbot-status">
            <?php if (isset($options['enabled']) && $options['enabled']): ?>
                <span class="status-badge status-active"><?php _e('Active', 'mozbot'); ?></span>
            <?php else: ?>
                <span class="status-badge status-inactive"><?php _e('Inactive', 'mozbot'); ?></span>
            <?php endif; ?>
        </div>
    </div>

    <?php if (isset($_GET['settings-updated'])): ?>
        <div class="notice notice-success is-dismissible">
            <p><?php _e('Settings saved successfully!', 'mozbot'); ?></p>
        </div>
    <?php endif; ?>

    <div class="mozbot-admin-content">
        <div class="mozbot-main-content">
            <form method="post" action="options.php">
                <?php
                settings_fields('mozbot_settings_group');
                do_settings_sections('mozbot-settings');
                ?>
                
                <div class="mozbot-settings-section">
                    <h3><?php _e('Quick Setup', 'mozbot'); ?></h3>
                    <div class="mozbot-quick-setup">
                        <div class="setup-step">
                            <div class="step-number">1</div>
                            <div class="step-content">
                                <h4><?php _e('Get Your Bot ID', 'mozbot'); ?></h4>
                                <p><?php _e('Sign up at MozBot.com and create your first chatbot to get your Bot ID.', 'mozbot'); ?></p>
                                <a href="https://mozbot.com/signup" target="_blank" class="button button-secondary"><?php _e('Create Account', 'mozbot'); ?></a>
                            </div>
                        </div>
                        
                        <div class="setup-step">
                            <div class="step-number">2</div>
                            <div class="step-content">
                                <h4><?php _e('Configure Settings', 'mozbot'); ?></h4>
                                <p><?php _e('Enter your Bot ID and customize the appearance below.', 'mozbot'); ?></p>
                            </div>
                        </div>
                        
                        <div class="setup-step">
                            <div class="step-number">3</div>
                            <div class="step-content">
                                <h4><?php _e('Enable Widget', 'mozbot'); ?></h4>
                                <p><?php _e('Check the "Enable Widget" option and save settings.', 'mozbot'); ?></p>
                            </div>
                        </div>
                    </div>
                </div>

                <table class="form-table" role="presentation">
                    <tbody>
                        <!-- General Settings -->
                        <tr>
                            <th scope="row" colspan="2">
                                <h3 class="section-title"><?php _e('General Settings', 'mozbot'); ?></h3>
                            </th>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_enabled"><?php _e('Enable Widget', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->enabled_field(); ?>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_bot_id"><?php _e('Bot ID', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->bot_id_field(); ?>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_api_key"><?php _e('API Key', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->api_key_field(); ?>
                            </td>
                        </tr>

                        <!-- Appearance Settings -->
                        <tr>
                            <th scope="row" colspan="2">
                                <h3 class="section-title"><?php _e('Appearance Settings', 'mozbot'); ?></h3>
                            </th>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_bot_name"><?php _e('Bot Name', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->bot_name_field(); ?>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_welcome_message"><?php _e('Welcome Message', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->welcome_message_field(); ?>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_primary_color"><?php _e('Primary Color', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->primary_color_field(); ?>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_position"><?php _e('Widget Position', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->position_field(); ?>
                            </td>
                        </tr>

                        <!-- Display Settings -->
                        <tr>
                            <th scope="row" colspan="2">
                                <h3 class="section-title"><?php _e('Display Settings', 'mozbot'); ?></h3>
                            </th>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_show_on_pages"><?php _e('Show on Pages', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->show_on_pages_field(); ?>
                            </td>
                        </tr>
                        
                        <tr>
                            <th scope="row">
                                <label for="mozbot_custom_css"><?php _e('Custom CSS', 'mozbot'); ?></label>
                            </th>
                            <td>
                                <?php $this->custom_css_field(); ?>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <?php submit_button(__('Save Settings', 'mozbot'), 'primary', 'submit', true, array('id' => 'mozbot-save-settings')); ?>
            </form>
        </div>

        <div class="mozbot-sidebar">
            <div class="mozbot-widget-preview">
                <h3><?php _e('Widget Preview', 'mozbot'); ?></h3>
                <div class="preview-container">
                    <div class="preview-widget" id="mozbot-preview">
                        <div class="widget-header" style="background-color: <?php echo esc_attr($options['primary_color'] ?? '#3B82F6'); ?>">
                            <div class="bot-avatar">🤖</div>
                            <div class="bot-info">
                                <div class="bot-name"><?php echo esc_html($options['bot_name'] ?? 'MozBot Assistant'); ?></div>
                                <div class="bot-status"><?php _e('Online now', 'mozbot'); ?></div>
                            </div>
                        </div>
                        <div class="widget-body">
                            <div class="message bot-message">
                                <div class="message-avatar">🤖</div>
                                <div class="message-content"><?php echo esc_html($options['welcome_message'] ?? 'Hello! How can I help you today?'); ?></div>
                            </div>
                        </div>
                        <div class="widget-footer">
                            <input type="text" placeholder="<?php _e('Type your message...', 'mozbot'); ?>" disabled>
                            <button style="background-color: <?php echo esc_attr($options['primary_color'] ?? '#3B82F6'); ?>">→</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mozbot-help-box">
                <h3><?php _e('Need Help?', 'mozbot'); ?></h3>
                <ul>
                    <li><a href="https://docs.mozbot.com" target="_blank"><?php _e('Documentation', 'mozbot'); ?></a></li>
                    <li><a href="https://mozbot.com/support" target="_blank"><?php _e('Support Center', 'mozbot'); ?></a></li>
                    <li><a href="https://mozbot.com/contact" target="_blank"><?php _e('Contact Us', 'mozbot'); ?></a></li>
                </ul>
            </div>

            <div class="mozbot-features-box">
                <h3><?php _e('Features', 'mozbot'); ?></h3>
                <ul>
                    <li>✅ <?php _e('AI-Powered Responses', 'mozbot'); ?></li>
                    <li>✅ <?php _e('Multi-Channel Support', 'mozbot'); ?></li>
                    <li>✅ <?php _e('Automation Workflows', 'mozbot'); ?></li>
                    <li>✅ <?php _e('Analytics & Reporting', 'mozbot'); ?></li>
                    <li>✅ <?php _e('Custom Branding', 'mozbot'); ?></li>
                    <li>✅ <?php _e('24/7 Support', 'mozbot'); ?></li>
                </ul>
            </div>
        </div>
    </div>
</div>

