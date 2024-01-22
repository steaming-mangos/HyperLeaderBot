from bs4 import BeautifulSoup
import requests


def scrape_hyprdm_lb():
    html = requests.get("https://hyprd.mn/leaderboards").text
    soup = BeautifulSoup(html, "html.parser")
    t = soup.find("table", {"class:", "leaderboard"})

    # [[rank, username, hd_id, score, run_link], [.....]]
    users: list[int, str] = t.find_all("a")[0::2]
    ids: list[int, int] = t.find_all("a")[1::2]

    lb = {}
    # a is user id and username
    # b is run id and score
    for i in range(1000):
        uid = users[i].attrs.get("href").rfind("/")
        uid = users[i].attrs.get("href")[uid + 1 : :]
        rlink = ids[i].attrs.get("href").rfind("/")
        rlink = ids[i].attrs.get("href")[rlink + 1 : :]
        lb[uid] = {
            "rank": i + 1,
            "username": users[i].text,
            "score": ids[i].text,
            "run_link": rlink,
        }
    return lb
