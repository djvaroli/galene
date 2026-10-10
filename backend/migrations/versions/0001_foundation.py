"""Establish the schema revision before inventory tables arrive."""

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    raise RuntimeError("Automated schema downgrades are not supported.")
