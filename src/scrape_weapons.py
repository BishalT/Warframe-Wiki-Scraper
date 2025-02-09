"""Script for scraping detailed weapon information from Warframe Wiki and generating JSON data."""

import json
import re
import requests
from bs4 import BeautifulSoup

class Weapon:
    """Class representing a weapon in Warframe."""
    def __init__(self, name, mastery, weapon_type, max_rank, slot, acq_text, acq_table, foundry_table) -> None:
        """Initialize a Weapon object."""
        self.name = name
        self.mastery: str = mastery
        self.weapon_type: str = weapon_type
        self.max_rank: str = max_rank
        self.slot: str = slot
        self.acq_text: str = acq_text
        self.acq_table = acq_table
        self.foundry_table = foundry_table

def get_acquisition_rows(arr):
    """Get acquisition rows from the HTML table."""
    res = []
    for table_row in arr:
        r = []
        if table_row.find(name="th"):
            continue
        else:
            for idx, column_info in enumerate(table_row.find_all(name="td")):
                if idx == 0:
                    text = column_info.find("span", {"class": "hidden"}).next_sibling.getText().replace("\\n", "").strip()
                else:
                    text = column_info.getText().replace("\\n", "").strip()
                r.append(text)
        res.append(r)
    return res

def get_acquisition_text(soup):
    """Get acquisition text from the HTML table."""
    aqu_text = soup.find(name="span", id="Acquisition")
    try:
        stripped_text = soup.find(name="span", id="Acquisition").parent.find_next_sibling("p").get_text().strip()
        split_text = (re.sub(r"({.*})", "", stripped_text).split(" "))
        aqu_text = " ".join(map(lambda x: x.strip(), split_text))
    except Exception as e:
        print("Error getting acquisition text: ", e)
        aqu_text = "No available source for the item yet"
    return aqu_text

def get_acquisition_prime_grid(soup):
    """Get acquisition prime grid from the HTML table."""
    table_headers = soup.find(name="table", class_="article-table").find_all("th")
    table_info = soup.find(name="table", class_="article-table").find_all(name="td")
    aqu_info = []
    for idx, elem in enumerate(table_info):
        c_table_header: str = table_headers[idx].get_text().strip()
        c_table_text: str = elem.get_text().replace(u'\xa0', u' ').strip()

        stxt = c_table_text.split(" ")
        i = 0
        relics = []
        while i < len(stxt):
            if i + 3 < len(stxt) and stxt[i + 3] == '(V)':
                break
            relic_info = " ".join(stxt[i:i+3])
            i += 3
            relics.append(relic_info)
        c_table_text_joined = ",".join(relics)
        aqu_info.append([c_table_header, c_table_text_joined])
    return aqu_info

def get_foundry_table(soup):
    """Get foundry table from the HTML table."""
    t = soup.find(name="table", class_="foundrytable")
    if not t:
        print("No foundry table found")
        return []
    table = soup.find(name="table", class_="foundrytable").find_all("tr")
    resources_row = soup.find(name="table", class_="foundrytable").find_all("tr")
    resources_name_row = resources_row[1].find_all(name="span", attrs={"data-param2": "Resources"})
    foundry_map = {}
    resource_list = []
    resource_count = []

    for i in resources_name_row:
        resource = i['data-param']
        if resource == "Platinum":
            continue
        if resource == "Standing":
            continue
        resource_list.append(resource)
    
    for idx, i in enumerate(table[1]):
        text = i.getText().strip()
        resource = ""
        if idx == 0:
            resource = "Credits"
        else: 
            resource = re.split(r"\d+", text)[0].replace(u'\xa0', u' ')
        
        val = "".join(re.findall(r"(?<=})\d{1,3}(?:,\d{3})*", text))

        if not val:
            continue
            
        resource_count.append(val.replace(",", ""))

    for i, elem in enumerate(resource_list):
        foundry_map[elem] = resource_count[i]

    foundry_map_list = [str(x + ": " + foundry_map[x]) for x in foundry_map]
    return foundry_map_list
    

def find_label(container, label):
    """Find a label in the HTML table."""
    divs = container.find_all("div", {"class": "label left"})
    for div in divs:
        a_tag = div.find("a", {"title": label})
        if a_tag:
            return div.find_next_sibling("div", {"class": "value right"}).get_text().strip()
    return None

def find_max_rank(container):
    """Find the max rank in the HTML table."""
    divs = container.find_all("div", {"class": "label left"})
    for div in divs:
        if div.get_text().strip() == "Max Rank":
            return div.find_next_sibling("div", {"class": "value right"}).get_text().strip()
    return None

def get_general_information(container):
    """Get general information from the HTML table."""

    mastery : str       = find_label(container, "Mastery Rank")
    weapon_type : str   = find_label(container, "Mod/Compatibility")
    slot : str          = find_label(container, "Weapons")
    max_rank : str      = find_max_rank(container)
    return [mastery, weapon_type, max_rank, slot]


def get_weapon_details(weapon_name, body) -> Weapon:
    """Generate weapon details from the HTML table."""
    reg_table = body.find("table",{"class": "acquisition-table"})
    acq_table = []

    if reg_table:
        acq_rows = body.find("table",{"class": "acquisition-table"}).find_next("tbody").find_all("tr")
        acq_table = get_acquisition_rows(acq_rows)
    elif "Prime" in weapon_name:
        acq_table = get_acquisition_prime_grid(body)
    else:
        print("NO ROWS")
    
    acq_text = get_acquisition_text(body)
    foundry_table = get_foundry_table(body)
    general_info = body.find("div", {"class": "infobox"})
    [mastery, weapon_type, max_rank, slot] = get_general_information(general_info)
    new_wep = Weapon(weapon_name, mastery, weapon_type, max_rank, slot, acq_text, acq_table, foundry_table)
    return new_wep

def send_request(weapon_name: str) -> BeautifulSoup:
    """Send a request to the Warframe Wiki and return the BeautifulSoup object."""
    url = "https://wiki.warframe.com/w/" + weapon_name
    r = requests.get(url, timeout=10)
    response = BeautifulSoup(r.text, 'html.parser')
    return response

def main():
    """Main function to scrape weapon data and generate JSON output file."""
    with open("./lists/weapons_list.txt", encoding='utf-8') as z:
        with open("./data/weapons.json", "w", encoding='utf-8') as f:
            weapon_list = list(z.read().split(","))
            weapon_json = {"weapons" : []}
            for i, weapon_name in enumerate(weapon_list):
                print(f"Processing weapon {i+1} of {len(weapon_list)}: {weapon_name}")
                try:
                    r = send_request(weapon_name)
                    new_wep = get_weapon_details(weapon_name, r)
                    json_dump = json.loads(json.dumps(vars(new_wep)))
                    weapon_json["weapons"].append(json_dump)
                except Exception as error:
                    print("Error: ", error)
                    new_wep = Weapon(weapon_name, "-1", "-1", "-1", "-1", "-1", "-1", "-1")
                    json_dump = json.loads(json.dumps(vars(new_wep)))
                    weapon_json["weapons"].append(json_dump)
            json.dump(weapon_json, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()