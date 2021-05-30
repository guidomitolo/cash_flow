"""empty message

Revision ID: d70e775253da
Revises: e9ad861c35e0
Create Date: 2021-05-28 17:21:27.097028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd70e775253da'
down_revision = 'e9ad861c35e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('credit', sa.Column('tag', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_credit_tag'), 'credit', ['tag'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_credit_tag'), table_name='credit')
    op.drop_column('credit', 'tag')
    # ### end Alembic commands ###