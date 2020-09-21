import time
import threading
import modules.register as register
import modules.unregister as unregister
import modules.session_manager as session
from getpass import getpass

print("XMPP Chat client by Luis Diego F. V_0.2")

menu0 = '''
Select one of the options:
    1. Manage Account
    2. Exit
'''

menu1 = '''
Select one of the options:
    1. Sign In/Enter Session
    2. Register account
    3. Delete account
    4. <- back
'''

menu1_1 =  '''
Select one of the options to show your subscribers:
    1. chat
    2. away
    3. xa
    4. dnd
'''

menu2 = '''
Select one of the options:
    1. Show direct messages
    2. Send direct messages
    3. Add contact
    4. Show contacts
    5. Disconect
'''

def session_thread(xmpp, stop):
    while True:
        xmpp.process(forever=True, timeout=3)
        
        if stop(): 
            break

        time.sleep(0.2)
    
    return

def process_menu1():
    try:
        opt = int(input(menu1))

        if opt < 1 or opt > 5:
            print("Choose a valid option")
            return

    except:
        print("Choose a valid option")
        return

    if opt == 1:
        jid = input("ID: ")
        password = getpass("Password: ")
        status = ""

        while True:
            st = 0
            status_msg = ""
            status_ops = ['chat','away','xa','dnd']

            stat_opt = input("Use defualt status: chat/available? (y/n) ")
            
            if stat_opt.upper() == 'Y' or stat_opt.upper() == "YES":
                status = 'chat'
                status_msg = "available"
                break
            
            try:
                st = int(input(menu1_1))
                if st < 1 or st > 4:
                    print("Choose a valid option")
                    continue
                status_msg = input("Add a status message: ")
            except:
                print("Choose a valid option")
                continue
            
            status = status_ops[st - 1]

            break

        xmpp = session.Session(jid, password, status, status_msg)
        xmpp.connect()

        stop_threads = False
        ses_thread = threading.Thread(target = session_thread, args=(xmpp, lambda : stop_threads,))
        ses_thread.start()

        time.sleep(3)

        while True:
            # Display open session menu
            try:
                opt2 = int(input(menu2))

                if opt2 < 1 or opt2 > 5:
                    print("Choose a valid option")
                    continue
            except:
                print("Choose a valid option")
                continue
            
            # OPTION 1: for seeing chats and responding
            if opt2 == 1:
                messages = xmpp.get_messages()

                # No active conversations found
                if len(messages.keys()) == 0:
                    print("You have 0 current chats, send a message to someone first")
                    continue
                
                # Print all active conversations
                index = 1
                print("Choose one of the following chats:")

                for key in messages.keys():
                    print("    " + str(index) + ". Chat whit " + key)
                    index += 1

                # User select conversation
                try:
                    chat_opt = int(input(""))
                except:
                    print("Choose a valid option")
                    continue
                
                # See if index is valid else display conv. and allow response
                if chat_opt < 1 or chat_opt >= index:
                    print("Choose a valid option")
                else:
                    # Get user and messages
                    user_to_chat = list(messages.keys())[chat_opt - 1]
                    messages_sent = messages[user_to_chat]["messages"]

                    # Display conversation
                    for i in messages_sent:
                        print(i)

                    # Response
                    print("*** write and press enter to respond (-q to quit) ***")
                    msg_body = input()

                    # Excape reserved word
                    if msg_body == '-q':
                        break

                    # Send Response  
                    xmpp.direct_message(user_to_chat + "@redes2020.xyz", msg_body)

            # OPTION 2: for sending a direct message
            elif opt2 == 2:
                msg_to = input("To: ")
                msg_body = input("Message: ")
                xmpp.direct_message(msg_to, msg_body)

                print("Message sent")

            # OPTION 3: for subscribing to someone
            elif opt2 == 3:
                msg_to = input("Subscribe to: ")

                xmpp.send_subscription_request(msg_to)
            
            # OPTION 4: for displaying contacts' info
            elif opt2 == 4:
                print("")
                xmpp.get_contacts()

            # OPTION 5: session log out
            elif opt2 == 5:
                xmpp.get_disconnected()
                time.sleep(4)
                stop_threads = True
                ses_thread.join()
                break

    elif opt == 2:
        jid = input("ID: ")
        password = getpass("Password: ")

        xmpp = register.RegisterBot(jid, password)

        xmpp.connect()
        xmpp.process(forever=False)

    elif opt == 3:
        jid = input("ID: ")
        password = getpass("Password: ")

        xmpp = unregister.RegisterBot(jid, password)

        xmpp.connect()
        xmpp.process(forever=False)

    elif opt == 4:
        return


while True:
    try:
        opt = int(input(menu0))

        if opt < 1 or opt > 2:
            print("Choose a valid option")
            continue

    except:
        print("Choose a valid option")
        continue

    if opt == 1:
        process_menu1()
    else:
        break
