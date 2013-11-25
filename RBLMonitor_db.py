#!/usr/bin/python3
#####################################
#                                   # 
#   Real-Time Black List Monitor    #   
#   Database Setup & objects        #
#                                   #
#   By: Wayne Simmerson             #
#   https://github.com/wsimmerson   #
#                                   #
#####################################

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///RBLMonitor.db', echo=True)
Base = declarative_base()

#############################
class Blacklist(Base):
    """

    """

    __tablename__ = "blacklists"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)

    def __init__(self, name, url):
        self.name = name
        self.url = url

############################
class Server(Base):
    """

    """

    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ip_address = Column(String)

    def __init__(self, name, ip_address):
        self.name = name
        self.ip_address = ip_address

############################
class Listing(Base):
    """

    """

    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    blacklist_id = Column(Integer, ForeignKey('blacklists.id'))
    server_id = Column(Integer, ForeignKey('servers.id'))

    def __init__(self, blacklist_id, server_id):
        self.blacklist_id = blacklist_id
        self.server_id = server_id


###########################

if __name__ == '__main__':
    Base.metadata.create_all(engine)
