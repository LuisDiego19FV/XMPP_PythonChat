#    session_manager.py:  XMPP Clinet using Slixmpp
#    author:              Luis Diego Fernandez
#
#    XMPP client for managing chats
import os
import sys
import time
import asyncio
import slixmpp
from getpass import getpass
from slixmpp.exceptions import IqError, IqTimeout
import xml.etree.ElementTree as ET

# Set asyncio loop policies if using Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Session: XMPP client class
# Manage all the atributes, functions and messages recieved
# from a XMPP server.
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
        self.current_chat_with = None
        self.unable_to_connect = True

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
            self.unable_to_connect = False
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
            # Get user
            msg_from = str(msg['from'])
            msg_from = msg_from[:msg_from.index("@")]
            msg_body = str(msg['body'])

            # Store message in messages dictionary
            if msg_from in self.messages.keys():
                self.messages[msg_from]["messages"].append(msg_from + ": " + msg_body)
            else:
                self.messages[msg_from] = {"messages":[msg_from + ": " + msg_body]}

            if self.current_chat_with == msg_from:
                print(msg_from + ": " + msg_body)
            else:
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

    # get_messages: Returns the conversations' log
    # Args: self
    def get_messages(self):
        return self.messages
    
    # got_online: Handles presence stanzas from contacts
    # when they get online.
    # Args: self, event (stanza)
    def got_online(self, event):

        # Avoid getting users from a MUC
        if "conference" in str(event['from']):
            return

        # Get from without domain
        mfrom = str(event['from'])
        mfrom = mfrom[:mfrom.index("@")]

        mshow = ""
        mstatus= ""

        # Try getting the show and status
        try:
            mshow = str(event['show'])
            mstatus = str(event['status'])
        except:
            mshow = "available"
            mstatus = "available"

        # Log the user' info in the local dictionary
        self.online_contacts[mfrom] = {"from":mfrom, "show":mshow, "status":mstatus}

        # Avoid printing self
        if mfrom == self.local_jid[:self.local_jid.index("@")]:
            return

        # Display notification
        print("*** " + mfrom + " is online. " + str(mstatus) + " ***")
    
    # got_offline: Handles presence stanzas from contacts
    # when they get offline.
    # Args: self, event (stanza)
    def got_offline(self, event):
        
        # Avoid getting users from a MUC
        if "conference" in str(event['from']):
            return

        # Get from without domain
        mfrom = str(event['from'])
        mfrom = mfrom[:mfrom.index("@")]

        # Log the user' info in the local dictionary
        self.online_contacts[mfrom]["show"] = "unavailable"
        self.online_contacts[mfrom]["status"] = "unavailable"

        # Display notification
        print("*** " + mfrom + " is now offline ***")

    # muc_create_room: manage the creation and setting of a new room
    # with self as owner
    # Args: self, room (string as room_name@domain), nick (user's nickname)
    async def muc_create_room(self, room, nick):
        # Set local atributes for room
        self.room = room
        self.nick = nick

        # Create and affiliate to the room
        self['xep_0045'].join_muc(room, nick)
        self['xep_0045'].set_affiliation(room, self.boundjid, affiliation='owner')

        # Add event handelers
        self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
        self.add_event_handler("muc::%s::got_offline" % self.room, self.muc_offline)

        # Set local ownership of room
        self.room_owner = True

        # Send default configurations for an instant room to the server
        try:
            # Set protocol of query
            query = ET.Element('{http://jabber.org/protocol/muc#owner}query')

            # Set Configurations and append them to the query
            x = ET.Element('{jabber:x:data}x', type='submit')
            query.append(x)

            # Create iq object with libray and send
            iq = self.make_iq_set(query)
            iq['to'] = room
            iq['from'] = self.boundjid
            iq.send()
        except:
            print("Couldn't send room configurations")

    # muc_exit_room: manage user exiting the actual room
    # Args: self, msg (string)
    def muc_exit_room(self, msg=''):
        # Leave room
        self['xep_0045'].leave_muc(self.room, self.nick, msg=msg)

        # Change local atributes
        self.room = None
        self.nick = ''
        self.room_owner = False

    # muc_join: manage user requesting joining a room
    # Args: self, room (string as room_name@domain), nick (user's nickname)
    def muc_join(self, room, nick):
        # Set local atributes for room
        self.room = room
        self.nick = nick

        # Request joining of room
        self['xep_0045'].join_muc(room, nick, wait=True, maxhistory=False)

        # Add handlers
        self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
        self.add_event_handler("muc::%s::got_offline" % self.room, self.muc_offline)

    # muc_message: Handle message from muc
    # Args: self, msg (string)
    def muc_message(self, msg):
        # Check room is active and message is not from self
        if str(msg['mucnick']) != self.nick and self.room in str(msg['from']):
            print(str(msg['mucnick']) + ": " + str(msg['body']))
    
    # muc_online: Handle presence stanza when a user enters the room
    # Args: self, presence (stanza)
    def muc_online(self, presence):

        # Case from when stanza is not form self
        if presence['muc']['nick'] != self.nick:
            print(str(presence['muc']['nick']) + " just enter the room!")

            # Auto assing user as a member of the room
            if self.room_owner:
                self['xep_0045'].set_affiliation(self.room, nick=str(presence['muc']['nick']), affiliation='member')
        
        # Case of self entering the room
        else:
            print("You just enter the room!")
    
    # muc_offline: Handle presence stanza when a user exits the room
    # Args: self, presence (stanza)
    def muc_offline(self, presence):
        if presence['muc']['nick'] != self.nick:
            print(str(presence['muc']['nick']) + " left the room...")

    # muc_send_message: Send message to actual group
    # Args: self, msg (string)
    def muc_send_message(self, msg):
        self.send_message(mto=self.room, mbody=msg, mtype='groupchat')

    # muc_discover_room: Send server request for public rooms info
    # Args: self
    def muc_discover_rooms(self):
        try:
            self['xep_0030'].get_items(jid='conference.redes2020.xyz')
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

    # send_subscription_request: send subscription to specific user
    # Args: self, to (string with user's complete JID)
    def send_subscription_request(self, to):
        try:
            self.send_presence_subscription(to, self.local_jid, 'subscribe')
        except:
            print("Subscribing failed")

    # _handle_new_subscription: Handler for handling the subsciption
    # Args: self, pres (stanza)
    def _handle_new_subscription(self, pres):
        # get roster and items
        roster = self.roster[pres['to']]
        item = self.roster[pres['to']][pres['from']]

        # Check whitelist
        if item['whitelisted']:
            item.authorize()

            if roster.auto_subscribe:
                item.subscribe()

        # Auto authorize case
        elif roster.auto_authorize:
            item.authorize()
            
            # If auto subscribe, subscribe to subscriber
            if roster.auto_subscribe:
                item.subscribe()

        # Reject request case 
        elif roster.auto_authorize == False:
            item.unauthorize()
