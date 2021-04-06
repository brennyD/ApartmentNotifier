from bs4 import BeautifulSoup
import requests
import json


class ApartmentBase:
    def __init__(self):
        self.seen_listings = []

    def new_listings(self):
        return "Im unimplemented the fuck?"


class Kiara(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)
        self.URL = "https://www.hollandresidential.com/wa/seattle/kiara/availability/luxury/"

    def map_row(self, row):
        ret = {
            "unit": int(row["Unit"]),
            "type": row["Type"],
            "baths": int(row["Baths"]),
            "sqft": int(row["SqFt"]),
            "floor": int(row["Floor"]),
            "rent": int(row["Rent"])
        }
        return ret

    def new_listings(self):
        page = requests.get(self.URL)
        raw_data = page.content
        anchor_string = b'var dataSet = '
        end_string = b'}];'
        data = raw_data.find(anchor_string) + len(anchor_string)
        raw_data = raw_data[data:]
        end = raw_data.find(end_string) + len(end_string) - 1
        data = raw_data[:end]
        data = json.loads(data)
        ret = None
        for r in data:
            info = self.map_row(r)
            if info["type"] == "2 Bedroom" and info["unit"] not in self.seen_listings:
                if ret is None:
                    ret = "NEW KIARA LISTING(s):\n"
                self.seen_listings.append(info["unit"])
                formatted = "{} unit {}, {} sqft for ${}/month on floor {}\n".format(info["type"], info["unit"], info["sqft"], info["rent"], info["floor"])
                ret += formatted


        return ret

class Stratus(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)
        self.URL_exts = ['b1', 'b2', 'b3', 'b4', 'b5']
        self.URL_BASE = "https://www.stratusseattle.com/floorplans/"

    def map_row(self, row):
        info = row.findAll('td')
        ret = {
            "unit": int(info[0].get_text().strip().split('#')[1]),
            "sqft": info[1].get_text().strip(),
            "rent": info[2].get_text().strip().split(":")[1],
        }
        return ret


    def new_listings(self):
        ret = None
        for e in self.URL_exts:
            req = requests.get(self.URL_BASE + e)
            soup = BeautifulSoup(req.content, 'html.parser')
            if b'Units are not available under selected Floor plan(s)' not in req.content:
                table = soup.find("table", class_=["table", "table-bordered"])
                body = table.find('tbody')
                rows = body.findAll('tr')
                for row in rows:
                    info = self.map_row(row)
                    if info["unit"] not in self.seen_listings:
                        self.seen_listings.append(info["unit"])
                        if ret is None:
                            ret = "NEW STRATUS LISTING(s):\n"
                        formatted = "{} unit {}, {} sqft with rent range of {}\n".format(e, info["unit"], info["sqft"], info["rent"])
                        ret += formatted
            else:
                print("No {} units".format(e))


        return ret

class McKenzie(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)
        self.URL = "https://sightmap.com/app/api/v1/6m9pzykzvk1/sightmaps/1106"

    def new_listings(self):
        req = requests.get(self.URL).json()["data"]
        ret = None
        fp = req["floor_plans"]
        units = req["units"]
        floor_plans = {}
        for f in fp:
            if f["bedroom_count"] == 2 and f["bathroom_count"] == 2:
                floor_plans[f["id"]] = f

        for u in units:
            if u["floor_plan_id"] in floor_plans and u["floor_id"] not in self.seen_listings:
                self.seen_listings.append(u["floor_id"])
                if ret is None:
                    ret = "McKenzie LISTING(s)\n"
                formatted = "unit {}, {} sqft with rent of ${}\n".format(u["unit_number"], u["display_area"].split(" ")[0], u["display_price"][1:])
                ret += formatted


        return ret




if __name__ == "__main__":
    apt = Stratus() #Kiara()
    print(apt.new_listings())
