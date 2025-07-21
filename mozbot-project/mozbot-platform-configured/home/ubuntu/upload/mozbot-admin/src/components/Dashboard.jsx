import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Bot,
  MessageSquare,
  Users,
  TrendingUp,
  Activity,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const Dashboard = () => {
  // Mock data for charts
  const conversationData = [
    { name: 'Mon', conversations: 45, resolved: 38 },
    { name: 'Tue', conversations: 52, resolved: 47 },
    { name: 'Wed', conversations: 38, resolved: 35 },
    { name: 'Thu', conversations: 61, resolved: 55 },
    { name: 'Fri', conversations: 73, resolved: 68 },
    { name: 'Sat', conversations: 29, resolved: 26 },
    { name: 'Sun', conversations: 34, resolved: 31 },
  ]

  const channelData = [
    { name: 'Website', value: 65, color: '#4299e1' }, // Użycie kolorów z nowej palety
    { name: 'Telegram', value: 20, color: '#48bb78' },
    { name: 'WhatsApp', value: 10, color: '#ecc94b' },
    { name: 'Messenger', value: 5, color: '#ed8936' },
  ]

  const responseTimeData = [
    { time: '00:00', avgTime: 2.3 },
    { time: '04:00', avgTime: 1.8 },
    { time: '08:00', avgTime: 3.2 },
    { time: '12:00', avgTime: 4.1 },
    { time: '16:00', avgTime: 3.8 },
    { time: '20:00', avgTime: 2.9 },
  ]

  const stats = [
    {
      title: 'Total Chatbots',
      value: '12',
      change: '+2 this month',
      icon: Bot,
      color: 'text-blue-500', // Zmiana na bardziej stonowane kolory
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Active Conversations',
      value: '1,247',
      change: '+12% from last week',
      icon: MessageSquare,
      color: 'text-green-500',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Total Users',
      value: '8,429',
      change: '+5% from last month',
      icon: Users,
      color: 'text-purple-500',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Resolution Rate',
      value: '94.2%',
      change: '+2.1% improvement',
      icon: TrendingUp,
      color: 'text-orange-500',
      bgColor: 'bg-orange-100'
    }
  ]

  const recentActivity = [
    {
      id: 1,
      type: 'conversation',
      message: 'New conversation started on Website',
      time: '2 minutes ago',
      icon: MessageSquare,
      color: 'text-blue-500'
    },
    {
      id: 2,
      type: 'automation',
      message: 'Automation workflow triggered for lead capture',
      time: '5 minutes ago',
      icon: Activity,
      color: 'text-green-500'
    },
    {
      id: 3,
      type: 'resolved',
      message: 'Support ticket #1247 resolved automatically',
      time: '8 minutes ago',
      icon: CheckCircle,
      color: 'text-green-500'
    },
    {
      id: 4,
      type: 'alert',
      message: 'High response time detected on Telegram channel',
      time: '12 minutes ago',
      icon: AlertCircle,
      color: 'text-orange-500'
    },
    {
      id: 5,
      type: 'user',
      message: 'New user registered: john@example.com',
      time: '15 minutes ago',
      icon: Users,
      color: 'text-purple-500'
    }
  ]

  return (
    <div className="space-y-8 p-4 md:p-6 lg:p-8"> {/* Zwiększenie ogólnego odstępu */}
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"> {/* Dostosowanie gridu */}
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index} className="shadow-md hover:shadow-lg transition-shadow duration-200"> {/* Dodanie cienia */}
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                    <p className="text-sm text-gray-500 mt-1">{stat.change}</p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}> {/* Zmiana na okrągłe ikony */}
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Conversations Chart */}
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle>Conversation Trends</CardTitle>
            <CardDescription>Daily conversations and resolution rates</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={conversationData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /> {/* Zmiana koloru siatki */}
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="conversations" fill="#4299e1" name="Total" /> {/* Użycie kolorów z nowej palety */}
                <Bar dataKey="resolved" fill="#48bb78" name="Resolved" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Channel Distribution */}
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle>Channel Distribution</CardTitle>
            <CardDescription>Conversations by communication channel</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={channelData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                  labelLine={false} // Usunięcie linii do etykiet
                >
                  {channelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Response Time Chart */}
        <Card className="lg:col-span-2 shadow-md">
          <CardHeader>
            <CardTitle>Average Response Time</CardTitle>
            <CardDescription>Response time throughout the day (in seconds)</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={responseTimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /> {/* Zmiana koloru siatki */}
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="avgTime" 
                  stroke="#4299e1" 
                  strokeWidth={2}
                  dot={{ fill: '#4299e1' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest platform events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => {
                const Icon = activity.icon
                return (
                  <div key={activity.id} className="flex items-start space-x-3">
                    <div className={`p-2 rounded-full ${activity.bgColor || 'bg-gray-100'}`}> {/* Zwiększenie paddingu i dodanie domyślnego tła */}
                      <Icon className={`h-5 w-5 ${activity.color}`} /> {/* Zwiększenie rozmiaru ikon */}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">{activity.message}</p>
                      <p className="text-xs text-gray-500 flex items-center mt-1">
                        <Clock className="h-3 w-3 mr-1" />
                        {activity.time}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
            <Button variant="outline" className="w-full mt-4">
              View All Activity
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard


