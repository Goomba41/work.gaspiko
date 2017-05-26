"""empty message

Revision ID: 019339ada220
Revises: 0d1ea8f79019
Create Date: 2017-05-05 15:22:35.631263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '019339ada220'
down_revision = '0d1ea8f79019'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('module', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['module'], ['module.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('table')
    # ### end Alembic commands ###