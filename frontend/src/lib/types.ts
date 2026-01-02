export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  detectedLanguage?: string
  responseLanguage?: string
  intent?: string
  confidence?: number
  sources?: Source[]
  needsEscalation?: boolean
}

export interface Source {
  title: string
  content: string
  score: number
}

export interface ChatResponse {
  session_id: string
  response: string
  detected_language: string
  response_language: string
  intent: string | null
  confidence: number
  sources: Array<{
    title: string
    content: string
    score: number
  }>
  needs_escalation: boolean
  suggested_questions: string[]
}

export interface DashboardStats {
  sessions: { total: number; active_24h: number }
  messages: { total: number; today: number }
  escalations: { pending: number }
  knowledge_base: { faqs: number; documents: number; vector_chunks: number }
  performance: { avg_confidence_7d: number }
}
