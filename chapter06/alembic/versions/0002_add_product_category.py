from alembic import op
import sqlalchemy as sa


revision = "0002_add_product_category"
down_revision = "0001_create_products"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "products",
        sa.Column("category", sa.String(length=80), nullable=False, server_default="general"),
    )


def downgrade():
    op.drop_column("products", "category")
