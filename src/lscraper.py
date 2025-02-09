"""Web scraper for extracting Warframe game data from the Warframe Wiki."""

import re
import requests
from bs4 import BeautifulSoup

def send_request(category: str) -> BeautifulSoup:
    """Send a request to the Warframe Wiki and return the BeautifulSoup object."""
    url = "https://warframe.fandom.com/wiki/" + category
    r = requests.get(url, timeout=10)   
    response = BeautifulSoup(r.content, 'html.parser')
    return response

def write_to_file(fileName: str, csv: str) -> None:
    """Write the CSV data to a file."""
    with open(fileName, 'w', encoding='utf-8') as f:
        f.write(csv)

def scrape_weapons() -> None:
    """Scrape the weapons data from the Warframe Wiki."""
    response = send_request("Weapons")
    arr = response.findAll(lambda tag: tag.name=='span' and tag.has_attr('data-param') and tag.has_attr("data-param2"))

    weapon_set = set()
    
    for i in arr:
        item_key, item_val = i["data-param2"], i["data-param"]
        if item_key == "Weapons":
            modded_val = re.sub(r'\(.*\)', '', item_val).strip()
            modded_val = modded_val.replace(" ", "_")
            weapon_set.add(modded_val)
    weapons_arr = sorted(list(weapon_set))
    weapons_csv: str = ",".join(weapons_arr)
    write_to_file("../lists/weapons_list.txt", weapons_csv)

def scrape_warframes() -> None:
    """Scrape the warframes data from the Warframe Wiki."""
    response = send_request("Warframes")
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
    frame_list.sort()
    frames_csv = ",".join(frame_list)
    write_to_file("../lists/frames_list.txt", frames_csv)

if __name__ == "__main__":
    scrape_weapons()
    scrape_warframes()