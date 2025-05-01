import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import Base
from app.models import (
    users, product,sales
   
)

target_metadata = Base.metadata
