"""empty message

Revision ID: 76fadd6278c4
Revises: 3af2d99b8146
Create Date: 2020-02-03 12:19:10.066365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76fadd6278c4'
down_revision = '3af2d99b8146'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('artists', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('shows', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.add_column('venues', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'website')
    op.drop_column('venues', 'seeking_description')
    op.drop_column('shows', 'start_time')
    op.drop_column('artists', 'website')
    op.drop_column('artists', 'seeking_description')
    # ### end Alembic commands ###