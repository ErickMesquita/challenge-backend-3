"""empty message

Revision ID: a93d7b16900c
Revises: 1c1dea1db0c2
Create Date: 2022-04-28 11:53:56.982297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a93d7b16900c'
down_revision = '1c1dea1db0c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DELETE FROM "transaction";')
    op.execute('DELETE FROM "transactions_file";')
    op.create_unique_constraint(None, 'transactions_file', ['csv_filepath'])
    op.create_unique_constraint(None, 'transactions_file', ['transactions_date'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions_file', type_='unique')
    op.drop_constraint(None, 'transactions_file', type_='unique')
    # ### end Alembic commands ###
