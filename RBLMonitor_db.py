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
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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
    logged = Column(DateTime, default=datetime.utcnow)

    def __init__(self, blacklist_id, server_id):
        self.blacklist_id = blacklist_id
        self.server_id = server_id


###########################

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    engine = create_engine('sqlite:///RBLMonitor.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    RBLS = {'Spamhaus-Zen': 'zen.spamhaus.org',
            'Spamcop': 'bl.spamcop.net',
            'Sorbs': 'dnsbl.sorbs.net',
            'Barracuda': 'b.barracudacentral.org',
            'Mailspike-Blacklist': 'bl.mailspike.net',
            'Mailspike-Reputation': 'rep.mailspike.net',
            'McAfee': 'cidr.bl.mcafee.com',
            'Microsoft Forefront': 'dnsbl.forefront.microsoft.com',
            'nsZones': 'bl.nszones.com',
            'ORBIT': 'rbl.orbit.com',
            'Pedantic-Netblock': 'netblock.pedantic.org',
            'Pedantic-Spam': 'spam.pedantic.org',
            'Lashback': 'ubl.unsubscore.com',
            'Backscatterer': 'ips.backscatterer.org'
            }

    # populate rbls from above

    for name, rbl in RBLS.items():
        session.add(Blacklist(name, rbl))
    session.commit()
