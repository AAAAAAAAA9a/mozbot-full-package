import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { 
  MessageCircle, 
  X, 
  Send, 
  Minimize2,
  Bot,
  User,
  Paperclip,
  Smile
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const ChatWidget = ({ 
  botName = "MozBot Assistant",
  welcomeMessage = "Hello! How can I help you today?",
  primaryColor = "#3B82F6",
  position = "bottom-right",
  isOpen: controlledIsOpen,
  onToggle
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: welcomeMessage,
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const actualIsOpen = controlledIsOpen !== undefined ? controlledIsOpen : isOpen
  const actualToggle = onToggle || (() => setIsOpen(!isOpen))

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    // Simulate bot response
    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        text: getBotResponse(inputValue),
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botResponse])
      setIsTyping(false)
    }, 1500)
  }

  const getBotResponse = (userInput) => {
    const input = userInput.toLowerCase()
    
    if (input.includes('hello') || input.includes('hi')) {
      return "Hello! I'm here to help you. What can I assist you with today?"
    } else if (input.includes('help')) {
      return "I'd be happy to help! You can ask me about our products, services, or any questions you might have."
    } else if (input.includes('price') || input.includes('cost')) {
      return "For pricing information, I'd recommend speaking with our sales team. Would you like me to connect you with them?"
    } else if (input.includes('support')) {
      return "I can help with basic support questions. For complex technical issues, I can escalate you to our support team."
    } else {
      return "Thank you for your message! I'm processing your request. Is there anything specific I can help you with?"
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const positionClasses = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4'
  }

  return (
    <div className={`fixed ${positionClasses[position]} z-50`}>
      <AnimatePresence>
        {actualIsOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.2 }}
            className="mb-4"
          >
            <Card className="w-80 h-96 shadow-2xl border-0 overflow-hidden">
              {/* Header */}
              <CardHeader 
                className="p-4 text-white flex flex-row items-center justify-between"
                style={{ backgroundColor: primaryColor }}
              >
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">{botName}</h3>
                    <p className="text-xs opacity-90">Online now</p>
                  </div>
                </div>
                <div className="flex space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 text-white hover:bg-white hover:bg-opacity-20"
                    onClick={() => {/* Minimize functionality */}}
                  >
                    <Minimize2 className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 text-white hover:bg-white hover:bg-opacity-20"
                    onClick={actualToggle}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </CardHeader>

              {/* Messages */}
              <CardContent className="p-0 flex flex-col h-full">
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex items-start space-x-2 max-w-[80%] ${
                        message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      }`}>
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                          message.sender === 'user' 
                            ? 'bg-gray-300 text-gray-700' 
                            : 'text-white'
                        }`} style={message.sender === 'bot' ? { backgroundColor: primaryColor } : {}}>
                          {message.sender === 'user' ? <User className="h-3 w-3" /> : <Bot className="h-3 w-3" />}
                        </div>
                        <div className={`px-3 py-2 rounded-lg text-sm ${
                          message.sender === 'user'
                            ? 'bg-gray-100 text-gray-900'
                            : 'text-white'
                        }`} style={message.sender === 'bot' ? { backgroundColor: primaryColor } : {}}>
                          {message.text}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="flex items-start space-x-2">
                        <div 
                          className="w-6 h-6 rounded-full flex items-center justify-center text-xs text-white"
                          style={{ backgroundColor: primaryColor }}
                        >
                          <Bot className="h-3 w-3" />
                        </div>
                        <div 
                          className="px-3 py-2 rounded-lg text-sm text-white"
                          style={{ backgroundColor: primaryColor }}
                        >
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-white bg-opacity-60 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-white bg-opacity-60 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-white bg-opacity-60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 relative">
                      <textarea
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-opacity-50 text-sm"
                        style={{ focusRingColor: primaryColor }}
                        rows={1}
                      />
                    </div>
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputValue.trim()}
                      size="sm"
                      className="h-8 w-8 p-0"
                      style={{ backgroundColor: primaryColor }}
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex space-x-2">
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-gray-400">
                        <Paperclip className="h-3 w-3" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-gray-400">
                        <Smile className="h-3 w-3" />
                      </Button>
                    </div>
                    <p className="text-xs text-gray-400">Powered by MozBot</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Button */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          onClick={actualToggle}
          className="w-14 h-14 rounded-full shadow-lg border-0 text-white"
          style={{ backgroundColor: primaryColor }}
        >
          <AnimatePresence mode="wait">
            {actualIsOpen ? (
              <motion.div
                key="close"
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <X className="h-6 w-6" />
              </motion.div>
            ) : (
              <motion.div
                key="open"
                initial={{ rotate: 90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: -90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <MessageCircle className="h-6 w-6" />
              </motion.div>
            )}
          </AnimatePresence>
        </Button>
      </motion.div>
    </div>
  )
}

export default ChatWidget

