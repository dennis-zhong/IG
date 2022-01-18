from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from constants import *
import time
from multiprocessing import Process, Queue
import json

class InstagramScraper:

    driver = None
    id = None

    def login(self):
        chrome_options = Options()
        # chrome_options.add_experimental_option("detach", True)
        # chrome_options.add_argument("--incognito")
        self.driver = webdriver.Chrome(executable_path=CHROME_PATH, options=chrome_options)
        self.driver.get("https://www.instagram.com/accounts/login/")
        body = self.driver.find_element_by_id("react-root") # access the correct body to get to elements
        time.sleep(1) # pw and user needs time to reveal
        body.find_element_by_name("password").send_keys(PASSWORD)
        body.find_element_by_name("username").send_keys(USERNAME)
        time.sleep(1) # give time to unlock login button
        body.find_element_by_class_name("sqdOP.L3NKy.y3zKF     ").click()
        self.driver.find_elements_by_tag_name("body")
        time.sleep(4) # give time to login

    def getID(self, username=USERNAME):
        self.driver.get("https://www.instagram.com/"+username+"/?__a=1")
        x = self.driver.find_element_by_tag_name("body").text
        dic = json.loads(x)
        self.id = dic['graphql']['user']['id']

    def setB(self):
        self.dic2 = {"id": self.id,
            "include_reel": True,
            "fetch_mutual": True,
            "first": 50
            }
        print(self.dic2)
        self.b = json.dumps(self.dic2, separators=(',', ':'))

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

    def get_followers(self):
        self.driver.get("https://www.instagram.com/graphql/query/?query_hash="+self.config['followers']['hash']+"&variables="+quote(self.b))
        self.followers_usernames = []
        bodytext = self.driver.find_element_by_tag_name("body").text
        dic3 = json.loads(bodytext)
        for edge in dic3['data']['user'][self.config['followers']['path']]['edges']:
            self.followers_usernames.append(edge['node']['username'])
        self.dic2['after'] = dic3['data']['user'][self.config['followers']['path']]['page_info']['end_cursor']
        while self.dic2['after']:
            self.b = json.dumps(self.dic2, separators=(',', ':'))
            self.driver.get("https://www.instagram.com/graphql/query/?query_hash="+self.config['followers']['hash']+"&variables="+quote(self.b))
            x = self.driver.find_element_by_tag_name("body").text
            dic3 = json.loads(x)
            for edge in dic3['data']['user'][self.config['followers']['path']]['edges']:
                self.followers_usernames.append(edge['node']['username'])
            self.dic2['after'] = dic3['data']['user'][self.config['followers']['path']]['page_info']['end_cursor']

    def get_following(self):
        self.driver.get("https://www.instagram.com/graphql/query/?query_hash="+self.config['following']['hash']+"&variables="+quote(self.b))
        self.following_usernames = []
        bodytext = self.driver.find_element_by_tag_name("body").text
        dic3 = json.loads(bodytext)
        for edge in dic3['data']['user'][self.config['following']['path']]['edges']:
            self.following_usernames.append(edge['node']['username'])
        self.dic2['after'] = dic3['data']['user'][self.config['following']['path']]['page_info']['end_cursor']
        while self.dic2['after']:
            self.b = json.dumps(self.dic2, separators=(',', ':'))
            self.driver.get("https://www.instagram.com/graphql/query/?query_hash="+self.config['following']['hash']+"&variables="+quote(self.b))
            x = self.driver.find_element_by_tag_name("body").text
            dic3 = json.loads(x)
            for edge in dic3['data']['user'][self.config['following']['path']]['edges']:
                self.following_usernames.append(edge['node']['username'])
            self.dic2['after'] = dic3['data']['user'][self.config['following']['path']]['page_info']['end_cursor']

    def main(page, username=USERNAME):
        thang = InstagramScraper()
        thang.login()
        thang.getID(username)
        thang.setB()
        if page=='followers':
            thang.get_followers()
            print(len(thang.followers_usernames))
            return thang.followers_usernames
        else:
            thang.get_following()
            print(len(thang.following_usernames))
            return thang.following_usernames

def compare(dictionary, username=USERNAME):
    print(len(dictionary["following"]))
    print(len(dictionary["followers"]))
    listofnotfollowers = [follow for follow in dictionary["following"] if follow not in dictionary["followers"]]
    print(listofnotfollowers)

def route(username=USERNAME): # needs to be less than 1000
    """
    Goes through followers+following of someone you follow and analyzes; Can only do a few hundred
    """
    dictionary = {}
    dictionary["followers"] = InstagramScraper.main("followers", username)
    dictionary["following"] = InstagramScraper.main("following", username)
    compare(dictionary)

start = time.time()
route()
print("Elapsed time: " + str(time.time() - start))