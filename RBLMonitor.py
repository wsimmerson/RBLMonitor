#!/usr/bin/python3
#####################################
#                                   #
#   Real-Time Black List Monitor    #
#   By: Wayne Simmerson             #
#                                   #
#####################################

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from ipaddress import IPv4Address, AddressValueError
from socket import gethostbyname
import argparse
import smtplib
from email.mime.text import MIMEText

from RBLMonitor_db import Blacklist, Server, Listing

class RBLMonitor:

    def __init__(self):
        self.engine = create_engine('sqlite:///RBLMonitor.db', echo=True)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_rbl(self, name, url):
        """
            Add RBL to database
        """
        res = self.session.query(Blacklist).filter(or_(Blacklist.name == name, Blacklist.url == url)).first()
        if not res:
            print("Blacklist Name or URL is already monitored!")
            new_rbl = Blacklist(name, url)
            self.session.add(new_rbl)
            self.session.commit()
        else:
            print("Blacklist Name or URL is already monitored!")

    def remove_rbl(self, ident):
        """
            Removes rbl from database where name or url == ident
        """
        res = self.session.query(Blacklist).filter(or_(Blacklist.name == ident, Blacklist.url == ident)).first()

        if not res:
            print("No RBL identified by %s found!" % ident)
        else:
            blacklist_id = res.id
            self.session.delete(res)
            self.session.commit()
            res = self.session.query(Listing).filter(Listing.blacklist_id == blacklist_id).all()
            if not res:
                pass
            else:
                for listing in res:
                    self.session.delete(listing)
                    self.session.commit()

    def print_rbls(self):
        res = self.session.query(Blacklist).all()
        for bl in res:
            print(bl.name, bl.url)

    def add_ip(self, name, ip):
        """
            Add IP to Monitored table
        """
        res = self.session.query(Server).filter(or_(Server.name == name, Server.ip_address == ip)).first()
        if not res:
            try:
                IPv4Address(ip) # Validate the ipv4 address
                new_server = Server(name, ip)
                self.session.add(new_server)
                self.session.commit()
            except AddressValueError:
                print ('%s is not a valid IPv4 Address' % ip)
        else:
            print('Name or IP is already monitored!')

    def remove_ip(self, ident):
        """
            Removes a IP from database where name or ip == ident
        """
        res = self.session.query(Server).filter(or_(Server.name == ident, Server.ip_address == ident)).first()

        if not res:
            print("No Server identified by %s found!" % ident)
        else:
            server_id = res.id
            self.session.delete(res)
            self.session.commit()
            res = self.session.query(Listing).filter(Listing.server_id == server_id).all()
            if not res:
                pass
            else:
                for listing in res:
                    self.session.delete(listing)
                    self.session.commit()

    def print_servers(self):
        res = self.session.query(Server).all()
        for monitored in res:
            print(monitored.name, monitored.ip_address)

    def check_ip_all(self):
        """
            Check a single ip against all RBLs and 
            print all listings
        """
        blacklists = self.session.query(Blacklist).all()
        servers = self.session.query(Server).all()

        for server in servers:
            print('\n', server.name)
            listed = False
            for blacklist in blacklists:
                if self.check_ip2rbl(server.ip_address, blacklist.url):
                    print("[+]", blacklist.name, blacklist.url)
                    listed = True
            else:
                if not listed:
                    print("[-] No Blacklistings found!")


    def check_ip2rbl(self, server_ip, rbl_url):
        """
            Perform a single check of an ip to a rbl and
            return True / False
        """
        ip_parts = server_ip.split('.')
        ip_parts.reverse()
        ip_rev = '.'.join(ip_parts)

        try:
            lookup = gethostbyname(ip_rev + '.' + rbl_url)
            return True
        except:
            return False

    def check_all(self):
        """
            Check all Monitored IPs against all RBLs using
            self.check_ip2rbl, update Listings accordingly and
            return report data
        """
        return "report data"

    def send_report(report_data, email):
        """
            Email status report
        """
        msg = MIMEText(report_data)
        msg['Subject'] = 'RBL Check Report'
        msg['From'] = 'mail_admin@localhost'
        msg['To'] = email

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
    
if __name__ == '__main__':
    # Create RBLMonitor
    rbl = RBLMonitor()

    # Process Args
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-rbl', nargs=2, metavar=('name', 'url'), 
            help="add a new rbl")
    parser.add_argument('--add-server', nargs=2, metavar=('name', 'ip'), 
            help="add a new server ip to monitor")
    parser.add_argument('--remove-rbl', 
            help="remove rbl by name or url")
    parser.add_argument('--remove-ip', 
            help="remove monitored server by name or ip")
    parser.add_argument('--check-ip-all', action='store_true',
            help="check an ip against all rbls")
    parser.add_argument('--lookup', nargs=2, metavar=('ip', 'rbl-url'),
            help="check a ip against a user supplied rbl")
    parser.add_argument('--email', 
            help='send report to specified email')
    parser.add_argument('--show-rbls', action='store_true',
            help="print list of monitored RBLs")
    parser.add_argument('--show-servers', action='store_true',
            help="print list of monitored servers")

    options = vars(parser.parse_args())

    if not not options['add_rbl']:
        rbl.add_rbl(options['add_rbl'][0], options['add_rbl'][1])

    elif not not options['add_server']:
        rbl.add_ip(options['add_server'][0], options['add_server'][1])

    elif not not options['remove_rbl']:
        rbl.remove_rbl(options['remove_rbl'])
    
    elif not not options['remove_ip']:
        rbl.remove_ip(options['remove_ip'])

    elif options['check_ip_all']:
        rbl.check_ip_all()

    elif not not options['lookup']:
        rbl.checkip2rbl(options['lookup'][0], options['lookup'][1])

    elif not not options['email']:
        rbl.send_report(check_all(), options['email'])

    elif options['show_rbls']:
        rbl.print_rbls()

    elif options['show_servers']:
        rbl.print_servers()

    else:
        print(rbl.check_all())

