<?php
// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

$options = get_option('mozbot_settings');
?>

<div class="wrap">
    <h1><?php _e('MozBot Analytics', 'mozbot'); ?></h1>
    
    <div class="mozbot-analytics-header">
        <div class="analytics-summary">
            <div class="summary-card">
                <h3><?php _e('Total Conversations', 'mozbot'); ?></h3>
                <div class="summary-number">1,247</div>
                <div class="summary-change positive">+12% <?php _e('from last week', 'mozbot'); ?></div>
            </div>
            
            <div class="summary-card">
                <h3><?php _e('Active Users', 'mozbot'); ?></h3>
                <div class="summary-number">892</div>
                <div class="summary-change positive">+8% <?php _e('from last week', 'mozbot'); ?></div>
            </div>
            
            <div class="summary-card">
                <h3><?php _e('Response Rate', 'mozbot'); ?></h3>
                <div class="summary-number">94.2%</div>
                <div class="summary-change positive">+2.1% <?php _e('improvement', 'mozbot'); ?></div>
            </div>
            
            <div class="summary-card">
                <h3><?php _e('Avg Response Time', 'mozbot'); ?></h3>
                <div class="summary-number">2.3s</div>
                <div class="summary-change negative">+0.2s <?php _e('from last week', 'mozbot'); ?></div>
            </div>
        </div>
    </div>

    <div class="mozbot-analytics-content">
        <div class="analytics-main">
            <div class="chart-container">
                <h3><?php _e('Conversation Trends', 'mozbot'); ?></h3>
                <div class="chart-placeholder">
                    <p><?php _e('Chart will be displayed here when connected to MozBot API', 'mozbot'); ?></p>
                </div>
            </div>
            
            <div class="analytics-grid">
                <div class="analytics-card">
                    <h4><?php _e('Top Pages', 'mozbot'); ?></h4>
                    <div class="analytics-list">
                        <div class="list-item">
                            <span class="item-name"><?php _e('Homepage', 'mozbot'); ?></span>
                            <span class="item-value">45%</span>
                        </div>
                        <div class="list-item">
                            <span class="item-name"><?php _e('Contact Page', 'mozbot'); ?></span>
                            <span class="item-value">23%</span>
                        </div>
                        <div class="list-item">
                            <span class="item-name"><?php _e('Product Pages', 'mozbot'); ?></span>
                            <span class="item-value">18%</span>
                        </div>
                        <div class="list-item">
                            <span class="item-name"><?php _e('About Page', 'mozbot'); ?></span>
                            <span class="item-value">14%</span>
                        </div>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <h4><?php _e('Common Questions', 'mozbot'); ?></h4>
                    <div class="analytics-list">
                        <div class="list-item">
                            <span class="item-name"><?php _e('What are your hours?', 'mozbot'); ?></span>
                            <span class="item-value">28</span>
                        </div>
                        <div class="list-item">
                            <span class="item-name"><?php _e('How can I contact support?', 'mozbot'); ?></span>
                            <span class="item-value">22</span>
                        </div>
                        <div class="list-item">
                            <span class="item-name"><?php _e('What are your prices?', 'mozbot'); ?></span>
                            <span class="item-value">19</span>
                        </div>
                        <div class="list-item">
                            <span class="item-name"><?php _e('Do you offer refunds?', 'mozbot'); ?></span>
                            <span class="item-value">15</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="analytics-sidebar">
            <div class="analytics-widget">
                <h4><?php _e('Recent Activity', 'mozbot'); ?></h4>
                <div class="activity-list">
                    <div class="activity-item">
                        <div class="activity-time">2 min ago</div>
                        <div class="activity-text"><?php _e('New conversation started', 'mozbot'); ?></div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-time">5 min ago</div>
                        <div class="activity-text"><?php _e('Support ticket resolved', 'mozbot'); ?></div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-time">12 min ago</div>
                        <div class="activity-text"><?php _e('Automation triggered', 'mozbot'); ?></div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-time">18 min ago</div>
                        <div class="activity-text"><?php _e('New user registered', 'mozbot'); ?></div>
                    </div>
                </div>
            </div>
            
            <div class="analytics-widget">
                <h4><?php _e('Export Data', 'mozbot'); ?></h4>
                <p><?php _e('Download your analytics data for further analysis.', 'mozbot'); ?></p>
                <button class="button button-secondary" disabled><?php _e('Export CSV', 'mozbot'); ?></button>
                <button class="button button-secondary" disabled><?php _e('Export PDF', 'mozbot'); ?></button>
                <p class="description"><?php _e('Available with Pro plan', 'mozbot'); ?></p>
            </div>
        </div>
    </div>
    
    <?php if (!isset($options['bot_id']) || empty($options['bot_id'])): ?>
    <div class="notice notice-warning">
        <p><?php _e('Please configure your Bot ID in the settings to view analytics data.', 'mozbot'); ?> 
           <a href="<?php echo admin_url('admin.php?page=mozbot-settings'); ?>"><?php _e('Go to Settings', 'mozbot'); ?></a>
        </p>
    </div>
    <?php endif; ?>
</div>

