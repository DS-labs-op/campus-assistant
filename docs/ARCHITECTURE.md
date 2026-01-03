# Campus Assistant Architecture

## Overview

Campus Assistant is a multilingual chatbot application for educational institutions. It consists of a FastAPI backend and a Next.js frontend, with PostgreSQL for persistence and ChromaDB for vector search.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer                             │
│                    (Nginx/Cloud LB)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────┐                           ┌───────────────┐
│   Frontend    │                           │   Backend     │
│   (Next.js)   │◄─────── REST API ────────►│   (FastAPI)   │
│   Port 3000   │                           │   Port 8000   │
└───────────────┘                           └───────────────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────────────────┐
                    ▼                               ▼                               ▼
            ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
            │  PostgreSQL   │               │   ChromaDB    │               │  Google AI    │
            │   (Primary)   │               │ (Vector Store)│               │   (Gemini)    │
            │   Port 5432   │               │   (Embedded)  │               │    (LLM)      │
            └───────────────┘               └───────────────┘               └───────────────┘
```

## Components

### Backend (FastAPI)

**Location:** `backend/`

**Key Modules:**
- `app/main.py` - Application entry point, middleware, health endpoints
- `app/core/config.py` - Pydantic settings with validation
- `app/core/database.py` - Async SQLAlchemy with PostgreSQL
- `app/core/security.py` - bcrypt password hashing, JWT tokens
- `app/api/routes/` - API route handlers
- `app/services/` - Business logic (chat, RAG, translation)

**API Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Liveness probe |
| `/ready` | GET | Readiness probe (DB check) |
| `/metrics` | GET | Prometheus metrics |
| `/api/v1/chat` | POST | Send chat message |
| `/api/v1/faqs` | CRUD | FAQ management |
| `/api/v1/documents` | CRUD | Document upload/indexing |
| `/api/v1/admin/*` | Various | Admin dashboard |
| `/api/v1/telegram/*` | POST | Telegram webhook |

### Frontend (Next.js)

**Location:** `frontend/`

**Key Components:**
- `src/components/ChatWidget.tsx` - Floating chat widget
- `src/components/ChatInterface.tsx` - Chat conversation UI
- `src/hooks/useChat.ts` - Chat state management
- `src/lib/api.ts` - API client

### Database Schema

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   users     │     │  sessions   │     │  messages   │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │◄────│ user_id(FK) │◄────│ session_id  │
│ external_id │     │ session_id  │     │ role        │
│ platform    │     │ language    │     │ content     │
│ created_at  │     │ context     │     │ intent      │
└─────────────┘     └─────────────┘     └─────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    faqs     │     │  documents  │     │ escalations │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ question    │     │ filename    │     │ session_id  │
│ answer      │     │ file_path   │     │ reason      │
│ category    │     │ is_indexed  │     │ status      │
│ keywords    │     │ chunk_count │     │ assigned_to │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Data Flow

### Chat Message Flow

```
1. User sends message via ChatInterface
2. Frontend POST /api/v1/chat with message + session_id
3. Backend:
   a. Detect language (IndicNLP/langdetect)
   b. Translate to English if needed
   c. Query ChromaDB for relevant context
   d. Build prompt with context + history
   e. Call Gemini API for response
   f. Translate response back if needed
   g. Store message in PostgreSQL
4. Return response to frontend
5. Frontend displays response in ChatInterface
```

### Document Indexing Flow

```
1. Admin uploads document via /api/v1/documents
2. Backend:
   a. Save file to disk
   b. Extract text (PyPDF2/python-docx)
   c. Chunk text into segments
   d. Generate embeddings
   e. Store in ChromaDB
   f. Update document.is_indexed = true
3. Document available for RAG queries
```

## Security

### Authentication
- **Admin Panel:** HTTP Basic Auth with bcrypt-hashed passwords
- **API:** Optional API key authentication
- **Tokens:** JWT with HS256 signing

### Environment Secrets
All secrets use `SecretStr` in Pydantic:
- `SECRET_KEY` - JWT signing key
- `ADMIN_PASSWORD_HASH` - bcrypt hash
- `GOOGLE_API_KEY` - Gemini API key
- `DATABASE_URL` - PostgreSQL connection

### Rate Limiting
- Configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW`
- Per-IP rate limiting using slowapi

## Observability

### Metrics (Prometheus)
- `http_requests_total` - Request counter by method/endpoint/status
- `http_request_duration_seconds` - Request latency histogram
- `chat_messages_total` - Chat messages by language/intent

### Logging
- Structured JSON logging (loguru)
- Request ID tracing via `X-Request-ID` header
- Log levels: DEBUG, INFO, WARNING, ERROR

### Error Tracking
- Sentry integration (optional)
- Automatic error capture with context

## Deployment

### Docker Compose (Development)
```bash
docker-compose up --build
```

### Production Deployment
1. Set all environment variables
2. Run database migrations: `alembic upgrade head`
3. Deploy via Docker or cloud platform
4. Configure reverse proxy (nginx)
5. Set up SSL termination

### Environment Variables
See `backend/.env.example` for full list.

## Testing

### Backend
```bash
cd backend
pytest --cov=app tests/
```

### Frontend
```bash
cd frontend
npm test
```

### Integration
```bash
docker-compose -f docker-compose.yml -f docker-compose.test.yml up
```

## Scaling Considerations

1. **Horizontal Scaling:** Backend is stateless, scale via container replicas
2. **Database:** Use connection pooling, consider read replicas
3. **Vector Store:** ChromaDB is embedded; for scale, use Pinecone/Weaviate
4. **Caching:** Add Redis for session/response caching
5. **CDN:** Serve frontend via CDN for global distribution
