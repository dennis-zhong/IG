from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from constants import *
import time
from multiprocessing import Process, Queue
import json

driver = None
id = None
username = "dennis.zhong"
headers = None
headers_string = ""
followers_usernames = []
following_usernames = []
ret = {"following": [], "followers": []}

def login():
    global driver
    chrome_options = Options()
    # chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get("https://www.instagram.com/accounts/login/")
    body = driver.find_element_by_id("react-root") # access the correct body to get to elements
    time.sleep(1) # pw and user needs time to reveal
    body.find_element_by_name("password").send_keys(PASSWORD)
    body.find_element_by_name("username").send_keys(USERNAME)
    time.sleep(1) # give time to unlock login button
    body.find_element_by_class_name("sqdOP.L3NKy.y3zKF     ").click()
    driver.find_elements_by_tag_name("body")
    time.sleep(4) # give time to login

def getID():
    global driver, id, username
    driver.get("https://www.instagram.com/"+username+"/?__a=1")
    x = driver.find_element_by_tag_name("body").text
    print(x)
    profile = json.loads(x)
    id = profile['graphql']['user']['id']

def set_Headers():
    global headers, id, headers_string
    headers = {"id": id,
        "include_reel": True,
        "fetch_mutual": True,
        "first": 50
        }
    print(headers)
    headers_string = json.dumps(headers, separators=(',', ':'))

config = {
    'followers': {
        'hash': 'c76146de99bb02f6415203be841dd25a',
        'path': 'edge_followed_by'
    },
    'following': {
        'hash': 'd04b0a864b4b54837c0d870b0e77e076',
        'path': 'edge_follow'
    }
}

def get_Users_List(page, queue): # page = followers or following
    global driver, headers_string, config, headers
    driver.get("https://www.instagram.com/graphql/query/?query_hash="+config[page]['hash']+"&variables="+quote(headers_string))
    bodytext = driver.find_element_by_tag_name("body").text
    dic3 = json.loads(bodytext)
    users_lst = []
    for edge in dic3['data']['user'][config[page]['path']]['edges']:
        users_lst.append(edge['node']['username'])
    headers['after'] = dic3['data']['user'][config[page]['path']]['page_info']['end_cursor']
    while headers['after']:
        headers_string = json.dumps(headers, separators=(',', ':'))
        driver.get("https://www.instagram.com/graphql/query/?query_hash="+config[page]['hash']+"&variables="+quote(headers_string))
        x = driver.find_element_by_tag_name("body").text
        dic3 = json.loads(x)
        for edge in dic3['data']['user'][config[page]['path']]['edges']:
            users_lst.append(edge['node']['username'])
        headers['after'] = dic3['data']['user'][config[page]['path']]['page_info']['end_cursor']
    ret = queue.get()
    ret[page] = users_lst
    queue.put(ret)
    driver.quit()

def main(page, queue):
    print("Logging in...")
    login()
    print("Retrieving ID...")
    getID()
    print("Creating headers...")
    set_Headers()
    get_Users_List(page, queue)

def route():
    queue = Queue()
    queue.put(ret)
    p1 = Process(target=main, args = ('followers', queue))
    p2 = Process(target=main, args = ('following', queue))
    p1.start()
    time.sleep(1)
    p2.start()
    p1.join()
    p2.join()
    compare(queue)

def compare(queue):
    dictionary = queue.get()
    print(len(dictionary["following"]))
    print(len(dictionary["followers"]))
    listofnotfollowers = [follow for follow in dictionary["following"] if follow not in dictionary["followers"]]
    print(listofnotfollowers)

if __name__=='__main__':
    start = time.time()
    route()
    print("Elapsed time: " + str(time.time() - start))