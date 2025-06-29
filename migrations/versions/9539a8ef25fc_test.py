"""test

Revision ID: 9539a8ef25fc
Revises: e270117010c1
Create Date: 2025-06-17 17:17:07.067148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9539a8ef25fc'
down_revision = 'e270117010c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email_hash', sa.String(length=200), nullable=False),
    sa.Column('email_encrypted', sa.LargeBinary(), nullable=False),
    sa.Column('password_hash', sa.String(length=200), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email_hash')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
