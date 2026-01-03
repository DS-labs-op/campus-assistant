'use client'

import { useState, useRef, useEffect, useId } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { useChat } from '@/hooks/useChat'
import { useLanguage } from '@/hooks/useLanguage'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import SuggestedQuestions from './SuggestedQuestions'

export default function ChatInterface() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const messagesRegionId = useId()
  const { language } = useLanguage()
  const { messages, isLoading, sendMessage, suggestions } = useChat()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Announce new messages to screen readers
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      if (lastMessage.role === 'assistant') {
        // The aria-live region will automatically announce this
      }
    }
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const message = input.trim()
    setInput('')
    await sendMessage(message, language)
  }

  const handleSuggestionClick = async (question: string) => {
    await sendMessage(question, language)
  }

  return (
    <div
      className="flex flex-col h-[calc(100vh-140px)] bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
      role="region"
      aria-label="Chat conversation"
    >
      {/* Messages Area */}
      <div
        id={messagesRegionId}
        className="flex-1 overflow-y-auto p-4 space-y-4"
        role="log"
        aria-live="polite"
        aria-atomic="false"
        aria-relevant="additions"
        tabIndex={0}
      >
        {messages.length === 0 ? (
          <WelcomeMessage onSuggestionClick={handleSuggestionClick} />
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && !isLoading && (
        <SuggestedQuestions
          questions={suggestions}
          onSelect={handleSuggestionClick}
        />
      )}

      {/* Input Area */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-gray-200 p-4"
        role="form"
        aria-label="Send a message"
      >
        <div className="flex gap-2">
          <label htmlFor="chat-input" className="sr-only">
            Type your question
          </label>
          <input
            id="chat-input"
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question in any language..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
            aria-describedby="language-support"
            autoComplete="off"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            aria-label={isLoading ? 'Sending message...' : 'Send message'}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
            ) : (
              <Send className="w-5 h-5" aria-hidden="true" />
            )}
          </button>
        </div>
        <p id="language-support" className="text-xs text-gray-400 mt-2 text-center">
          Supports: English, Hindi, Gujarati, Marathi, Punjabi, Tamil, Rajasthani
        </p>
      </form>
    </div>
  )
}

function WelcomeMessage({
  onSuggestionClick,
}: {
  onSuggestionClick: (q: string) => void
}) {
  const quickQuestions = [
    'What is the fee structure?',
    'Admission last date kya hai?',
    'Scholarship ke liye kaise apply karein?',
    'Hostel facility ke baare mein batao',
    'Exam schedule kab aayega?',
  ]

  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="bg-primary-100 text-primary-700 p-4 rounded-full mb-4" aria-hidden="true">
        <svg
          className="w-12 h-12"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Welcome to Campus Assistant!
      </h2>
      <p className="text-gray-600 mb-6 max-w-md">
        I can help you with admission queries, fee information, exam schedules,
        hostel facilities, and more. Ask me anything in your preferred language!
      </p>

      <nav className="w-full max-w-lg" aria-label="Quick questions">
        <p className="text-sm text-gray-500 mb-3" id="quick-questions-label">Try asking:</p>
        <div
          className="flex flex-wrap gap-2 justify-center"
          role="group"
          aria-labelledby="quick-questions-label"
        >
          {quickQuestions.map((question, index) => (
            <button
              key={index}
              onClick={() => onSuggestionClick(question)}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1"
            >
              {question}
            </button>
          ))}
        </div>
      </nav>
    </div>
  )
}
