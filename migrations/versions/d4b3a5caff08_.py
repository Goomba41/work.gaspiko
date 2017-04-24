"""empty message

Revision ID: d4b3a5caff08
Revises: 
Create Date: 2017-04-24 11:26:06.897540

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd4b3a5caff08'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('migrate_version')
    op.create_unique_constraint(None, 'user', ['login'])
    op.create_unique_constraint(None, 'user', ['email'])
    op.create_unique_constraint(None, 'user', ['password'])
    op.create_unique_constraint(None, 'user', ['phone'])
    op.create_foreign_key(None, 'user', 'post', ['post_id'], ['id'])
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    op.create_foreign_key(None, 'user', 'department', ['department_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.create_table('migrate_version',
    sa.Column('repository_id', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=250), nullable=False),
    sa.Column('repository_path', mysql.MEDIUMTEXT(collation=u'utf8mb4_unicode_ci'), nullable=True),
    sa.Column('version', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('repository_id'),
    mysql_collate=u'utf8mb4_unicode_ci',
    mysql_default_charset=u'utf8mb4',
    mysql_engine=u'InnoDB'
    )
    # ### end Alembic commands ###
