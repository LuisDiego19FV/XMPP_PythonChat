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

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping

        self.add_event_handler("session_start", self.start)

    async def start(self, event):

        self.send_presence()
        try:
            await self.get_roster()
            print("Signed in")
        except:
            print("Couldn't connect")


        recipient = input("To: ")
        msg = input("Message: ")

        self.send_message(mto=recipient, mbody=msg, mtype='chat')
        
        self.disconnect()

if __name__ == '__main__':
    # ID and arguments
    # jid = input("ID: ")
    # password = getpass("Password: ")

    jid = "diego_test104@redes2020.xyz"
    password = "1234"

    xmpp = Session(jid, password)

    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=False)
