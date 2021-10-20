from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from constants import *
import time
from multiprocessing import Process, Queue
import json

followers = []
following = []
ret = {"following": [], "followers": []}
driver = None
def getListFromPage(pageurl, queue):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=CHROME_PATH, options=chrome_options)
    driver.get("https://www.instagram.com/accounts/access_tool/"+pageurl)
    body = driver.find_element_by_id("react-root") # access the correct body to get to elements
    time.sleep(2) # pw and user needs time to reveal
    body.find_element_by_name("password").send_keys(PASSWORD)
    body.find_element_by_name("username").send_keys(USERNAME)
    time.sleep(2) # give time to unlock login button
    body.find_element_by_class_name("sqdOP.L3NKy.y3zKF     ").click()
    time.sleep(4) # give time to login
    driver.get("https://www.instagram.com/accounts/access_tool/"+pageurl)
    body = driver.find_element_by_id("react-root")
    time.sleep(1)
    viewmore = body.find_element_by_xpath('//button[text()="View More"]')
    try:
        while viewmore:
            viewmore.click()
            time.sleep(1)
    except:
        pass
    listofpeople = []
    for person in body.find_elements_by_class_name("-utLf"):
        listofpeople.append(person.text)
    ret = queue.get()
    if pageurl == "accounts_following_you":
        ret["followers"] = listofpeople
    else:
        ret["following"] = listofpeople
    queue.put(ret)
    driver.quit()

def loginIG():
    global driver
    chrome_options = Options()
    # chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(executable_path=CHROME_PATH, options=chrome_options)
    driver.get("https://www.instagram.com/accounts/login/")
    body = driver.find_element_by_id("react-root") # access the correct body to get to elements
    time.sleep(1) # pw and user needs time to reveal
    body.find_element_by_name("password").send_keys(PASSWORD)
    body.find_element_by_name("username").send_keys(USERNAME)
    time.sleep(1) # give time to unlock login button
    body.find_element_by_class_name("sqdOP.L3NKy.y3zKF     ").click()
    time.sleep(4) # give time to login

def getListFromFlex(pageurl, queue):
    loginIG()
    global driver
    driver.get("https://www.instagram.com/"+USERNAME) # get again in case of pop ups
    body = driver.find_element_by_id("react-root")
    time.sleep(1)
    numlst = int(body.find_element_by_partial_link_text(pageurl).text.split()[0])
    body.find_element_by_xpath("//a[@href='/"+USERNAME+"/"+pageurl+"/']").click()
    time.sleep(1)
    currlst = []
    while(len(currlst)<numlst):
        currlst = driver.find_elements_by_class_name("FPmhX.notranslate._0imsa ")
        driver.execute_script("arguments[0].scrollIntoView(true);", currlst[-1])
        time.sleep(0.75)
    listofpeople = []
    for person in driver.find_elements_by_class_name("FPmhX.notranslate._0imsa "):
        listofpeople.append(person.text)
    ret = queue.get()
    ret[pageurl] = listofpeople
    queue.put(ret)
    driver.quit()

def getListFromFlex(pageurl, queue, username):
    loginIG()
    global driver
    driver.get("https://www.instagram.com/"+username) # get again in case of pop ups
    body = driver.find_element_by_id("react-root")
    time.sleep(1)
    numlst = int(body.find_element_by_partial_link_text(pageurl).text.split()[0].replace(",",""))
    body.find_element_by_xpath("//a[@href='/"+username+"/"+pageurl+"/']").click()
    time.sleep(1)
    currlst = []
    while(len(currlst)<numlst):
        currlst = driver.find_elements_by_class_name("FPmhX.notranslate._0imsa ")
        driver.execute_script("arguments[0].scrollIntoView(true);", currlst[-1])
        time.sleep(0.5)
    listofpeople = []
    for person in driver.find_elements_by_class_name("FPmhX.notranslate._0imsa "):
        listofpeople.append(person.text)
    ret = queue.get()
    ret[pageurl] = listofpeople
    queue.put(ret)
    driver.quit()

def route1():
    """
    Checks your own following and followers; Can do around 1.5k
    """
    queue = Queue()
    queue.put(ret)
    page1 = "accounts_following_you"
    page2 = "accounts_you_follow"
    p1 = Process(target=getListFromPage, args = (page1, queue))
    p2 = Process(target=getListFromPage, args = (page2, queue))
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
    recordkeep(dictionary)
    print(listofnotfollowers)

def recordkeep(dictionary):
    with open("record.txt", "r+") as f:
        record = json.loads(f.read())
        old_record = record[USERNAME]
        if old_record:
            lost_followers = [follower for follower in old_record["followers"] if follower not in dictionary["followers"]]
            print("Lost followers")
            print(lost_followers)
        record[USERNAME] = dictionary
        f.write(json.dumps(record))

def route2(username=""):
    """
    Goes through followers+following of someone you follow and analyzes; Can only do a few hundred
    """
    queue = Queue()
    queue.put(ret)
    page1 = "followers"
    page2 = "following"
    if username == "":
        p1 = Process(target=getListFromFlex, args = (page1, queue,))
        p2 = Process(target=getListFromFlex, args = (page2, queue,))
    else:
        p1 = Process(target=getListFromFlex, args = (page1, queue, username,))
        p2 = Process(target=getListFromFlex, args = (page2, queue, username,))
    p1.start()
    time.sleep(1)
    p2.start()
    p1.join()
    p2.join()
    compare(queue)

# driver.find_element_by_class_name("sqdOP.yWX7d.y3zKF     ") Not Now button