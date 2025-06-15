from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import mapped_column

user_id = Annotated[int, mapped_column(primary_key=True, unique=True, nullable=False)]
created_at = Annotated[datetime, mapped_column(default=datetime.utcnow)]