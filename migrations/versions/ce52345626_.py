"""empty message

Revision ID: ce52345626
Revises: 2a91060e7e61
Create Date: 2015-03-11 18:35:51.153095

"""

# revision identifiers, used by Alembic.
revision = 'ce52345626'
down_revision = '2a91060e7e61'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('keepaliveds', sa.Column('idc_id', sa.Integer(), nullable=True))
    op.add_column('keepaliveds', sa.Column('name', sa.String(length=64), nullable=True))
    op.create_unique_constraint(None, 'keepaliveds', ['name'])
    op.add_column('memcacheds', sa.Column('keepalived_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('memcacheds', 'keepalived_id')
    op.drop_constraint(None, 'keepaliveds')
    op.drop_column('keepaliveds', 'name')
    op.drop_column('keepaliveds', 'idc_id')
    ### end Alembic commands ###
