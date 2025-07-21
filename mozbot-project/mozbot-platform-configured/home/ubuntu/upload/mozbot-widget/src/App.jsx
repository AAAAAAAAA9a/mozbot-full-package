import { useState } from 'react'
import ChatWidget from './components/ChatWidget'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import './App.css'

function App() {
  const [widgetConfig, setWidgetConfig] = useState({
    botName: "MozBot Assistant",
    welcomeMessage: "Hello! How can I help you today?",
    primaryColor: "#3B82F6",
    position: "bottom-right"
  })

  const [showWidget, setShowWidget] = useState(false)

  const colorOptions = [
    { name: "Blue", value: "#3B82F6" },
    { name: "Green", value: "#10B981" },
    { name: "Purple", value: "#8B5CF6" },
    { name: "Red", value: "#EF4444" },
    { name: "Orange", value: "#F59E0B" },
    { name: "Pink", value: "#EC4899" }
  ]

  const positionOptions = [
    { name: "Bottom Right", value: "bottom-right" },
    { name: "Bottom Left", value: "bottom-left" },
    { name: "Top Right", value: "top-right" },
    { name: "Top Left", value: "top-left" }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">MozBot Widget Demo</h1>
            </div>
            <Button 
              onClick={() => setShowWidget(!showWidget)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {showWidget ? 'Hide Widget' : 'Show Widget'}
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Widget Configuration</CardTitle>
                <CardDescription>Customize your chat widget appearance and behavior</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Bot Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bot Name
                  </label>
                  <input
                    type="text"
                    value={widgetConfig.botName}
                    onChange={(e) => setWidgetConfig(prev => ({ ...prev, botName: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Welcome Message */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Welcome Message
                  </label>
                  <textarea
                    value={widgetConfig.welcomeMessage}
                    onChange={(e) => setWidgetConfig(prev => ({ ...prev, welcomeMessage: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                  />
                </div>

                {/* Primary Color */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Color
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {colorOptions.map((color) => (
                      <button
                        key={color.value}
                        onClick={() => setWidgetConfig(prev => ({ ...prev, primaryColor: color.value }))}
                        className={`w-full h-10 rounded-md border-2 transition-all ${
                          widgetConfig.primaryColor === color.value 
                            ? 'border-gray-900 scale-105' 
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                        style={{ backgroundColor: color.value }}
                        title={color.name}
                      />
                    ))}
                  </div>
                </div>

                {/* Position */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Position
                  </label>
                  <select
                    value={widgetConfig.position}
                    onChange={(e) => setWidgetConfig(prev => ({ ...prev, position: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {positionOptions.map((position) => (
                      <option key={position.value} value={position.value}>
                        {position.name}
                      </option>
                    ))}
                  </select>
                </div>

                <Button 
                  onClick={() => setShowWidget(true)}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  Preview Widget
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Demo Content */}
          <div className="lg:col-span-2">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Embeddable Chat Widget</CardTitle>
                  <CardDescription>
                    A fully customizable chat widget that can be embedded on any website
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose max-w-none">
                    <h3>Features</h3>
                    <ul>
                      <li><strong>Responsive Design:</strong> Works perfectly on desktop and mobile devices</li>
                      <li><strong>Customizable Appearance:</strong> Match your brand colors and styling</li>
                      <li><strong>Real-time Messaging:</strong> Instant communication with smooth animations</li>
                      <li><strong>Multi-position Support:</strong> Place the widget anywhere on your page</li>
                      <li><strong>Easy Integration:</strong> Simple JavaScript snippet for any website</li>
                      <li><strong>AI-Powered Responses:</strong> Intelligent bot responses and conversation flow</li>
                    </ul>

                    <h3>Integration Code</h3>
                    <div className="bg-gray-100 p-4 rounded-lg font-mono text-sm">
                      <pre>{`<!-- Add this script to your website -->
<script src="https://cdn.mozbot.com/widget.js"></script>
<script>
  MozBot.init({
    botId: 'your-bot-id',
    botName: '${widgetConfig.botName}',
    welcomeMessage: '${widgetConfig.welcomeMessage}',
    primaryColor: '${widgetConfig.primaryColor}',
    position: '${widgetConfig.position}'
  });
</script>`}</pre>
                    </div>

                    <h3>WordPress Plugin</h3>
                    <p>
                      For WordPress users, we provide a dedicated plugin that makes integration even easier. 
                      Simply install the MozBot plugin, configure your settings through the admin panel, 
                      and the widget will automatically appear on your site.
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Demo Website Content</CardTitle>
                  <CardDescription>This simulates a typical website where the chat widget would be embedded</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <h2 className="text-2xl font-bold text-gray-900">Welcome to Our Company</h2>
                    <p className="text-gray-600">
                      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
                      incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
                      nostrud exercitation ullamco laboris.
                    </p>
                    <p className="text-gray-600">
                      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
                      eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, 
                      sunt in culpa qui officia deserunt mollit anim id est laborum.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-blue-900">Our Services</h3>
                        <p className="text-blue-700 text-sm mt-1">
                          We provide comprehensive solutions for your business needs.
                        </p>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-green-900">24/7 Support</h3>
                        <p className="text-green-700 text-sm mt-1">
                          Our team is always ready to help you with any questions.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Widget */}
      {showWidget && (
        <ChatWidget
          botName={widgetConfig.botName}
          welcomeMessage={widgetConfig.welcomeMessage}
          primaryColor={widgetConfig.primaryColor}
          position={widgetConfig.position}
        />
      )}
    </div>
  )
}

export default App

