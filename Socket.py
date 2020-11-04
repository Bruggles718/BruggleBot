import socket
from BotSettings import HOST, PORT, PASS, NICK, CHANNEL

def openSocket(): # this connects to twitch basically, thats all you really need to know
    s = socket.socket()
    s.connect((HOST, PORT))
    s.send((f"PASS " + PASS + "\r\n").encode('utf-8'))
    s.send((f"NICK " + NICK + "\r\n").encode('utf-8'))
    s.send((f"JOIN #" + CHANNEL + "\r\n").encode('utf-8'))
    return s

def sendMessage(s, message): # this sends a message in chat
    messageTemp = f"PRIVMSG #" + CHANNEL + " :" + message
    s.send((messageTemp + "\r\n").encode('utf-8'))
    print("Sent: " + messageTemp)