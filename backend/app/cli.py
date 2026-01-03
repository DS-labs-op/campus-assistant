"""
Command-line interface for Campus Assistant management.

Provides utilities for:
- Password hashing for admin setup
- Database initialization
- FAQ import/export
- System health checks
"""

import argparse
import getpass
import sys


def hash_password_command(args: argparse.Namespace) -> int:
    """Generate bcrypt hash for a password."""
    from app.core.security import get_password_hash

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter password to hash: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Error: Passwords do not match", file=sys.stderr)
            return 1

    if len(password) < 8:
        print("Error: Password must be at least 8 characters", file=sys.stderr)
        return 1

    hashed = get_password_hash(password)
    print("\nGenerated password hash:")
    print(f"ADMIN_PASSWORD_HASH={hashed}")
    print("\nAdd this to your .env file or environment variables.")
    return 0


def generate_secret_key_command(args: argparse.Namespace) -> int:
    """Generate a secure secret key."""
    from app.core.security import generate_secure_token

    secret = generate_secure_token(32)
    print("\nGenerated secret key:")
    print(f"SECRET_KEY={secret}")
    print("\nAdd this to your .env file or environment variables.")
    return 0


def check_config_command(args: argparse.Namespace) -> int:
    """Check configuration for common issues."""
    import warnings

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from app.core.config import get_settings
        settings = get_settings()

    print("Configuration Check")
    print("=" * 50)

    issues = []
    warnings_list = [str(warning.message) for warning in w]

    # Check secret key
    if settings.secret_key.get_secret_value() == "CHANGE-THIS-IN-PRODUCTION-USE-SECURE-KEY":
        issues.append("SECRET_KEY is using default value")

    # Check admin password
    if not settings.admin_password_hash:
        issues.append("ADMIN_PASSWORD_HASH is not set")

    # Check database
    if "sqlite" in settings.database_url and settings.is_production:
        issues.append("Using SQLite in production (should use PostgreSQL)")

    # Check LLM API key
    if settings.llm_provider == "gemini" and not settings.google_api_key:
        issues.append("GOOGLE_API_KEY is not set but LLM_PROVIDER is 'gemini'")
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        issues.append("OPENAI_API_KEY is not set but LLM_PROVIDER is 'openai'")

    # Print results
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}")
    print(f"LLM Provider: {settings.llm_provider}")
    print()

    if issues:
        print("Issues Found:")
        for issue in issues:
            print(f"  ❌ {issue}")
        print()
        return 1 if settings.is_production else 0
    else:
        print("✅ No issues found")
        return 0


def init_db_command(args: argparse.Namespace) -> int:
    """Initialize the database."""
    import asyncio
    from app.core.database import init_db

    async def run():
        print("Initializing database...")
        await init_db()
        print("✅ Database initialized successfully")

    asyncio.run(run())
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Campus Assistant CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # hash-password command
    hash_parser = subparsers.add_parser(
        "hash-password",
        help="Generate bcrypt hash for admin password"
    )
    hash_parser.add_argument(
        "--password", "-p",
        help="Password to hash (will prompt if not provided)"
    )

    # generate-secret command
    secret_parser = subparsers.add_parser(
        "generate-secret",
        help="Generate a secure secret key"
    )

    # check-config command
    config_parser = subparsers.add_parser(
        "check-config",
        help="Check configuration for issues"
    )

    # init-db command
    initdb_parser = subparsers.add_parser(
        "init-db",
        help="Initialize the database"
    )

    args = parser.parse_args()

    if args.command == "hash-password":
        return hash_password_command(args)
    elif args.command == "generate-secret":
        return generate_secret_key_command(args)
    elif args.command == "check-config":
        return check_config_command(args)
    elif args.command == "init-db":
        return init_db_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
