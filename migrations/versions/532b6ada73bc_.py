"""empty message

Revision ID: 532b6ada73bc
Revises: 019339ada220
Create Date: 2017-05-05 15:33:01.780650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '532b6ada73bc'
down_revision = '019339ada220'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('cdate', sa.DateTime(), nullable=True),
    sa.Column('action', sa.String(length=50), nullable=True),
    sa.Column('table', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['table'], ['table.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('history')
    # ### end Alembic commands ###