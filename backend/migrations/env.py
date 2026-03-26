"""Alembic environment configuration for Scrounger."""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our database configuration
from src.config import settings
from src.database import Base

# Import all models so they are registered with Base.metadata
# This is required for Alembic autogenerate to detect all tables

# Core models
from src.models.item import Item
from src.models.lead import Lead
from src.models.sale import Sale, sale_items
from src.models.setting import UserSetting, AIModel
from src.models.reddit_message import RedditMessage

# Organization models
from src.models.category import Category
from src.models.tag import Tag, item_tags
from src.models.value_factor import ValueFactor, item_value_factors

# Image models
from src.models.item_image import ItemImage

# Message models
from src.models.lead_message import LeadMessage, MessageAttachment

# Marketplace models
from src.models.marketplace import Marketplace, MarketplaceRule, MarketplaceAIPrompt

# Action system
from src.models.action import Action

# Dispute model
from src.models.dispute import Dispute

# Junction tables
from src.models.lead_item import lead_items


# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite ALTER TABLE support
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Handle SQLite connection args
    connect_args = {}
    if "sqlite" in settings.database_url:
        connect_args = {"check_same_thread": False}

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite ALTER TABLE support
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
