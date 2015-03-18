"""rename name to code; rename en_name to name

Revision ID: eba8a2a2c31
Revises: 3f72c5bf02e3
Create Date: 2015-03-18 16:25:10.405611

"""

# revision identifiers, used by Alembic.
revision = 'eba8a2a2c31'
down_revision = '3f72c5bf02e3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    table_names = ['departments', 'idcs', 'projects', 'roles']
    def change_table(table_name):
        #op.drop_constraint(u'name', table_name, u'unique')
        #op.drop_constraint(u'en_name', table_name, u'unique')
        op.alter_column(table_name, "name", new_column_name='code', existing_type=sa.String(64))
        op.alter_column(table_name, "en_name", new_column_name='name', existing_type=sa.String(64))
        op.create_unique_constraint(None, table_name, ['code'])
        op.create_unique_constraint(None, table_name, ['name'])

    map(change_table, table_names)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    table_names = ['departments', 'idcs', 'projects', 'roles']
    def change_table(table_name):
        op.drop_constraint(u'code', table_name)
        op.drop_constraint(u'name', table_name)
        op.alter_column(table_name, "name", new_column_name='en_name', existing_type=sa.String(64))
        op.alter_column(table_name, "code", new_column_name='name', existing_type=sa.String(64))
        op.create_unique_constraint(None, table_name, ['en_name'])
        op.create_unique_constraint(None, table_name, ['name'])

    map(change_table, table_names)
    ### end Alembic commands ###