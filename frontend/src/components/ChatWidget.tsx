'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { MessageCircle, X, Minimize2 } from 'lucide-react'
import ChatInterface from './ChatInterface'

interface ChatWidgetProps {
  position?: 'bottom-right' | 'bottom-left'
  primaryColor?: string
}

export default function ChatWidget({
  position = 'bottom-right',
  primaryColor = '#2563eb',
}: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const dialogRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)

  const positionClasses =
    position === 'bottom-right' ? 'right-4 bottom-4' : 'left-4 bottom-4'

  // Handle escape key to close the chat
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape' && isOpen) {
      setIsOpen(false)
      triggerRef.current?.focus()
    }
  }, [isOpen])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  // Focus management when opening/closing
  useEffect(() => {
    if (isOpen && dialogRef.current) {
      const firstFocusable = dialogRef.current.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      firstFocusable?.focus()
    }
  }, [isOpen])

  if (!isOpen) {
    return (
      <button
        ref={triggerRef}
        onClick={() => setIsOpen(true)}
        className={`fixed ${positionClasses} z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
        style={{ backgroundColor: primaryColor }}
        aria-label="Open chat assistant"
        aria-haspopup="dialog"
        aria-expanded={isOpen}
      >
        <MessageCircle className="w-6 h-6 text-white" aria-hidden="true" />
      </button>
    )
  }

  return (
    <div
      ref={dialogRef}
      role="dialog"
      aria-label="Campus Assistant Chat"
      aria-modal="true"
      className={`fixed ${positionClasses} z-50 ${
        isMinimized ? 'w-72' : 'w-96 h-[600px]'
      } flex flex-col bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden transition-all`}
    >
      {/* Header */}
      <header
        className="flex items-center justify-between px-4 py-3 text-white"
        style={{ backgroundColor: primaryColor }}
      >
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5" aria-hidden="true" />
          <h2 className="font-semibold text-base" id="chat-title">Campus Assistant</h2>
        </div>
        <div className="flex items-center gap-1" role="group" aria-label="Chat window controls">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-white/20 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-white/50"
            aria-label={isMinimized ? 'Expand chat' : 'Minimize chat'}
            aria-pressed={isMinimized}
          >
            <Minimize2 className="w-4 h-4" aria-hidden="true" />
          </button>
          <button
            onClick={() => {
              setIsOpen(false)
              triggerRef.current?.focus()
            }}
            className="p-1 hover:bg-white/20 rounded transition-colors focus:outline-none focus:ring-2 focus:ring-white/50"
            aria-label="Close chat"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
      </header>

      {/* Chat Content */}
      {!isMinimized && (
        <div className="flex-1 overflow-hidden">
          <ChatInterface />
        </div>
      )}
    </div>
  )
}
