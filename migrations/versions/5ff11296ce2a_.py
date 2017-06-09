"""empty message

Revision ID: 5ff11296ce2a
Revises: 515b63b3bd6d
Create Date: 2017-06-09 11:04:36.302871

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5ff11296ce2a'
down_revision = '515b63b3bd6d'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'appeals_ibfk_1', 'appeals', type_='foreignkey')
    op.create_foreign_key(None, 'appeals', 'user', ['author'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.drop_constraint(u'history_ibfk_2', 'history', type_='foreignkey')
    op.drop_constraint(u'history_ibfk_1', 'history', type_='foreignkey')
    op.create_foreign_key(None, 'history', 'table', ['table'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.create_foreign_key(None, 'history', 'user', ['user_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.drop_constraint(u'important_news_ibfk_1', 'important_news', type_='foreignkey')
    op.create_foreign_key(None, 'important_news', 'user', ['author'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.drop_constraint(u'news_ibfk_1', 'news', type_='foreignkey')
    op.create_foreign_key(None, 'news', 'user', ['user_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.drop_constraint(u'permission_ibfk_2', 'permission', type_='foreignkey')
    op.drop_constraint(u'permission_ibfk_3', 'permission', type_='foreignkey')
    op.drop_constraint(u'permission_ibfk_1', 'permission', type_='foreignkey')
    op.create_foreign_key(None, 'permission', 'table', ['table_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.create_foreign_key(None, 'permission', 'role', ['role_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.create_foreign_key(None, 'permission', 'user', ['user_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.drop_constraint(u'table_ibfk_1', 'table', type_='foreignkey')
    op.create_foreign_key(None, 'table', 'module', ['module'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.drop_constraint(u'user_ibfk_1', 'user', type_='foreignkey')
    op.drop_constraint(u'user_ibfk_2', 'user', type_='foreignkey')
    op.drop_constraint(u'user_ibfk_3', 'user', type_='foreignkey')
    op.create_foreign_key(None, 'user', 'post', ['post_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    op.create_foreign_key(None, 'user', 'department', ['department_id'], ['id'], source_schema='arhiv', referent_schema='arhiv')
    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', schema='arhiv', type_='foreignkey')
    op.drop_constraint(None, 'user', schema='arhiv', type_='foreignkey')
    op.drop_constraint(None, 'user', schema='arhiv', type_='foreignkey')
    op.create_foreign_key(u'user_ibfk_3', 'user', 'department', ['department_id'], ['id'])
    op.create_foreign_key(u'user_ibfk_2', 'user', 'role', ['role_id'], ['id'])
    op.create_foreign_key(u'user_ibfk_1', 'user', 'post', ['post_id'], ['id'])
    op.drop_constraint(None, 'table', schema='arhiv', type_='foreignkey')
    op.create_foreign_key(u'table_ibfk_1', 'table', 'module', ['module'], ['id'])
    op.drop_constraint(None, 'permission', schema='arhiv', type_='foreignkey')
    op.drop_constraint(None, 'permission', schema='arhiv', type_='foreignkey')
    op.drop_constraint(None, 'permission', schema='arhiv', type_='foreignkey')
    op.create_foreign_key(u'permission_ibfk_1', 'permission', 'table', ['table_id'], ['id'])
    op.create_foreign_key(u'permission_ibfk_3', 'permission', 'user', ['user_id'], ['id'])
    op.create_foreign_key(u'permission_ibfk_2', 'permission', 'role', ['role_id'], ['id'])
    op.drop_constraint(None, 'news', schema='arhiv', type_='foreignkey')
    op.create_foreign_key(u'news_ibfk_1', 'news', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'important_news', schema='arhiv', type_='foreignkey')
    op.create_foreign_key(u'important_news_ibfk_1', 'important_news', 'user', ['author'], ['id'])
    op.drop_constraint(None, 'history', schema='arhiv', type_='foreignkey')
    op.drop_constraint(None, 'history', schema='arhiv', type_='foreignkey')
    op.create_foreign_key(u'history_ibfk_1', 'history', 'table', ['table'], ['id'])
    op.create_foreign_key(u'history_ibfk_2', 'history', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'appeals', schema='arhiv', type_='foreignkey')
    op.create_foreign_key(u'appeals_ibfk_1', 'appeals', 'user', ['author'], ['id'])
    # ### end Alembic commands ###


def upgrade_kartoteka():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('request', sa.Column('date_done', sa.Date(), nullable=True))
    op.add_column('request', sa.Column('date_send', sa.Date(), nullable=True))
    op.add_column('request', sa.Column('executor_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'request_ibfk_2', 'request', type_='foreignkey')
    op.drop_constraint(u'request_ibfk_1', 'request', type_='foreignkey')
    op.create_foreign_key(None, 'request', 'character', ['character_id'], ['id'], referent_schema='kartoteka')
    op.create_foreign_key(None, 'request', 'executor', ['executor_id'], ['id'], referent_schema='kartoteka')
    op.create_foreign_key(None, 'request', 'kind', ['kind_id'], ['id'], referent_schema='kartoteka')
    # ### end Alembic commands ###


def downgrade_kartoteka():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'request', type_='foreignkey')
    op.drop_constraint(None, 'request', type_='foreignkey')
    op.drop_constraint(None, 'request', type_='foreignkey')
    op.create_foreign_key(u'request_ibfk_1', 'request', 'character', ['character_id'], ['id'])
    op.create_foreign_key(u'request_ibfk_2', 'request', 'kind', ['kind_id'], ['id'])
    op.drop_column('request', 'executor_id')
    op.drop_column('request', 'date_send')
    op.drop_column('request', 'date_done')
    op.add_column('executor', sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.create_foreign_key(u'executor_ibfk_1', 'executor', 'user', ['user_id'], ['id'], referent_schema='arhiv')
    op.create_index('user_id', 'executor', ['user_id'], unique=True)
    # ### end Alembic commands ###

