import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Bot, 
  Plus, 
  Settings, 
  MoreVertical,
  MessageSquare,
  Users,
  Activity,
  Globe,
  Smartphone,
  MessageCircle,
  Send,
  Eye,
  Edit,
  Trash2,
  Power,
  PowerOff
} from 'lucide-react'

const Chatbots = () => {
  const [selectedBot, setSelectedBot] = useState(null)

  // Mock chatbot data
  const chatbots = [
    {
      id: 1,
      name: 'Customer Support Bot',
      description: 'Handles general customer inquiries and support tickets',
      status: 'active',
      channels: ['web', 'telegram'],
      conversations: 1247,
      users: 892,
      responseRate: 94.2,
      lastActive: '2 minutes ago',
      avatar: '🤖'
    },
    {
      id: 2,
      name: 'Sales Assistant',
      description: 'Helps with product inquiries and lead qualification',
      status: 'active',
      channels: ['web', 'whatsapp'],
      conversations: 634,
      users: 445,
      responseRate: 89.7,
      lastActive: '5 minutes ago',
      avatar: '💼'
    },
    {
      id: 3,
      name: 'FAQ Bot',
      description: 'Answers frequently asked questions automatically',
      status: 'inactive',
      channels: ['web'],
      conversations: 89,
      users: 67,
      responseRate: 96.1,
      lastActive: '2 hours ago',
      avatar: '❓'
    },
    {
      id: 4,
      name: 'Booking Assistant',
      description: 'Manages appointment scheduling and calendar integration',
      status: 'active',
      channels: ['web', 'messenger', 'telegram'],
      conversations: 423,
      users: 234,
      responseRate: 91.8,
      lastActive: '1 minute ago',
      avatar: '📅'
    }
  ]

  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'web': return <Globe className="h-4 w-4" />
      case 'telegram': return <Send className="h-4 w-4" />
      case 'whatsapp': return <Smartphone className="h-4 w-4" />
      case 'messenger': return <MessageCircle className="h-4 w-4" />
      default: return <MessageSquare className="h-4 w-4" />
    }
  }

  const getChannelColor = (channel) => {
    switch (channel) {
      case 'web': return 'bg-blue-100 text-blue-800'
      case 'telegram': return 'bg-sky-100 text-sky-800'
      case 'whatsapp': return 'bg-green-100 text-green-800'
      case 'messenger': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Chatbots</h2>
          <p className="text-gray-600 mt-1">Manage your AI-powered chatbots</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          Create Chatbot
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Bots</p>
                <p className="text-2xl font-bold">{chatbots.length}</p>
              </div>
              <Bot className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Bots</p>
                <p className="text-2xl font-bold">{chatbots.filter(bot => bot.status === 'active').length}</p>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Conversations</p>
                <p className="text-2xl font-bold">{chatbots.reduce((sum, bot) => sum + bot.conversations, 0).toLocaleString()}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response Rate</p>
                <p className="text-2xl font-bold">{(chatbots.reduce((sum, bot) => sum + bot.responseRate, 0) / chatbots.length).toFixed(1)}%</p>
              </div>
              <Users className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chatbots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {chatbots.map((bot) => (
          <Card key={bot.id} className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">{bot.avatar}</div>
                  <div>
                    <CardTitle className="text-lg">{bot.name}</CardTitle>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant={bot.status === 'active' ? 'default' : 'secondary'}>
                        {bot.status === 'active' ? (
                          <Power className="h-3 w-3 mr-1" />
                        ) : (
                          <PowerOff className="h-3 w-3 mr-1" />
                        )}
                        {bot.status}
                      </Badge>
                      <span className="text-xs text-gray-500">{bot.lastActive}</span>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="mt-2">{bot.description}</CardDescription>
            </CardHeader>
            
            <CardContent className="pt-0">
              {/* Channels */}
              <div className="mb-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Active Channels</p>
                <div className="flex flex-wrap gap-2">
                  {bot.channels.map((channel) => (
                    <Badge key={channel} variant="outline" className={`${getChannelColor(channel)} border-0`}>
                      {getChannelIcon(channel)}
                      <span className="ml-1 capitalize">{channel}</span>
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">{bot.conversations.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">Conversations</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">{bot.users.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">Users</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">{bot.responseRate}%</p>
                  <p className="text-xs text-gray-500">Response Rate</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <Button variant="outline" size="sm" className="flex-1">
                  <Eye className="h-4 w-4 mr-1" />
                  View
                </Button>
                <Button variant="outline" size="sm" className="flex-1">
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button variant="outline" size="sm" className="flex-1">
                  <Settings className="h-4 w-4 mr-1" />
                  Config
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Create New Bot Card */}
        <Card className="border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors duration-200 cursor-pointer group">
          <CardContent className="flex flex-col items-center justify-center h-full min-h-[300px] text-center">
            <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-100 transition-colors">
              <Plus className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Create New Chatbot</h3>
            <p className="text-gray-500 text-sm mb-4">Set up a new AI-powered chatbot for your business</p>
            <Button variant="outline" className="group-hover:bg-blue-50 group-hover:border-blue-300">
              Get Started
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Chatbots

