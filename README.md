# XMPP_PythonChat
By: Luis Diego Fernandez

## Description
CLI client for XMPP. Allowing users to register & unregister accounts, log-in to an account at a server, sending messages, creating and chatting in groupchats, searching for groupchats, adding and displaying contacts, setting the status and loging out.

Features from planned features so far:
- [x] Register new account
- [x] Unregister account
- [x] Log in/Log out
- [x] Chat 1v1 whit any user
- [x] Create, join and display groupchats
- [x] Add contacts
- [x] Display contacts' info
- [x] Notification system for messages and presences
- [ ] File transfering

## Installation

Download the code from this repository.

### Language
Python 3 \ This program was tested with Python 3.8

### Dependencies
Install the following not-native libraries using pip:
- slixmpp            1.5.2
- asyncio            3.4.3

## Program & modules specifications
- Program MAIN.PY: runs the main CLI for the client, everything is process by the modules. It uses two threads, one for managing the inputs from the user and other for running the XMPP client.
- Module SESSION_MANAGER.PY: contains the class for the main XMPP client use in main.py. It contain the functions for processing messages, groupchats, adding contacts and requests from the server as well as the handlers for getting information from the server.
- Module REGISTER.PY: contains the class for the XMPP client for registering an account with a server. The module disign to run the request, getting a response and exiting afterwards.
- Module UNREGISTER.PY: contains the class for the XMPP client for unregistering an account with a server. The module disign to run the request, getting a response and exiting afterwards.

## Running & using the program the program

### Running
After installing the dependencies run: ```python main.py``` at the root of the repository.

### Using the program 
The first menu that will appear is:
```
    1. Sign In/Enter Session
    2. Register account
    3. Delete account
    4. Exit
```
#### Option 1: 
Will ask you to sign in with an ID and password (if you don't have any create one using the second option). The following is an example of entering:
```
  ID: usuer_name@domain.xyz
  Password:
```
Is neccesary that you include the domain to use. If you don't any find a public XMPP server to use. Also remember that the password won't be display when you write it.

After this a way of setting the status and the show messages will be display, just follow the instructions at the console. There is an option to use a default status, if you want to use it enter 'y' when the asked.

After a succesfull login the following menu will appear:
```
Select one of the options:
    1. Show direct messages
    2. Send direct messages
    3. Add contact
    4. Show contacts
    5. Group Chat
    6. Disconnect/Log-out
```
- Show direct messages (1): Allows you to enter a direct chat with a user. If a promt appears saying you have 0 active conversations just send a message to some one first using the option 'Send direct messages' (2) at the menu. Else a menu will appear where you can select a chat to enter, in here you can send messages by simply writting and pressing enter. To exit the chat enter '-q' and press enter.
- Send direct messages (2): Allows you to send a message to any user in the server. You have to know their JID (with domain included), for ```example user2@domain.xyz```. After sending an initial message to someone a conversation will be available at the option 'Show direct messages' (1).
- Add contact (3): Allows you to add a contact. You have to know their JID (with domain included), for example ```user2@domain.xyz```. After this the contact info will appear at the 'Show contacts' option (4).
- Group Chat (5): This will display several options. You can 1. Create a new room, 2. Enter a new room, 3. Request name of all public rooms. In the first two options it will require the name of the room and a nickname for you. The nickname can be anything you want. The name of the room has to contain the name and domain of the room, for example: ```room@conference.domain.xyz```. Afterwards a groupchat will open, in here you can send messages by simply writting and pressing enter. To exit the chat enter '-q' and press enter.
- Disconnect/Log-out (6): Will log you out. You will also exit the program.

#### Option 2:
It will request from you the useranme and password for the new account. The following is an example:
```
  ID: usuer_name@domain.xyz
  Password:
```
Remember that the password won't be display when you write it.

Then if succesfull will display:
```
  Account created for user_name@domain.xyz
```

#### Option 3:
It will request from you the useranme and password for the account to delete. The following is an example:
```
  ID: usuer_name@domain.xyz
  Password:
```
Remember that the password won't be display when you write it.

Then if succesfull will display:
```
  Account deleted for user_name@domain.xyz
```

#### Option 4:
Exit option.
