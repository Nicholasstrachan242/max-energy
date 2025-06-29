"""add is_active_flag to User model

Revision ID: 459abfc07beb
Revises: 381e254f7905
Create Date: 2025-06-24 15:32:17.021042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '459abfc07beb'
down_revision = '381e254f7905'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active_flag', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_active_flag')

    # ### end Alembic commands ###
