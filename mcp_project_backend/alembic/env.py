from mcp.core.config import settings
from mcp.db.base import metadata as target_metadata  # Use metadata directly
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Ensure the app directory is in the Python path
# This allows Alembic to find your models and configuration
# Adjust the path as necessary if your alembic.ini is not in mcp_project_backend/
# or if you run alembic from a different directory.
PROJECT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_DIR)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your Base and models here
# The metadata object from your Base is used for autogenerate support.
from mcp.db.models import *  # noqa: F401, F403 Ensure all models are imported

# Import application settings to get DATABASE_URL


def get_url():
    """Return the database URL from application settings."""
    db_url = settings.DATABASE_URL
    if not db_url:
        raise ValueError(
            "DATABASE_URL is not set in the application configuration.")
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Include naming convention for offline mode if needed by your DB
        # or if you want consistent DDL generation for review
        render_as_batch=True,  # Useful for SQLite, may be needed for other DBs for certain ops
        compare_type=True,  # Recommended for detecting type changes
        include_schemas=True,  # If you use schemas
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the sqlalchemy.url from our settings
    db_url = get_url()

    # Create a new dictionary for engine_from_config to avoid modifying the original config object
    engine_config_dict = config.get_section(
        config.config_ini_section) if config.config_ini_section else {}
    engine_config_dict["sqlalchemy.url"] = db_url

    connectable = engine_from_config(
        engine_config_dict,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Useful for SQLite and some complex ALTERs in other DBs
            compare_type=True,    # Detect column type changes
            include_schemas=True,  # If you use schemas other than default
            # Pass the naming convention to the context if not already on MetaData
            # This is usually handled if metadata has naming_convention set
            # naming_convention=target_metadata.naming_convention
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
