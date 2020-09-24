#    main.py:  XMPP Chat Clinet
#    author:   Luis Diego Fernandez
#
#    CLI for managing an XMPP chat client
import time
import asyncio
import threading
import modules.register as register
import modules.unregister as unregister
import modules.session_manager as session
from getpass import getpass

print("XMPP Chat client by Luis Diego F.")

# Menu for managing account (FIRST menu)
menu1 = '''
Select one of the options:
    1. Sign In/Enter Session
    2. Register account
    3. Delete account
    4. Exit
'''

# Menu for choosing 'show' (OPTIONAL menu)
menu1_1 =  '''
Select one of the options to show your subscribers:
    1. chat
    2. away
    3. xa
    4. dnd
'''

# Menu for managing session options (SECOND menu)
menu2 = '''
Select one of the options:
    1. Show direct messages
    2. Send direct messages
    3. Add contact
    4. Show contacts
    5. Group Chat
    6. Disconect/Log-out
'''

# Menu for managing MUC (THIRD menu)
menu2_6 = '''
    1. Join room
    2. Create & join room
    3. Show all rooms
    4. <- Back
'''
# session_thread: Thread for running the main xmpp loop in background
# Args: xmpp (class type session), stop (lambda function returns bool)
def session_thread(xmpp, stop):

    # Process xmpp loop every 3 seconds, rest for 0.2s
    while True:
        # Run xmpp process in background
        try:
            xmpp.process(forever=True, timeout=3)
        except:
            print("shit")
        # Exit condition
        if stop(): 
            break

        time.sleep(0.2)
    
    # Disconnect xmpp client from server
    xmpp.get_disconnected()

    return

# run_cli: Displays and manage the cli loop
# Args: None
def run_cli():

    # Display first menu and get option
    while True:
        try:
            opt = int(input(menu1))

            # Check option is in range
            if opt < 1 or opt > 4:
                print("Choose a valid option")
                continue
            break
        except:
            print("Choose a valid option")
            continue

    # Log-in
    if opt == 1:
        # Input account info
        jid = input("ID: ")
        password = getpass("Password: ")
        status = ""

        # Get status and message from user
        while True:
            st = 0
            status_msg = ""
            status_ops = ['chat','away','xa','dnd']

            # Change or remain with default option
            stat_opt = input("Use default status: chat/available? (y/n) ")
            
            # Use default case
            if stat_opt.upper() == 'Y' or stat_opt.upper() == "YES":
                status = 'chat'
                status_msg = "available"
                break
            
            # Change status case
            try:
                st = int(input(menu1_1))

                # Check option is in range
                if st < 1 or st > 4:
                    print("Choose a valid option")
                    continue

                status_msg = input("Add a status message: ")
            except:
                print("Choose a valid option")
                continue
            
            # Get status form list of options
            status = status_ops[st - 1]
            break
        
        # Start xmpp class and connect
        xmpp = session.Session(jid, password, status, status_msg)
        xmpp.connect()

        # Start thread for background xmpp proccessing
        stop_threads = False
        ses_thread = threading.Thread(target = session_thread, args=(xmpp, lambda : stop_threads,))
        ses_thread.start()

        # Wait for connection timeout
        time.sleep(3)

        # Case of unable to connect to server
        if xmpp.unable_to_connect:

            # Wait a bit longer
            time.sleep(2)

            # If still unable to connect
            if xmpp.unable_to_connect:
                print("\nUNABLE to connect to server, check credentials.\n")
                stop_threads = True
                ses_thread.join()
                return

        # Start logged session loop
        while True:
            # Display open session menu
            try:
                opt2 = int(input(menu2))

                # Check option is in range
                if opt2 < 1 or opt2 > 6:
                    print("Choose a valid option")
                    continue
            except:
                print("Choose a valid option")
                continue
            
            # OPTION 1: for seeing chats and responding
            if opt2 == 1:
                # Get all conversations
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

                    xmpp.current_chat_with = user_to_chat

                    print("\n--------- DMs with " + user_to_chat.upper() + " ---------")
                    print("* write and press enter to respond (-q to quit) *")

                    # Display conversation
                    for i in messages_sent:
                        print(i)

                    # Direct chat loop
                    while True:
                        # Response
                        msg_body = input()

                        # Excape reserved word
                        if msg_body == '-q':
                            break

                        # Send Response  
                        xmpp.direct_message(user_to_chat + "@redes2020.xyz", msg_body)

                    xmpp.current_chat_with = None

            # OPTION 2: for sending a direct message
            elif opt2 == 2:
                msg_to = input("To: ")
                msg_body = input("Message: ")

                # Send message via xmpp client
                xmpp.direct_message(msg_to, msg_body)

                print("Message sent")

            # OPTION 3: for subscribing to someone
            elif opt2 == 3:
                msg_to = input("Subscribe to: ")

                # Submit subscribtion via xmpp client
                xmpp.send_subscription_request(msg_to)
            
            # OPTION 4: for displaying contacts' info
            elif opt2 == 4:
                print("\n------------- CONTACTS -------------")
                xmpp.get_contacts()

            # OPTION 5: for managing muc
            elif opt2 == 5:
                
                # Display MUC options menu (menu 2.6) and get option
                while True:
                    try:
                        opt2_6 = int(input(menu2_6))

                        # Check option is in range
                        if opt2_6 < 1 or opt2_6 > 4:
                            print("Choose a valid option")
                            continue

                        break
                    except:
                        opt2_6 = 4
                        break
                    
                # Exit option
                if opt2_6 == 4:
                    continue
                
                # Get all rooms option
                elif opt2_6 == 3:
                    xmpp.muc_discover_rooms()
                    continue
                
                # Get room & user's nickname for it
                room = input("Room: ")
                nick_name = input("Nickname: ")

                # Create and join room option
                if opt2_6 == 2:
                    asyncio.run(xmpp.muc_create_room(room, nick_name))
                
                # Join room option
                elif opt2_6 == 1:
                    xmpp.muc_join(room, nick_name)

                # Display room chat
                print("\n--------- MUC AT " + room.upper() + " ---------")
                print("* write and press enter to respond (-q to quit) *")

                # Input for muc
                while True:
                    try:
                        msg_body = input("")

                        # Excape reserved word
                        if msg_body == '-q':
                            break

                        xmpp.muc_send_message(msg_body)
                    except:
                        continue
                
                # Exit room
                xmpp.muc_exit_room()

            # OPTION 6: session log out
            elif opt2 == 6:
                stop_threads = True
                ses_thread.join()
                break
    
    # Create account
    elif opt == 2:
        jid = input("ID: ")
        password = getpass("Password: ")

        # Start, run and disconnect xmpp client for registration
        xmpp = register.RegisterBot(jid, password)
        xmpp.connect()
        xmpp.process(forever=False)

    # Delete account
    elif opt == 3:
        jid = input("ID: ")
        password = getpass("Password: ")

        # Start, run and disconnect xmpp client for unregistration
        xmpp = unregister.RegisterBot(jid, password)
        xmpp.connect()
        xmpp.process(forever=False)

    # Exit program
    elif opt == 4:
        return

# Run CLI
run_cli()
exit(1)
