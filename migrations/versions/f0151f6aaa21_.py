"""empty message

Revision ID: f0151f6aaa21
Revises: 
Create Date: 2017-12-18 22:04:32.169029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0151f6aaa21'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('foreign_contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('channel', sa.String(), nullable=False),
    sa.Column('contact', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('lat', sa.Float(), nullable=True),
    sa.Column('lng', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('contact_phone', sa.String(), nullable=True),
    sa.Column('blood_type', sa.String(), nullable=False),
    sa.Column('rhesus', sa.String(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('lat', sa.Float(), nullable=True),
    sa.Column('lng', sa.Float(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('is_fulfilled', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('contact_phone', sa.String(), nullable=False),
    sa.Column('blood_type', sa.String(), nullable=True),
    sa.Column('rhesus', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('lat', sa.Float(), nullable=True),
    sa.Column('lng', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('contact_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('request', sa.Integer(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=True),
    sa.Column('foreign_contact', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['foreign_contact'], ['foreign_contacts.id'], ),
    sa.ForeignKeyConstraint(['request'], ['requests.id'], ),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contact_logs')
    op.drop_table('users')
    op.drop_table('requests')
    op.drop_table('foreign_contacts')
    # ### end Alembic commands ###
