from alembic import context
from sqlalchemy import MetaData

# Concrete models are added with their owning features.
context.configure(connection=context.config.attributes["connection"], target_metadata=MetaData())
with context.begin_transaction():
    context.run_migrations()
