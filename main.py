import modules.register as register
import modules.unregister as unregister
import modules.session_manager as session
from getpass import getpass

act_session = None
singed_in = False

print("XMPP Chat client by Luis Diego F. V_0.1")

menu0 = '''
Select one of the options:
    1. Manage Account
    2. Messaging
    3. Exit
'''

menu1 = '''
Select one of the options:
    1. Sign in
    2. Sign out
    3. Register account
    4. Delete account
'''

menu2 = '''
Select one of the options:
    1. Show contacts & others
    2. Add contact
    3. Show contact's info
    4. Send direct message
    5. Group chat
    6. Presence message settings
    7. Send/receive notifications
    8. Send/receive files
'''

def process_menu1():
    try:
        opt = int(input(menu1))

        if opt < 1 or opt > 4:
            print("Choose one of the options")
            return

    except:
        print("Choose one of the options")
        return

    if opt == 1:
        jid = input("ID: ")
        password = getpass("Password: ")

    elif opt == 3:
        jid = input("ID: ")
        password = getpass("Password: ")

        xmpp = register.RegisterBot(jid, password)

        xmpp.connect()
        xmpp.process(forever=False)

    elif opt == 4:
        jid = input("ID: ")
        password = getpass("Password: ")

        xmpp = unregister.RegisterBot(jid, password)

        xmpp.connect()
        xmpp.process(forever=False)

def process_menu2():
    if singed_in == False:
        print("Please sign in first in the \"Manage Account\" option")
        return

    try:
        opt = int(input(menu2))

        if opt < 1 or opt > 8:
            print("Choose one of the options")
            return 

    except:
        print("Choose one of the options")
        return

while True:
    try:
        opt = int(input(menu0))

        if opt < 1 or opt > 3:
            print("Choose one of the options")
            continue

    except:
        print("Choose one of the options")
        continue

    if opt == 1:
        process_menu1()
    elif opt == 2:
        process_menu2()
    else:
        exit()