"""add employee_id

Revision ID: 9387d8c8cd50
Revises: 459abfc07beb
Create Date: 2025-06-26 14:23:14.087635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9387d8c8cd50'
down_revision = '459abfc07beb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('employee_id', sa.Integer(), autoincrement=True, nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('employee_id')

    # ### end Alembic commands ###
