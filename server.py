import socket
from datetime import datetime
global currentTime
currentTime = ''
port = 23456
maxConnections = 1
endProgram = False

def connect():
    global endProgram
    # AF_INET makes the socket use IPv4
    # SOCK_STREAM instantiates a TCP connection
    print('----------New Session----------')
    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connects socket to the client to the port #
    Server.bind(('',port)) # This line only works with the nested parenthesis??
    # If it ain't broke, don't fix it
    # Allows the server to listen to maxConnections ports
    Server.listen(maxConnections)
    closing = False
    print("Connecting...")
    # Waits for connection
    connection, address = Server.accept()
    # When connected, print out to make sure it works :DDD
    print("Connection created with >>> ", str(address))

    # While server is recieving messages,
    # If message is 'TIME', send out the current time using datetime package
    # Else, tell client command was invalid
    # After completion, wait for another message

    #I had server.send instead of connection.send for 40 minutes :)
    while not closing and not endProgram:
        print("Recieving message...")
        # Recieve and decode the message sent from the client
        msg = connection.recv(1024).decode()
        print("Message recieved.")
        # Get the current date
        now = datetime.now()
        # Completely 'borrowed' this next line from GeeksForGeeks, just formats the datetime to a nice, readable string
        # https://www.geeksforgeeks.org/get-current-date-and-time-using-python/
        # Ctrl+F for -> curr_time = time.strftime("%H:%M:%S", time.localtime())
        currentTime = now.strftime("%m/%d/%y, %H:%M:%S")
        # If recieved message is "TIME" send out the current time
        if msg.upper() == "TIME":
            print("Sending time...")
            connection.send(currentTime.encode())
            print("Time sent")
        #Else if msg is Close (i.e. input to client was QUIT) close server and break loop
        elif msg.upper() == "QUIT":
            #Start the closing process and give updates
            print("Client closing connection")
            print("Server closing...")
            Server.close()
            print('Server closed.')
            # Prompt user for a new connection
            cond = input("Connect to a different client? (Y/N) >>> ")
            # If user inputs 'Y', process will run again and server will wait for a new client connection
            if cond.upper() == 'Y':
                connect()
            else:
                # Otherwise, program fully exits
                endProgram = True
                closing = True
                print('Program Finished.')
        #Otherwise, command not recognized, tell client
        else:
            print("Command unrecognized, informing client...")
            connection.send("Invalid command".encode())
            print("Client informed.")
# If program should not be ending (i.e. if just started or seeking new client, call connect() and run server program
if not endProgram:
    connect()

print("Clean exit")
# All commands for sockets and communcation between client and server found in the slides posted on blackboard