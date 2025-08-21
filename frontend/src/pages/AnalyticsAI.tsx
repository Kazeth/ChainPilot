import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  TrendingUp,
  BarChart,
  Newspaper,
  Plus,
  MessageSquare,
  Loader2,
  Bold,
  Italic,
  Type,
  Bot,
  User,
  Sparkles,
} from "lucide-react";
import Button from "../components/ui/button";
import Card from "../components/ui/card";

// Message type definitions
interface BaseMessage {
  sender: string;
}

interface TextMessage extends BaseMessage {
  text: string;
}

interface StructuredMessage extends BaseMessage {
  type: "structured";
  content: any;
}

type Message = TextMessage | StructuredMessage;

// API Configuration
const API_BASE_URL = "http://localhost:8083";

// Generate unique session ID
const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
};

// API Service for connecting to backend
const apiService = {
  async sendMessage(message: string, sessionId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: message,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.answer;
    } catch (error) {
      console.error('API Error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      throw new Error(`Failed to get AI response: ${errorMessage}`);
    }
  }
};

interface RichTextMessageProps {
  text: string;
  className?: string;
}

// Helper function to parse markdown-style formatting
const parseRichText = (text: string): React.ReactElement[] => {
  const parts: React.ReactElement[] = [];
  let currentIndex = 0;
  let key = 0;

  // Regex to match **bold**, *italic*, and ***bold italic***
  const markdownRegex = /(\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*)/g;
  let match;

  while ((match = markdownRegex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > currentIndex) {
      parts.push(
        <span key={key++}>
          {text.substring(currentIndex, match.index)}
        </span>
      );
    }

    // Determine the type of formatting and add styled element
    if (match[1].startsWith('***') && match[1].endsWith('***')) {
      // Bold italic
      parts.push(
        <strong key={key++} className="font-bold italic">
          {match[2]}
        </strong>
      );
    } else if (match[1].startsWith('**') && match[1].endsWith('**')) {
      // Bold
      parts.push(
        <strong key={key++} className="font-bold">
          {match[3]}
        </strong>
      );
    } else if (match[1].startsWith('*') && match[1].endsWith('*')) {
      // Italic
      parts.push(
        <em key={key++} className="italic">
          {match[4]}
        </em>
      );
    }

    currentIndex = match.index + match[0].length;
  }

  // Add remaining text after last match
  if (currentIndex < text.length) {
    parts.push(
      <span key={key++}>
        {text.substring(currentIndex)}
      </span>
    );
  }

  return parts;
};

export const RichTextMessage: React.FC<RichTextMessageProps> = ({ 
  text, 
  className = "" 
}) => {
  const richTextElements = parseRichText(text);
  
  return (
    <div className={className}>
      {richTextElements}
    </div>
  );
};




export default function AIAnalyticsPage() {
  const [chats, setChats] = useState<{
    id: number;
    title: string;
    messages: Message[];
  }[]>([
    {
      id: 1,
      title: "ChainPilot AI",
      messages: [
        {
          sender: "ai",
          text: "Hello! I'm your ChainPilot AI assistant. I can help you with crypto analysis, market insights, and trading strategies. How can I assist you today?",
        },
      ],
    },
  ]);

  const [activeChatId, setActiveChatId] = useState(1);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>("");
  const [showFormattingHelp, setShowFormattingHelp] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chats, isLoading]);

  // Generate session ID on component mount
  useEffect(() => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  // Function to insert formatting into the input
  const insertFormatting = (type: 'bold' | 'italic' | 'bold-italic') => {
    const input = document.querySelector('input[type="text"]') as HTMLInputElement;
    if (!input) return;
    
    const start = input.selectionStart || 0;
    const end = input.selectionEnd || 0;
    const selectedText = inputValue.slice(start, end);
    
    let formattedText = '';
    switch (type) {
      case 'bold':
        formattedText = `**${selectedText || 'text'}**`;
        break;
      case 'italic':
        formattedText = `*${selectedText || 'text'}*`;
        break;
      case 'bold-italic':
        formattedText = `***${selectedText || 'text'}***`;
        break;
    }
    
    const newValue = inputValue.slice(0, start) + formattedText + inputValue.slice(end);
    setInputValue(newValue);
    
    // Focus back to input and set cursor position
    setTimeout(() => {
      input.focus();
      const newPosition = start + formattedText.length;
      input.setSelectionRange(newPosition, newPosition);
    }, 0);
  };

  const activeChat = chats.find((chat) => chat.id === activeChatId);

  const handleSendMessage = async () => {
    if (inputValue.trim() === "" || !activeChat) return;

    const newUserMessage = { sender: "user", text: inputValue };
    setChats((prevChats) =>
      prevChats.map((chat) =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, newUserMessage] }
          : chat
      )
    );

    setInputValue("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.sendMessage(inputValue, sessionId);
      
      const newAiMessage = {
        sender: "ai",
        text: response,
      };

      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                messages: [...chat.messages, newAiMessage],
              }
            : chat
        )
      );
    } catch (err) {
      setError("Failed to get response from AI agent");
      console.error("API Error:", err);
      
      // Add error message to chat
      const errorMessage = {
        sender: "ai",
        text: "Sorry, I'm having trouble connecting to the AI service. Please try again.",
      };
      
      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                messages: [...chat.messages, errorMessage],
              }
            : chat
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    const newChatId =
      chats.length > 0 ? Math.max(...chats.map((c: any) => c.id)) + 1 : 1;
    const newChat = {
      id: newChatId,
      title: `New Analysis ${newChatId}`,
      messages: [
        {
          sender: "ai",
          text: "New chat started. What market data can I provide for you?",
        },
      ],
    };
    setChats([...chats, newChat]);
    setActiveChatId(newChatId);
  };

  return (
    <div
      className="flex h-[calc(100vh-5rem)] bg-zinc-950 relative overflow-hidden"
      style={{ fontFamily: "'Creati Display', sans-serif" }}
    >
      {/* Sidebar for Chat History */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ x: -320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -320, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="w-80 bg-zinc-900/95 backdrop-blur-sm border-r border-zinc-800/50 flex flex-col relative z-10"
          >
            {/* Header */}
            <motion.div 
              className="p-6 border-b border-zinc-800/50"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  onClick={handleNewChat}
                  className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-2 py-3"
                >
                  <Plus size={18} /> New Chat
                </Button>
              </motion.div>
            </motion.div>

            {/* Chat List */}
            <div className="flex-grow overflow-y-auto p-4 space-y-2 sidebar-scroll">
              <AnimatePresence>
                {chats.map((chat, index) => (
                  <motion.div
                    key={chat.id}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -20, opacity: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div
                      onClick={() => setActiveChatId(chat.id)}
                      className={`flex items-center gap-3 p-4 rounded-xl cursor-pointer transition-all duration-200 group ${
                        activeChatId === chat.id 
                          ? "bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 shadow-lg" 
                          : "hover:bg-zinc-800/50 border border-transparent"
                      }`}
                    >
                      <div className={`p-2 rounded-lg ${
                        activeChatId === chat.id ? "bg-blue-500/30" : "bg-zinc-700/50"
                      }`}>
                        <MessageSquare size={16} className={
                          activeChatId === chat.id ? "text-blue-400" : "text-zinc-400"
                        } />
                      </div>
                      <span className={`text-sm font-medium truncate ${
                        activeChatId === chat.id ? "text-blue-100" : "text-zinc-300"
                      }`}>
                        {chat.title}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex flex-col flex-grow relative">
        {/* Header */}
        <motion.div 
          className="flex items-center justify-between p-4 border-b border-zinc-800/50 bg-zinc-900/50 backdrop-blur-sm"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          <div className="flex items-center gap-3">
            <motion.button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <MessageSquare size={20} />
            </motion.button>
            <div className="flex items-center gap-2">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg">
                <Bot size={20} className="text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">ChainPilot AI</h2>
                <p className="text-xs text-zinc-400">Your crypto analysis assistant</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles size={16} className="text-blue-400" />
            </motion.div>
            <span className="text-xs text-zinc-500">Online</span>
          </div>
        </motion.div>

        {/* Messages Area */}
        <div className="flex-grow overflow-y-auto p-6 space-y-6 chat-scroll">
          <AnimatePresence>
            {activeChat?.messages.map((msg, index) => (
              <motion.div
                key={index}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -20, opacity: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`flex items-end gap-4 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.sender === "ai" && (
                  <motion.div 
                    className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0 shadow-lg"
                    whileHover={{ scale: 1.1 }}
                  >
                    <Bot size={18} className="text-white" />
                  </motion.div>
                )}
                
                <motion.div
                  className={`max-w-2xl rounded-2xl p-4 shadow-lg ${
                    msg.sender === "user" 
                      ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-br-md" 
                      : "bg-zinc-800/80 backdrop-blur-sm text-zinc-100 rounded-bl-md border border-zinc-700/50"
                  }`}
                  whileHover={{ scale: 1.01 }}
                  transition={{ duration: 0.2 }}
                >
                  {(msg as any).type === "structured" ? (
                    <div className="space-y-4">
                      <RichTextMessage text={(msg as any).content.intro} />
                      <div className="space-y-3">
                        {(msg as any).content.coins.map((coin: any, coinIndex: number) => (
                          <motion.div
                            key={coin.name}
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: coinIndex * 0.1 }}
                          >
                            <Card className="flex items-center gap-4 !p-4 bg-zinc-700/50 border-zinc-600/50 hover:bg-zinc-700 transition-colors">
                              <div className="text-[#87efff] text-xl">{coin.icon}</div>
                              <div>
                                <p className="font-semibold text-white">{coin.name}</p>
                                <p className="text-sm text-zinc-300">
                                  Sentiment:{" "}
                                  <span className="font-medium text-white">{coin.sentiment}</span>
                                </p>
                                <p className="text-sm text-zinc-400">{coin.keyMetric}</p>
                              </div>
                            </Card>
                          </motion.div>
                        ))}
                      </div>
                      <div className="flex flex-wrap gap-2 pt-2">
                        {(msg as any).content.suggestions.map((suggestion: any, suggestionIndex: number) => (
                          <motion.div
                            key={suggestion}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: suggestionIndex * 0.05 }}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <Button className="text-xs !px-3 !py-1.5 border-zinc-600 text-zinc-300 hover:bg-zinc-700 hover:text-white hover:border-zinc-500 transition-all">
                              {suggestion}
                            </Button>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <RichTextMessage text={(msg as TextMessage).text} />
                  )}
                </motion.div>

                {msg.sender === "user" && (
                  <motion.div 
                    className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0 shadow-lg"
                    whileHover={{ scale: 1.1 }}
                  >
                    <User size={18} className="text-white" />
                  </motion.div>
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
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center">
                  <Bot size={18} className="text-white" />
                </div>
                <div className="bg-zinc-800/80 backdrop-blur-sm rounded-2xl rounded-bl-md p-4 border border-zinc-700/50">
                  <div className="flex items-center gap-2">
                    <motion.div
                      className="w-2 h-2 bg-blue-400 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-blue-400 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-blue-400 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                    />
                    <span className="text-zinc-400 text-sm ml-2">AI is thinking...</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center"
            >
              <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-2 rounded-lg">
                ⚠️ {error}
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Area with Formatting Tools */}
        <motion.div 
          className="p-6 border-t border-zinc-800/50 bg-zinc-900/80 backdrop-blur-sm"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {/* Formatting Toolbar */}
          <motion.div 
            className="flex items-center gap-3 mb-4 pb-4 border-b border-zinc-800/50"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-center gap-1 bg-zinc-800/50 rounded-lg p-1">
              <motion.button
                onClick={() => insertFormatting('bold')}
                className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-700 rounded-md transition-colors"
                title="Bold (**text**)"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Bold size={16} />
              </motion.button>
              <motion.button
                onClick={() => insertFormatting('italic')}
                className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-700 rounded-md transition-colors"
                title="Italic (*text*)"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Italic size={16} />
              </motion.button>
              <motion.button
                onClick={() => insertFormatting('bold-italic')}
                className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-700 rounded-md transition-colors"
                title="Bold Italic (***text***)"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Type size={16} />
              </motion.button>
            </div>
            <motion.button
              onClick={() => setShowFormattingHelp(!showFormattingHelp)}
              className="ml-auto text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-3 py-1 rounded-md hover:bg-zinc-800"
              whileHover={{ scale: 1.05 }}
            >
              {showFormattingHelp ? "Hide" : "Show"} Formatting Help
            </motion.button>
          </motion.div>

          {/* Formatting Help */}
          <AnimatePresence>
            {showFormattingHelp && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="mb-4 p-4 bg-zinc-800/80 rounded-xl text-sm text-zinc-300 border border-zinc-700/50">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <code className="bg-zinc-700/70 px-2 py-1 rounded">**bold text**</code> 
                      <span>→</span> 
                      <strong className="text-white">bold text</strong>
                    </div>
                    <div className="flex items-center gap-3">
                      <code className="bg-zinc-700/70 px-2 py-1 rounded">*italic text*</code> 
                      <span>→</span> 
                      <em className="text-white">italic text</em>
                    </div>
                    <div className="flex items-center gap-3">
                      <code className="bg-zinc-700/70 px-2 py-1 rounded">***bold italic***</code> 
                      <span>→</span> 
                      <strong><em className="text-white">bold italic</em></strong>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Input Field */}
          <motion.div 
            className="relative"
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSendMessage()}
              placeholder="Ask about crypto analysis, market insights, or trading strategies..."
              className="w-full bg-zinc-800/80 backdrop-blur-sm border-2 border-zinc-700/50 text-white rounded-xl py-4 pl-6 pr-14 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 placeholder-zinc-500"
              disabled={isLoading}
            />
            <motion.button
              onClick={handleSendMessage}
              className={`absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all duration-200 ${
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
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Loader2 size={20} />
                </motion.div>
              ) : (
                <Send size={20} />
              )}
            </motion.button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}