#    unregister.py:  XMPP Clinet using Slixmpp
#
#    XMPP client for unregistering new user
import sys
import asyncio
import slixmpp
from getpass import getpass
from argparse import ArgumentParser
from slixmpp.exceptions import IqError, IqTimeout

# Set asyncio loop policies if using Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class RegisterBot(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # Plugins
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration

        # Set the events' handlers
        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        # Send presence
        self.send_presence()
        await self.get_roster()

        # unregister
        await self.unregister()

        # Disconnect
        self.disconnect()

    # unregister: Manage unregistration of account
    # Args: self
    async def unregister(self):
        # Set up message to send to server
        resp = self.Iq()
        resp['type'] = 'set'
        resp['from'] = self.boundjid.user
        resp['password'] = self.password
        resp['register']['remove'] = 'remove'

        # Sen request for unregistration
        try:
            await resp.send()
            print("Account unregistered for %s!" % self.boundjid)
        except IqError as e:
            print("Couldn't unregister account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()