from sqlalchemy import Column,Integer,String
from database import Base
# We are creating a table in database here
class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index = True)
    address = Column(String)
    coordinates = Column(String)
    map_url=Column(String)



