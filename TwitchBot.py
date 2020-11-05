from Socket import openSocket, sendMessage
from Initialize import joinRoom
from Read import getMessage, getUser
from BotSettings import CHANNEL
import urllib
from urllib import request, parse
import json
from collections import defaultdict
import random
from threading import Timer, Event
import math
import time

blacklistedUsers = ["nightbot", "streamelements", "moobot", "streamlabs"] #this is just a list of users that the bot won't collect messages from
chatBackLogAmountMin = 50 #this is how many messages it will store before it starts generating messages
chatBackLogAmountMax = 100000 #this is how many messages it will store up to before it starts replacing old messages with new ones. basically, say you set this to 150. when the 151st message is sent, it will delete the first message it has stored, and replace it with the 151st, so it stays at 150 messages stored.
loopingMessages = False #this determines if it has started sending messages yet or not. this is just so that when you initially run it, it knows to start sending messages, and won't start the loop every time another message is sent.
timeRangeStart = 300 #this is the least amount of seconds it can take between messages
timeRangeEnd = 600 #this is the most amount of time it can take between messages. it randomly chooses a number between the timeRangeStart and timeRangeEnd fow how many seconds it will take to generate the next message
timeBetweenMessages = random.randint(timeRangeStart,timeRangeEnd)

s = openSocket() #check Socket.py
joinRoom(s) #check Initialize.py

readBuffer = ""

#sends a message and pings a user at the start of it
def answer(user, genmessage):
    sendMessage(s, "@" + user + " " + genmessage)

#loops sending a message every so often
def every_so_often():
    if not done.is_set():
        sendMessage(s, generate_message()) #check Socket.py for sendMessage
        timeBetweenMessages = random.randint(timeRangeStart,timeRangeEnd)
        Timer(timeBetweenMessages, every_so_often).start()

#this is the function used to generate the markov chain it will use to generate text
def markov_chain(text):
    temp = text.replace("\n", "\n ")
    temp = temp.split(' ')
    words = []
    for i in range(len(temp)-1):
        words.append(temp[i]+" "+temp[i+1])
    m_dict = defaultdict(list)
    for current_word, next_word in zip(words[0:-1], words[1:]):
        m_dict[current_word].append(next_word.split(' ')[1])
    m_dict = dict(m_dict)
    return m_dict

#this is the function used to get the first two words of every message it has stored so it can start the markov chain on one of these to ensure the message it generates starts at the beginning of a complete thought, not in the middle
def line_starts(text):
    lines = text.split('\n')
    linestarts = []
    for i in range(len(lines)):
        try:
            lines[i].split(" ")[2]
            linestarts.append(lines[i].split(" ")[0] + " " + lines[i].split(" ")[1])
        except:
            continue
    return linestarts

#this is the function that generates the message itself
def generate_message():
    file = open(CHANNEL + "chatmessages.txt", "r")
    text = file.read()
    chat_dict = markov_chain(text)
    linestarts = line_starts(text)
    word1 = random.choice(linestarts)
    sentence = word1
    while not ("\n" in sentence):
        word2 = random.choice(chat_dict[word1])
        word1 = word1.split(' ')[1] + " " + word2
        sentence += " " + word2
    file.close()
    return sentence

#this is where it starts the loop of reading chat
while True:
    readBuffer = readBuffer + s.recv(2048).decode('utf-8')
    temp = readBuffer.split('\n')
    readBuffer = temp.pop()
    for line in temp:
        user = getUser(line) #check Read.py
        message = getMessage(line) #check Read.py
        if line.startswith('PING'): #every few minutes, twitch sends PING to your bot to check if its afk. this sends back PONG, which is what tells twitch that it is not afk.
            print("PING")
            s.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
            print("PONG")
        else: #and if the message it recieves isnt just twitch pinging it, then it will decide what to do with it
            if not message.startswith("!"): #definitely dont want it saving commands as messages to generate. you can add whatever else you want it to not save in this if statement
                if user not in blacklistedUsers: #if the message wasn't sent by any blacklisted users
                    file = open(CHANNEL + "chatmessages.txt", "a") #it creates a text file to store messages to. it creates a separate one for each stream so it can stay relatively on topic to whatever stream it's currently in
                    try: #the reason this try except statement is here is because for some reason, it can't store emojis, so if it tries, it'll just crash. this statement just prevents a crash and skips the message
                        file.write(message)
                    except:
                        continue
                    file.close()
                    #lines 101 to 132 are to make the bot send a message if multiple people are starting their messages with the same thing. so if everybody is saying gg for example, it will say gg. it looks for matches in the past 10 messages.
                    file = open(CHANNEL + "chatmessages.txt", "r+")
                    try:
                        last10Lines = (file.readlines())[-10:]
                    except:
                        last10Lines = file.readlines()
                    file.close()
                    file = open(CHANNEL + "chatmessages.txt", "r+")
                    length = len(file.read().splitlines(True))
                    file.close()
                    counter = 1
                    for i in range(0, len(last10Lines) - 1):
                        temp = last10Lines[i].lower().replace("\n", "").split(" ")[0]
                        temp2 = last10Lines[len(last10Lines) - 1].lower().replace("\n", "").split(" ")[0]
                        if (temp == temp2):
                            counter += 1
                        if counter == 5: #change this number to the amount of matches you want it to look for before joining in the spam. just set this to anything over 10 if you dont want it to join in
                            try:
                                file = open("sentSpam.txt", "r+") #here, its creating a text file to store the last thing it said that was "spam." this way, if anybody says the same thing after the bot, it knows not to join in again. say 5 people say gg, so it says gg, and then another person says gg. you wouldnt want it to say gg a second time, so this makes sure it doesnt.
                                lastLine = (file.readlines())[-1:]
                                file.close()
                                if not lastLine[0].replace("\n", "") == temp2:
                                    sendMessage(s, message)
                                    file = open("sentSpam.txt", "a")
                                    file.write(temp2 + "\n")
                                    file.close()
                                break
                            except:
                                sendMessage(s, message)
                                file = open("sentSpam.txt", "a")
                                file.write(temp2 + "\n")
                                file.close()
                                break
                    print(str(length) + " " + user + ": " + message)
                    if length > chatBackLogAmountMin and loopingMessages == False: #makes sure to start looping sending messages if the minimum amount of stored messages is met and it hasn't started the loop yet
                        Timer(timeBetweenMessages, every_so_often).start()
                        loopingMessages = True
                    elif length > chatBackLogAmountMax: #makes sure the bot only stores as many messages as the max is set to
                        file = open(CHANNEL + "chatmessages.txt", "w+")
                        file.writelines(text[1:])
                        file.close()
