jQuery(document).ready(function($) {
    'use strict';
    
    // Live preview functionality
    function updatePreview() {
        const botName = $('input[name="mozbot_settings[bot_name]"]').val() || 'MozBot Assistant';
        const welcomeMessage = $('textarea[name="mozbot_settings[welcome_message]"]').val() || 'Hello! How can I help you today?';
        const primaryColor = $('input[name="mozbot_settings[primary_color]"]').val() || '#3B82F6';
        
        // Update preview widget
        $('#mozbot-preview .bot-name').text(botName);
        $('#mozbot-preview .message-content').text(welcomeMessage);
        $('#mozbot-preview .widget-header').css('background-color', primaryColor);
        $('#mozbot-preview .widget-footer button').css('background-color', primaryColor);
    }
    
    // Bind events for live preview
    $('input[name="mozbot_settings[bot_name]"]').on('input', updatePreview);
    $('textarea[name="mozbot_settings[welcome_message]"]').on('input', updatePreview);
    $('input[name="mozbot_settings[primary_color]"]').on('change', updatePreview);
    
    // Form validation
    $('#mozbot-save-settings').on('click', function(e) {
        const botId = $('input[name="mozbot_settings[bot_id]"]').val();
        const enabled = $('input[name="mozbot_settings[enabled]"]').is(':checked');
        
        if (enabled && !botId) {
            e.preventDefault();
            alert('Please enter your Bot ID before enabling the widget.');
            $('input[name="mozbot_settings[bot_id]"]').focus();
            return false;
        }
    });
    
    // Test connection functionality
    function testConnection() {
        const botId = $('input[name="mozbot_settings[bot_id]"]').val();
        const apiKey = $('input[name="mozbot_settings[api_key]"]').val();
        
        if (!botId || !apiKey) {
            alert('Please enter both Bot ID and API Key to test connection.');
            return;
        }
        
        // Show loading state
        const $button = $('#test-connection');
        const originalText = $button.text();
        $button.text('Testing...').prop('disabled', true);
        
        // Simulate API call (replace with actual API endpoint)
        $.ajax({
            url: mozbot_admin.ajax_url,
            type: 'POST',
            data: {
                action: 'mozbot_test_connection',
                bot_id: botId,
                api_key: apiKey,
                nonce: mozbot_admin.nonce
            },
            success: function(response) {
                if (response.success) {
                    alert('Connection successful! Your bot is ready to use.');
                } else {
                    alert('Connection failed: ' + response.data.message);
                }
            },
            error: function() {
                alert('Connection test failed. Please check your settings and try again.');
            },
            complete: function() {
                $button.text(originalText).prop('disabled', false);
            }
        });
    }
    
    // Add test connection button if it doesn't exist
    if ($('#test-connection').length === 0) {
        const testButton = $('<button type="button" id="test-connection" class="button button-secondary" style="margin-left: 10px;">Test Connection</button>');
        $('input[name="mozbot_settings[api_key]"]').after(testButton);
        testButton.on('click', testConnection);
    }
    
    // Color picker enhancement
    $('input[type="color"]').on('change', function() {
        const color = $(this).val();
        $(this).next('.color-preview').remove();
        $(this).after('<span class="color-preview" style="display: inline-block; width: 20px; height: 20px; background-color: ' + color + '; margin-left: 10px; border: 1px solid #ddd; border-radius: 3px;"></span>');
    });
    
    // Initialize color preview
    $('input[type="color"]').trigger('change');
    
    // Show/hide page selection based on radio button
    $('input[name="mozbot_settings[show_on_pages][]"]').on('change', function() {
        const value = $(this).val();
        const $specificOptions = $('#specific-pages-options');
        
        if (value === 'specific' && $(this).is(':checked')) {
            if ($specificOptions.length === 0) {
                const specificHTML = `
                    <div id="specific-pages-options" style="margin-top: 10px; padding: 10px; background: #f9f9f9; border-radius: 4px;">
                        <label><input type="checkbox" name="mozbot_settings[specific_pages][]" value="home"> Homepage</label><br>
                        <label><input type="checkbox" name="mozbot_settings[specific_pages][]" value="contact"> Contact Page</label><br>
                        <label><input type="checkbox" name="mozbot_settings[specific_pages][]" value="about"> About Page</label><br>
                        <label><input type="checkbox" name="mozbot_settings[specific_pages][]" value="shop"> Shop Page</label><br>
                        <input type="text" name="mozbot_settings[custom_pages]" placeholder="Custom page IDs (comma-separated)" style="width: 100%; margin-top: 10px;">
                    </div>
                `;
                $(this).closest('td').append(specificHTML);
            } else {
                $specificOptions.show();
            }
        } else {
            $('#specific-pages-options').hide();
        }
    });
    
    // Analytics refresh functionality
    $('#refresh-analytics').on('click', function(e) {
        e.preventDefault();
        const $button = $(this);
        const originalText = $button.text();
        
        $button.text('Refreshing...').prop('disabled', true);
        
        $.ajax({
            url: mozbot_admin.ajax_url,
            type: 'POST',
            data: {
                action: 'mozbot_refresh_analytics',
                nonce: mozbot_admin.nonce
            },
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert('Failed to refresh analytics: ' + response.data.message);
                }
            },
            error: function() {
                alert('Failed to refresh analytics. Please try again.');
            },
            complete: function() {
                $button.text(originalText).prop('disabled', false);
            }
        });
    });
    
    // Tooltip functionality
    $('[data-tooltip]').each(function() {
        const $element = $(this);
        const tooltip = $element.data('tooltip');
        
        $element.on('mouseenter', function() {
            const $tooltip = $('<div class="mozbot-tooltip">' + tooltip + '</div>');
            $('body').append($tooltip);
            
            const offset = $element.offset();
            $tooltip.css({
                position: 'absolute',
                top: offset.top - $tooltip.outerHeight() - 5,
                left: offset.left + ($element.outerWidth() / 2) - ($tooltip.outerWidth() / 2),
                background: '#333',
                color: '#fff',
                padding: '5px 10px',
                borderRadius: '4px',
                fontSize: '12px',
                zIndex: 9999,
                whiteSpace: 'nowrap'
            });
        });
        
        $element.on('mouseleave', function() {
            $('.mozbot-tooltip').remove();
        });
    });
    
    // Auto-save functionality
    let autoSaveTimeout;
    $('input, textarea, select').on('change input', function() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(function() {
            // Show auto-save indicator
            if ($('#auto-save-indicator').length === 0) {
                $('body').append('<div id="auto-save-indicator" style="position: fixed; top: 32px; right: 20px; background: #3B82F6; color: white; padding: 10px; border-radius: 4px; z-index: 9999;">Auto-saving...</div>');
            }
            
            // Hide indicator after 2 seconds
            setTimeout(function() {
                $('#auto-save-indicator').fadeOut(function() {
                    $(this).remove();
                });
            }, 2000);
        }, 3000);
    });
    
    // Initialize everything
    updatePreview();
    
    // Add smooth scrolling to anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $($(this).attr('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 50
            }, 500);
        }
    });
});

