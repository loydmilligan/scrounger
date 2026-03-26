from sqlalchemy import Column, Integer, ForeignKey, Table
from ..database import Base

# Association table for many-to-many relationship between leads and items
lead_items = Table(
    'lead_items',
    Base.metadata,
    Column('lead_id', Integer, ForeignKey('leads.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True)
)
