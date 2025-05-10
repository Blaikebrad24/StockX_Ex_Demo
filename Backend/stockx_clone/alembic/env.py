from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.models import Base  # This is your declarative base
import app.models.users  # Import all models to register them with Base
import app.models.product