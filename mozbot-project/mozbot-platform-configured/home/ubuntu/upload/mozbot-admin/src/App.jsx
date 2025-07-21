import { useState } from 'react'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import Chatbots from './components/Chatbots'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'chatbots':
        return <Chatbots />
      case 'conversations':
        return <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Conversations</h2>
          <p className="text-gray-600">Conversation management coming soon...</p>
        </div>
      case 'automations':
        return <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Automations</h2>
          <p className="text-gray-600">Automation workflows coming soon...</p>
        </div>
      case 'users':
        return <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Users</h2>
          <p className="text-gray-600">User management coming soon...</p>
        </div>
      case 'settings':
        return <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Settings</h2>
          <p className="text-gray-600">Platform settings coming soon...</p>
        </div>
      default:
        return <Dashboard />
    }
  }

  return (
    <Layout currentPage={currentPage} onPageChange={setCurrentPage}>
      {renderPage()}
    </Layout>
  )
}

export default App

