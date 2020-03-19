"""role-permission

Revision ID: 02245d1a703c
Revises: 143b85fa9175
Create Date: 2020-03-15 23:25:32.961752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02245d1a703c'
down_revision = '143b85fa9175'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles_permissions',
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('permission_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], )
    )
    op.create_table('unit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('comment', sa.String(length=140), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unit_timestamp'), 'unit', ['timestamp'], unique=False)
    op.drop_table('roles_permission')
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.create_table('roles_permission',
    sa.Column('role_id', sa.INTEGER(), nullable=True),
    sa.Column('permission_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], )
    )
    op.drop_index(op.f('ix_unit_timestamp'), table_name='unit')
    op.drop_table('unit')
    op.drop_table('roles_permissions')
    # ### end Alembic commands ###
