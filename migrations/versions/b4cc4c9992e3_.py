"""empty message

Revision ID: b4cc4c9992e3
Revises: 
Create Date: 2021-02-10 10:41:31.283297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4cc4c9992e3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bank', sa.String(length=64), nullable=True),
    sa.Column('account_n', sa.String(length=120), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('detail', sa.String(length=128), nullable=True),
    sa.Column('flow', sa.Integer(), nullable=True),
    sa.Column('bal', sa.Integer(), nullable=True),
    sa.Column('tag', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_account_account_n'), 'account', ['account_n'], unique=False)
    op.create_index(op.f('ix_account_bal'), 'account', ['bal'], unique=False)
    op.create_index(op.f('ix_account_flow'), 'account', ['flow'], unique=False)
    op.create_index(op.f('ix_account_tag'), 'account', ['tag'], unique=False)
    op.create_index(op.f('ix_account_timestamp'), 'account', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_account_timestamp'), table_name='account')
    op.drop_index(op.f('ix_account_tag'), table_name='account')
    op.drop_index(op.f('ix_account_flow'), table_name='account')
    op.drop_index(op.f('ix_account_bal'), table_name='account')
    op.drop_index(op.f('ix_account_account_n'), table_name='account')
    op.drop_table('account')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
