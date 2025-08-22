"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Send, Loader2, Bot, User, X } from "lucide-react"
import Card from "./ui/card"

interface BaseMessage {
  sender: string
}

interface TextMessage extends BaseMessage {
  text: string
}

type Message = TextMessage

const API_BASE_URL = "http://localhost:8020"

const apiService = {
  async sendMessage(message: string, sessionId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/legacy-check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      return data.response || data.message || "Response received"
    } catch (error) {
      console.error("Legacy API Error:", error)
      return `Legacy Check Response: Processing "${message}". Please ensure you provide ICP address and email in format: <ICP_ADDRESS> <EMAIL> [threshold]`
    }
  },
}

const RichTextMessage: React.FC<{ text: string; className?: string }> = ({ text, className = "" }) => {
  return (
    <div className={`whitespace-pre-wrap leading-relaxed break-words overflow-wrap-anywhere ${className}`}>{text}</div>
  )
}

interface LegacyPopupProps {
  isOpen: boolean
  onToggle: () => void
}

export default function LegacyPopup({ isOpen, onToggle }: LegacyPopupProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "ai",
      text: "Hello! I'm your ChainPilot Legacy Assistant. I can help you check ICP address activity and monitor for inactivity.\n\nPlease provide: <ICP_ADDRESS> <EMAIL> [threshold]\n\nExample: a1b2c3d4e5f6... user@example.com 2 hours",
    },
  ])

  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  useEffect(() => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setSessionId(newSessionId)
  }, [])

  const handleSendMessage = async () => {
    if (inputValue.trim() === "") return

    const newUserMessage = { sender: "user", text: inputValue }
    setMessages((prev) => [...prev, newUserMessage])

    setInputValue("")
    setIsLoading(true)

    try {
      const response = await apiService.sendMessage(inputValue, sessionId)

      const newAiMessage = {
        sender: "ai",
        text: response,
      }

      setMessages((prev) => [...prev, newAiMessage])
    } catch (err) {
      console.error("API Error:", err)

      const errorMessage = {
        sender: "ai",
        text: "Sorry, I'm having trouble connecting to the legacy service. Please try again later.",
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.8, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.8, y: 20 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="fixed bottom-20 right-6 z-50"
      >
        <Card
          className={`bg-zinc-900/95 backdrop-blur-sm border-zinc-700/50 shadow-2xl transition-all duration-30 w-96 h-[500px]
          `}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-zinc-800/50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg">
                <Bot size={16} className="text-white" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Legacy Assistant</h3>
                <p className="text-xs text-zinc-400">ICP Activity Monitor</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <motion.button
                onClick={onToggle}
                className="p-1.5 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X size={14} />
              </motion.button>
            </div>
          </div>

          <>
            {/* Messages Area */}
            <div className="flex-grow overflow-y-auto p-4 space-y-4 h-80">
              <AnimatePresence>
                {messages.map((msg, index) => (
                  <motion.div
                    key={index}
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -20, opacity: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`flex items-end gap-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {msg.sender === "ai" && (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                        <Bot size={14} className="text-white" />
                      </div>
                    )}

                    <div
                      className={`max-w-xs rounded-2xl p-3 text-sm min-w-0 ${
                        msg.sender === "user"
                          ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-br-md"
                          : "bg-zinc-800/80 text-zinc-100 rounded-bl-md border border-zinc-700/50"
                      }`}
                    >
                      <RichTextMessage text={msg.text} />
                    </div>

                    {msg.sender === "user" && (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                        <User size={14} className="text-white" />
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex justify-start"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center">
                      <Bot size={14} className="text-white" />
                    </div>
                    <div className="bg-zinc-800/80 rounded-2xl rounded-bl-md p-3 border border-zinc-700/50">
                      <div className="flex items-center gap-2">
                        <motion.div
                          className="w-1.5 h-1.5 bg-blue-400 rounded-full"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, delay: 0 }}
                        />
                        <motion.div
                          className="w-1.5 h-1.5 bg-blue-400 rounded-full"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, delay: 0.2 }}
                        />
                        <motion.div
                          className="w-1.5 h-1.5 bg-blue-400 rounded-full"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, delay: 0.4 }}
                        />
                        <span className="text-zinc-400 text-xs ml-2">Processing...</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-zinc-800/50">
              <div className="relative">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSendMessage()}
                  placeholder="Enter ICP address and email..."
                  className="w-full bg-zinc-800/80 border border-zinc-700/50 text-white rounded-lg py-2.5 pl-3 pr-10 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all text-sm placeholder-zinc-500"
                  disabled={isLoading}
                />
                <motion.button
                  onClick={handleSendMessage}
                  className={`absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md transition-all ${
                    isLoading || !inputValue.trim()
                      ? "text-zinc-500 cursor-not-allowed"
                      : "text-zinc-400 hover:text-white hover:bg-blue-500/20"
                  }`}
                  disabled={isLoading || !inputValue.trim()}
                  whileHover={{ scale: isLoading || !inputValue.trim() ? 1 : 1.1 }}
                  whileTap={{ scale: isLoading || !inputValue.trim() ? 1 : 0.9 }}
                >
                  {isLoading ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                    >
                      <Loader2 size={16} />
                    </motion.div>
                  ) : (
                    <Send size={16} />
                  )}
                </motion.button>
              </div>
            </div>
          </>
        </Card>
      </motion.div>
    </AnimatePresence>
  )
}
