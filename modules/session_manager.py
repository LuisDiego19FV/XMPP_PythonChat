import sys
import time
import asyncio
import slixmpp
from getpass import getpass
from slixmpp.exceptions import IqError, IqTimeout

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Session(slixmpp.ClientXMPP):

    def __init__(self, jid, password, status, status_msg):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        
        # Local variables
        self.local_jid = jid
        self.local_status = status
        self.local_status_msg = status_msg
        self.messages = {}
        self.online_contacts = {}

        # Set the client to auto authorize and subscribe when 
        # a subcription event is recieved
        self.roster.auto_authorize = True
        self.roster.auto_subscribe = True

        # Plugins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0133') # Service administration
        self.register_plugin('xep_0199') # XMPP Ping

        # Set the events' handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("presence_subscribe", self._handle_new_subscription)
        self.add_event_handler("got_online", self.got_online)
        self.add_event_handler("got_offline", self.got_offline)

    # start: Handles the start event
    # Args: self, event (stanza with event)
    async def start(self, event):
        
        # Default nickname is the username without domain
        nick = self.local_jid[:self.local_jid.index("@")]

        # Send presence to server for it's distribution to subscribers
        self.send_presence(pshow=self.local_status, pstatus=self.local_status_msg, pnick=nick)

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
            
            # Print general info
            print("Contact: " + str(key))
            print("  name: " + str(contacts[key]["name"]))
            print("  groups: " + str(contacts[key]["groups"]))
            print("  subscription: " + str(contacts[key]["subscription"]))

            # Get id without domain
            partial_jid = str(key)[:str(key).index("@")]

            # Print status info
            if partial_jid in self.online_contacts.keys():
                print("  show: " + str(self.online_contacts[partial_jid]["show"]))
                print("  status: " + str(self.online_contacts[partial_jid]["status"]))

            else:
                print("  show: unavailable")
                print("  status: unavailable")
            
    
    # get_disconnected: Send unavailable presence and disconnect
    # Args: self
    def get_disconnected(self):
        pres = self.Presence()
        pres['type'] = 'unavailable'

        # Send stanza and wait
        pres.send()

        self.disconnect()

    def get_messages(self):
        return self.messages
    
    def got_online(self, event):

        mfrom = str(event['from'])
        mfrom = mfrom[:mfrom.index("@")]

        mshow = ""
        mstatus= ""

        try:
            mshow = str(event['show'])
            mstatus = str(event['status'])
        except:
            mstatus = "available"

        self.online_contacts[mfrom] = {"from":mfrom, "show":mshow, "status":mstatus}
    
    def got_offline(self, event):

        mfrom = str(event['from'])
        mfrom = mfrom[:mfrom.index("@")]
        self.online_contacts[mfrom]["show"] = "unavailable"
        self.online_contacts[mfrom]["status"] = "unavailable"

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
