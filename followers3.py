from instagrapi import Client
from constants import *

cl = Client()
print("here")
cl.login(USERNAME, PASSWORD)

username = "dennis.zhong"
print("here 1")
user_id = cl.user_id_from_username(username)

print("here 2")
followers = cl.user_followers(user_id)
print("here 3")
following = cl.user_following(user_id)
print("here 4")
lst = [follow for follow in following if follow not in followers]
for l in lst:
    print(following[l].username)