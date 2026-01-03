# Changelog

All notable changes to Campus Assistant are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Security
- **bcrypt password hashing** - Replaced plaintext admin password with bcrypt hashing via passlib
- **SecretStr for secrets** - All sensitive configuration values now use Pydantic SecretStr
- **CLI password tool** - Added `python -m app.cli hash-password` for generating secure password hashes
- **JWT token management** - Secure token generation and validation with python-jose

#### Database
- **PostgreSQL support** - Migrated from SQLite to PostgreSQL with asyncpg driver
- **Alembic migrations** - Added database migration framework with initial schema
- **Async database sessions** - Full async/await support for database operations

#### Observability
- **Prometheus metrics** - Added `/metrics` endpoint with request counters and latency histograms
- **Structured JSON logging** - Production-ready logging with loguru
- **Request ID tracing** - Every request gets a unique ID in `X-Request-ID` header
- **Sentry integration** - Optional error tracking with Sentry SDK
- **Health endpoints** - Added `/health` (liveness) and `/ready` (readiness) probes

#### Testing
- **pytest test suite** - Backend unit tests with pytest-asyncio and httpx
- **Jest test suite** - Frontend component tests with React Testing Library
- **Test configuration** - Added pyproject.toml with pytest, ruff, and mypy settings
- **Mock fixtures** - Comprehensive test fixtures for database and API testing

#### DevOps
- **GitHub Actions CI/CD** - Automated linting, testing, and Docker builds
- **Pre-commit hooks** - Code quality checks with ruff, black, isort, bandit, prettier
- **Multi-stage Docker builds** - Optimized images with non-root users
- **Docker Compose production config** - Named volumes, health checks, proper networking

#### Accessibility
- **ARIA labels and roles** - Screen reader support for chat components
- **Keyboard navigation** - Escape to close, focus management
- **Focus indicators** - Visible focus rings on all interactive elements
- **Semantic HTML** - Proper use of header, nav, dialog roles

#### Documentation
- **Architecture documentation** - System design, data flow, and component overview
- **Operations runbook** - Troubleshooting, scaling, and incident response procedures
- **API documentation** - Enhanced OpenAPI schema with descriptions

### Changed

#### Configuration
- **Pydantic Settings v2** - Upgraded to modern pydantic-settings with validators
- **Environment-based config** - All configuration via environment variables
- **Secure defaults** - Warnings for insecure default values in development

#### Docker
- **Next.js standalone mode** - Changed from `export` to `standalone` for Docker compatibility
- **Non-root users** - Containers run as non-privileged users
- **Health checks** - Container orchestration support with proper health checks

#### Dependencies
- **Pinned versions** - All Python and Node.js dependencies pinned to specific versions
- **Dev dependencies** - Separated development dependencies (pytest, black, etc.)
- **Security updates** - Updated all dependencies to latest secure versions

### Fixed

- **Docker build failures** - Fixed Next.js static export incompatibility
- **Rate limiting** - Proper rate limit error handling with retry information
- **CORS configuration** - Dynamic CORS origins from environment
- **Database connections** - Async connection pool with proper cleanup

### Security

- **OWASP compliance** - Addressed common vulnerabilities
- **Secret management** - No secrets in code or version control
- **Input validation** - Pydantic models for all API inputs
- **SQL injection prevention** - Parameterized queries via SQLAlchemy ORM

### Removed

- **Hardcoded credentials** - Removed `admin/admin123` default
- **SQLite dependency** - Removed embedded SQLite in favor of PostgreSQL
- **Unused exports** - Cleaned up unused code and dead exports

## [0.1.0] - Initial Release

### Added
- Basic chat interface with multilingual support
- FAQ management system
- Document upload and indexing
- Admin dashboard
- Telegram bot integration
- Web widget for embedding
