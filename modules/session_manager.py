import os
import sys
import time
import asyncio
import slixmpp
from getpass import getpass
from slixmpp.exceptions import IqError, IqTimeout
import xml.etree.ElementTree as ET

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Session(slixmpp.ClientXMPP):

    def __init__(self, jid, password, status, status_msg):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        
        # Local variables
        self.local_jid = jid
        self.local_status = status
        self.local_status_msg = status_msg
        self.room = ""
        self.room_owner = False
        self.nick = jid[:jid.index("@")]
        self.messages = {}
        self.online_contacts = {}

        # Set the client to auto authorize and subscribe when 
        # a subcription event is recieved
        self.roster.auto_authorize = True
        self.roster.auto_subscribe = True

        # Plugins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0045') # MUC
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0133') # Service administration
        self.register_plugin('xep_0199') # XMPP Ping

        # Set the events' handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("presence_subscribe", self._handle_new_subscription)
        self.add_event_handler("got_online", self.got_online)
        self.add_event_handler("got_offline", self.got_offline)
        self.add_event_handler("groupchat_message", self.muc_message)
        self.add_event_handler("disco_info",self.print_info)
        self.add_event_handler("disco_items", self.print_info)

    # start: Handles the start event
    # Args: self, event (stanza with event)
    async def start(self, event):

        # Send presence to server for it's distribution to subscribers
        self.send_presence(pshow=self.local_status, pstatus=self.local_status_msg)

        # Try comunication by asking for the roster
        try:
            await self.get_roster()
            print("\nSigned in as: " + self.local_jid)
        except:
            # Disconnect in case of failure
            print("Couldn't connect")
            self.disconnect()

    # message: Handles reciving messages
    # Args: self, msg (stanza with message)
    def message(self, msg):

        # Proccess message of type chat and normal
        if msg['type'] in ('chat', 'normal'):
            msg_from = str(msg['from'])
            msg_from = msg_from[:msg_from.index("@")]
            msg_body = str(msg['body'])

            # Store message in messages dictionary
            if msg_from in self.messages.keys():
                self.messages[msg_from]["messages"].append(msg_from + ": " + msg_body)
            else:
                self.messages[msg_from] = {"messages":[msg_from + ": " + msg_body]}

            print("*** message recieved from  " + msg_from + " ***")

    # direct_message: Sends a message to an specified users
    # Args: self, recipient (JID to send msg), msg (message's body)
    def direct_message(self, recipient, msg):
        self.send_message(mto=recipient, mbody=msg, mtype='chat', mfrom=self.local_jid)

        msg_to = recipient[:recipient.index("@")]
        msg_from = self.local_jid[:self.local_jid.index("@")]

        # Store message in messages dictionary
        if msg_to in self.messages.keys():
            self.messages[msg_to]["messages"].append(msg_from + ": " + msg)
        else:
            self.messages[msg_to] = {"messages":[msg_from + ": " + msg]}


    # get_contacts: Print contacts' info and status
    # Args: self
    def get_contacts(self):
        # Act. and get roster
        self.get_roster()
        contacts = self.roster[self.local_jid]

        # Print each user in roster
        for key in contacts.keys():
            
            # Avoid printing the own client
            if key == self.local_jid:
                continue
            
            # Print contact jid info
            print("Contact: " + str(key))

            # Get id without domain
            partial_jid = str(key)[:str(key).index("@")]

            # Print status info
            if partial_jid in self.online_contacts.keys():
                print("  show: " + str(self.online_contacts[partial_jid]["show"]))
                print("  status: " + str(self.online_contacts[partial_jid]["status"]))

            else:
                print("  show: unavailable")
                print("  status: unavailable")

            # Print general info
            print("  groups: " + str(contacts[key]["groups"]))
            print("  subscription: " + str(contacts[key]["subscription"]))
            
    
    # get_disconnected: Send unavailable presence and disconnect
    # Args: self
    def get_disconnected(self):
        pres = self.Presence()
        pres['type'] = 'unavailable'

        # Send stanza and wait
        pres.send()

    def get_messages(self):
        return self.messages
    
    def got_online(self, event):

        if "conference" in str(event['from']):
            return

        mfrom = str(event['from'])
        mfrom = mfrom[:mfrom.index("@")]

        mshow = ""
        mstatus= ""

        try:
            mshow = str(event['show'])
            mstatus = str(event['status'])
        except:
            mshow = "available"
            mstatus = "available"

        self.online_contacts[mfrom] = {"from":mfrom, "show":mshow, "status":mstatus}

        if mfrom == self.local_jid[:self.local_jid.index("@")]:
            return

        print("*** " + mfrom + " is online ***")
    
    def got_offline(self, event):

        if "conference" in str(event['from']):
            return

        mfrom = str(event['from'])
        mfrom = mfrom[:mfrom.index("@")]
        self.online_contacts[mfrom]["show"] = "unavailable"
        self.online_contacts[mfrom]["status"] = "unavailable"

        print("*** " + mfrom + " is now offline ***")

    async def muc_create_room(self, room, nick):
        self.room = room
        self.nick = nick
        self['xep_0045'].join_muc(room, nick)
        self['xep_0045'].set_affiliation(room, self.boundjid, affiliation='owner')

        self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
        self.add_event_handler("muc::%s::got_offline" % self.room, self.muc_offline)

        self.room_owner = True

        try:
            query = ET.Element('{http://jabber.org/protocol/muc#owner}query')
            x = ET.Element('{jabber:x:data}x', type='submit')
            query.append(x)
            iq = self.make_iq_set(query)
            iq['to'] = room
            iq['from'] = self.boundjid
            iq.send()
        except:
            print("Couldn't send room configurations")

    def muc_exit_room(self, msg=''):
        self['xep_0045'].leave_muc(self.room, self.nick, msg=msg)
        self.room = None
        self.nick = ''
        self.room_owner = False

    def muc_join(self, room, nick):
        self.room = room
        self.nick = nick
        self['xep_0045'].join_muc(room, nick, wait=True, maxhistory=False)

        self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
        self.add_event_handler("muc::%s::got_offline" % self.room, self.muc_offline)

    def muc_message(self, msg):
        if str(msg['mucnick']) != self.nick and self.room in str(msg['from']):
            print(str(msg['mucnick']) + ": " + str(msg['body']))
    
    def muc_online(self, presence):
        if presence['muc']['nick'] != self.nick:
            print(str(presence['muc']['nick']) + " just enter the room!")
            if self.room_owner:
                self['xep_0045'].set_affiliation(self.room, nick=str(presence['muc']['nick']), affiliation='member')
        else:
            print("You just enter the room!")
    
    def muc_offline(self, presence):
        if presence['muc']['nick'] != self.nick:
            print(str(presence['muc']['nick']) + " left the room...")

    def muc_send_message(self, msg):
        self.send_message(mto=self.room, mbody=msg, mtype='groupchat')

    def muc_discover_rooms(self):
        try:
            self['xep_0030'].get_items(jid='conference.redes2020.xyz')
        except (IqError, IqTimeout):
            print("Error in querry")

    def muc_discover_users(self):
        try:
            self['xep_0030'].get_items(jid='search.redes2020.xyz')
        except (IqError, IqTimeout):
            print("Error in querry")

    # print_info: print information of cases recieved from the server
    # Args: iq (stanza)
    def print_info(self, iq):
        
        # Processes result of rooms' query
        if str(iq['type']) == 'result' and 'conference' in str(iq['from']):
            
            print("\nPublic Rooms: ")

            # Print rooms
            cnt = 1
            to_print = ""
            for i in str(iq):
                # If on important info prepare and print
                if len(to_print) > 7 and i == '/':
                    print(str(cnt) + ". " + to_print)
                    to_print = ""
                    cnt += 1
                    continue
                elif "jid=" in to_print:
                    to_print += i
                    continue
                
                # Check for JID
                if i == "j":
                    to_print = 'j'
                elif i == "i":
                    to_print += 'i'
                elif i == "d":
                    to_print += 'd'
                elif i == "=":
                    to_print += '='
                else:
                    to_print = ''

    def send_subscription_request(self, to):
        try:
            self.send_presence_subscription(to, self.local_jid, 'subscribe')
        except:
            print("Subscribing failed")

    def _handle_new_subscription(self, pres):

        roster = self.roster[pres['to']]
        item = self.roster[pres['to']][pres['from']]

        if item['whitelisted']:
            item.authorize()

            if roster.auto_subscribe:
                item.subscribe()

        elif roster.auto_authorize:
            item.authorize()
            
            if roster.auto_subscribe:
                item.subscribe()

        elif roster.auto_authorize == False:
            item.unauthorize()

if __name__ == '__main__':
    # ID and arguments
    jid = input("ID: ")
    password = getpass("Password: ")

    xmpp = Session(jid, password, 'chat', 'hello')

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=True)
