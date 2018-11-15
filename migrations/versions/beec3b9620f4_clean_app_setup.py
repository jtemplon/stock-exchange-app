"""clean app setup

Revision ID: beec3b9620f4
Revises: 
Create Date: 2018-11-13 09:10:09.576304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'beec3b9620f4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock',
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('cash', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('holding',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('stock', sa.String(length=120), nullable=True),
    sa.Column('shares', sa.Integer(), nullable=True),
    sa.Column('purchase_price', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['stock'], ['stock.name'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('shares', sa.Integer(), nullable=True),
    sa.Column('team', sa.String(length=120), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('buy_or_sell', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_timestamp'), 'transaction', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_timestamp'), table_name='transaction')
    op.drop_table('transaction')
    op.drop_table('holding')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('stock')
    # ### end Alembic commands ###