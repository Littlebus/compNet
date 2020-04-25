"""update unit

Revision ID: 09a5179a86fd
Revises: 96bb223a8d3d
Create Date: 2020-04-25 16:59:29.426448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09a5179a86fd'
down_revision = '96bb223a8d3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('unit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('BMI', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('gender', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('height', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('weight', sa.Float(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'role', ['role_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('unit', schema=None) as batch_op:
        batch_op.drop_column('weight')
        batch_op.drop_column('height')
        batch_op.drop_column('gender')
        batch_op.drop_column('BMI')

    # ### end Alembic commands ###