"""empty message

Revision ID: 60b246fd45df
Revises: 3c43178e4e80
Create Date: 2024-10-22 15:18:01.256970

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '60b246fd45df'
down_revision = '3c43178e4e80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_index('order_reference')
        batch_op.drop_column('order_reference')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order_reference', mysql.VARCHAR(length=255), nullable=True))
        batch_op.create_index('order_reference', ['order_reference'], unique=True)

    # ### end Alembic commands ###
