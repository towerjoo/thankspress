from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('password', String(length=32), nullable=False),
    Column('language', String(length=5), nullable=False),
    Column('status', SmallInteger, nullable=False),
    Column('date_registered', DateTime, nullable=False),
    Column('date_last_signed_in', DateTime),
    Column('date_last_acted', DateTime),
    Column('username', String(length=32)),
    Column('password_reset_key', String(length=32)),
    Column('password_reset_key_expiration_date', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['date_last_acted'].create()
    post_meta.tables['user'].columns['date_last_signed_in'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['date_last_acted'].drop()
    post_meta.tables['user'].columns['date_last_signed_in'].drop()
