from bs4 import BeautifulSoup
import requests
import re

def get_shit():
    r = requests.get("https://hyprd.mn/leaderboards")
    soup = BeautifulSoup(r.content)
    t = soup.find('table', {'class:', 'leaderboard'})

    # [[rank, username, hd_id, score, run_link], [.....]]
    a = t.find_all('a')[0::2]
    b = t.find_all('a')[1::2]

    lb = []
    # a is user id and username
    # b is run id and score
    for i in range(1000):
        uid = a[i].attrs.get("href").rfind("/")
        uid = a[i].attrs.get("href")[uid+1::]
        rlink = b[i].attrs.get("href").rfind("/")
        rlink = b[i].attrs.get("href")[rlink + 1::]
        row = [i + 1, a[i].text, uid, b[i].text, rlink]
        lb.append(row) 
    return lb