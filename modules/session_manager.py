import sys
import asyncio
import slixmpp
from getpass import getpass
from slixmpp.exceptions import IqError, IqTimeout

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Session(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.messages = []

        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0004') # Data Forms
        xmpp.register_plugin('xep_0060') # PubSub
        xmpp.register_plugin('xep_0199') # XMPP Ping

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    async def start(self, event):

        self.send_presence()
        try:
            await self.get_roster()
            print("Connected")
            return 1
        except:
            print("Couldn't connect")
            return -1
            self.disconnect()

    def message(self, msg):

        if msg['type'] in ('chat', 'normal'):
            print((msg['from'], msg))

    def direct_message(self, recipient, msg):

        self.send_message(mto=recipient, mbody=msg, mtype='chat')

    def disconnect(self):

        self.disconnect()

        print("Account disconnected")


if __name__ == '__main__':
    # ID and arguments
    jid = input("ID: ")
    password = getpass("Password: ")

    xmpp = Session(jid, password)

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=True)
