import requests
import json
import re
from bs4 import BeautifulSoup

class Weapon:
    def __init__(self, name, mastery, type, max, slot, acqText, acqTable, foundryTable) -> None:
        self.name = name
        self.mastery: str = mastery
        self.type: str = type
        self.max: str = max
        self.slot: str = slot
        self.acqText: str = acqText
        self.acqTable = list(acqTable)
        self.foundryTable = list(foundryTable)

def _getAcquisitionRows(arr):
    res = []
    for i in arr:
        r = []
        if i.find(name="th"):
            continue
        else:
            for j in i.find_all(name="td"):
                r.append(j.get_text().replace("\\n", "").strip())
        res.append(r)
    return res

def _getAcquisitionText(soup):
    aquText = soup.find(name="span", id="Acquisition")
    try:
        aquText = soup.find(name="span", id="Acquisition").parent.find_next_sibling("p").get_text().strip()
    except:
        aquText = "No available source for the item yet"

    return aquText

def _getAcquisitionPrimeGrid(soup):
    tableHeader = soup.find(name="table", class_="article-table").find_all("th")
    tableInfo = soup.find(name="table", class_="article-table").find_all(name="td")
    aquInfo = []
    for idx, elem in enumerate(tableInfo):
        cTableHeader: str = tableHeader[idx].get_text().strip()
        cTableText: str = elem.get_text().replace(u'\xa0', u' ').strip()
        aquInfo.append([cTableHeader, cTableText])
    return aquInfo

def _getFoundryTable(soup):
    t = soup.find(name="table", class_="foundrytable")
    
    if not t:
        return []
    
    table = soup.find(name="table", class_="foundrytable").find_all("tr")
    resources = soup.find(name="table", class_="foundrytable").find_all(name="span", attrs={"data-param2": "Resources"})

    foundryMap = {}
    resourceList = []
    resourceCount = []

    for i in resources:
        resource = i['data-param']
        if resource == "Platinum":
            continue
        resourceList.append(resource)
    
    for idx, i in enumerate(table[1]):
        text = i.get_text().strip()
        if idx == 0:
            resource = "Credits"
        else: 
            resource = re.split(r"\d+", text)[0].replace(u'\xa0', u' ')
        
        val = "".join(re.findall(r"(\d+)", text))

        if not val:
            continue
            
        resourceCount.append(val)

    for i in range(len(resourceList)):
        foundryMap[resourceList[i]] = resourceCount[i]

    foundryMapList = [str(x + ": " + foundryMap[x]) for x in foundryMap.keys()]   
    return foundryMapList
    

def _getGeneralInformation(container):
    mastery : str       = container.find(attrs={"data-source": "Mastery"}).find(name='div').get_text()
    type : str          = container.find(attrs={"data-source": "Class"}).find(name='div').get_text()
    maxRank  : str      = container.find(attrs={"data-source": "MaxRank"}).find(name='div').get_text()
    slot : str          = container.find(attrs={"data-source": "Slot"}).find(name='div').get_text()

    return [mastery, type, maxRank, slot]


def _generateWeaponDetails(name, soup) -> Weapon:
    regTable = soup.find(name="table", class_="acquisition-table")
    acqTable = []

    if regTable:
        acqRows = soup.find(name="table", class_="acquisition-table").find_next(name="tbody").find_all(name="tr")
        acqTable = _getAcquisitionRows(acqRows)
    elif "Prime" in name:
        acqTable = _getAcquisitionPrimeGrid(soup)
    else:
        print("NO ROWS")
    
    acqText = _getAcquisitionText(soup)
    foundryTable = _getFoundryTable(soup)
    generalInfo = soup.find(name="aside", class_="portable-infobox")
    [mastery, type, maxRank, slot] = _getGeneralInformation(generalInfo)
    
    newWep = Weapon(name, mastery, type, maxRank, slot, acqText, acqTable, foundryTable)
    return newWep

def main():
    z = open("../lists/weapons_list.txt")
    f = open("../data/weapons.json", "w")
    weaponList = list(z.read().split(","))
    weaponJSON = {"weapons" : []}
    for i in range(0, 3):
        w = weaponList[i]
        print(w)
        r = requests.get('https://warframe.fandom.com/wiki/' + w)
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            newWep = _generateWeaponDetails(w, soup)
            jsonDump = json.dumps(vars(newWep))
            weaponJSON["weapons"].append(jsonDump)
            print(jsonDump)
        except Exception as error:
            print("GOOFED: ", error)
            continue
    
    f.write(json.dumps(weaponJSON))
    z.close()
    f.close()

if __name__ == "__main__":
    main()