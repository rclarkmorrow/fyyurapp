"""Normalized Venue table

Revision ID: 7be7e06ac500
Revises: ad17e495302a
Create Date: 2020-04-10 20:15:09.341456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7be7e06ac500'
down_revision = 'ad17e495302a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), server_default='f', nullable=False))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.alter_column('Venue', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               type_=sa.String(120),
               nullable=False)
    op.create_unique_constraint(None, 'Venue', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Venue_name_key', 'Venue', type_='unique')
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('Venue', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
