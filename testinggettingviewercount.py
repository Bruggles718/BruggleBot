import urllib
import json
from urllib import request, parse
import math

response = urllib.request.urlopen('http://tmi.twitch.tv/group/user/joaish/chatters')
data = json.loads(response.read())
viewercount = data['chatter_count']
z = 5
def test():
    global z
    z+=1
test()
print(z)