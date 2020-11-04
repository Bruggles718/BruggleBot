import string
from Socket import sendMessage

def joinRoom(s): #this will basically just print some initial stuff. its not really important. you dont even have to call it. however, if you uncomment the sendMessage after where it prints "Successfully Connected" you can have it say an initial message when it joins a chat room.
    readbuffer = ""
    Loading = True
    while Loading:
        readbuffer = readbuffer + s.recv(1024).decode('utf-8')
        temp = readbuffer.split("\n")
        readbuffer = temp.pop()

        for line in temp:
            print(line)
            Loading = loadingComplete(line)
    print("Successfully Connected")
    #sendMessage(s, "Successfully Connected")

def loadingComplete(line):
    if "End of /NAMES list" in line:
        return False
    else:
        return True