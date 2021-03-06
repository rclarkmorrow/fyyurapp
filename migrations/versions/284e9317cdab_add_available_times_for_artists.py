"""Add available times for artists.

Revision ID: 284e9317cdab
Revises: 0cefe8e3aa0c
Create Date: 2020-04-29 19:58:33.980733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '284e9317cdab'
down_revision = '0cefe8e3aa0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('available_end', sa.DateTime(), nullable=True))
    op.add_column('Artist', sa.Column('available_start', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'available_start')
    op.drop_column('Artist', 'available_end')
    # ### end Alembic commands ###
