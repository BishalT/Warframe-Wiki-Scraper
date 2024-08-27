import requests
import re
from bs4 import BeautifulSoup
from collections import defaultdict

def _sendRequest(category: str) -> BeautifulSoup:
    url = "https://warframe.fandom.com/wiki/" + category
    r = requests.get(url)
    response = BeautifulSoup(r.content, 'html.parser')
    return response

def _writeFile(fileName, csv):
    f = open(fileName, 'w')
    f.write(csv)
    f.close()
    return

def _scrapeWeapons() -> None:
    response = _sendRequest("Weapons")
    arr = response.findAll(lambda tag: tag.name=='span' and tag.has_attr('data-param') and tag.has_attr("data-param2"))

    weapon_set = set()
    
    for i in arr:
        item_key, item_val = i["data-param2"], i["data-param"]
        if item_key == "Weapons":
            modded_val = re.sub(r'\(.*\)', '', item_val).strip()
            modded_val = modded_val.replace(" ", "_")
            weapon_set.add(modded_val)
    
    print(weapon_set)
    print(len(weapon_set))

    weapons_arr = sorted(list(weapon_set))
    weapons_csv: str = ",".join(weapons_arr)
    print(weapons_csv)
    
    _writeFile("../lists/weapons_list.txt", weapons_csv)
    return

def _scrapeWarframes() -> None:
    response = _sendRequest("Warframes")
    arr = response.findAll(name="div", class_="wds-is-current")
    a = []
    for i in arr:
        a = i.findAll(lambda tag: tag.name=='a' and tag.has_attr('title'))
    
    frame_list = []
    
    for elem in a:
        if "Update" not in elem['title']:
            frame = elem['title']
            frame = frame.replace(" ", "_").strip()
            frame_list.append(frame)
    
    print(frame_list)
    frame_list.sort()
    frames_csv = ",".join(frame_list)
    
    _writeFile("../lists/frames_list.txt", frames_csv)
    return

if __name__ == "__main__":
    _scrapeWeapons()
    _scrapeWarframes()
    