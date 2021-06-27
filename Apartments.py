from bs4 import BeautifulSoup
import requests
import json


class ApartmentBase:
    def __init__(self):
        self.seen_listings = {}

    def new_listings(self):
        return "Im unimplemented!"

    def generate_text(self, units, building_name, has_type=False):
        text = "{} Listings:\n".format(building_name)
        for number, unit in units.items():
            if number not in self.seen_listings:
                msg = "Unit {} available {}, {} sqft for ${}\n".format(number, unit["available"], unit["sqft"], unit["rent"])
                if has_type:
                    msg = "{} {}".format(unit["type"], msg)
                text += msg
                self.seen_listings[number] = unit
        for number, unit in dict(self.seen_listings).items():
            if number not in units:
                msg = "Unit {}, {} sqft, ${} is no longer available\n".format(number, unit["sqft"], unit["rent"])
                del self.seen_listings[number]
                text += msg

        if text == "{} Listings:\n".format(building_name):
            return None

        return text


class Kiara(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)
        self.URL = "https://www.hollandresidential.com/wa/seattle/kiara/availability/luxury/"

    def map_row(self, row):
        ret = {
            "unit": int(row["Unit"]),
            "type": row["Type"],
            "sqft": int(row["SqFt"]),
            "available": row["Available"],
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
        rem = ""

        units = {}
        for r in data:
            try:
                row = self.map_row(r)
                if row["type"] == "2 Bedroom":
                    addition = self.map_row(r)
                    units[addition["unit"]] = addition
            except Exception as e:
                print(e)
                continue

        return self.generate_text(units, "Kiara")


class Stratus(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)
        self.URL_exts = ['b1', 'b2', 'b3', 'b4', 'b5']
        self.URL_BASE = "https://www.stratusseattle.com/floorplans/"

    def map_row(self, row):
        info = row.findAll('td')
        date = info[4].get_text().strip().split(":")[1]
        ret = {
            "unit": int(info[0].get_text().strip().split('#')[1]),
            "sqft": info[1].get_text().strip(),
            "rent": info[2].get_text().strip().split(":")[1],
            "available": "now" if date == "Available" else date
        }
        return ret


    def new_listings(self):
        units = {}
        for e in self.URL_exts:
            req = requests.get(self.URL_BASE + e)
            soup = BeautifulSoup(req.content, 'html.parser')
            if b'Units are not available under selected Floor plan(s)' not in req.content:
                table = soup.find("table", class_=["table", "table-bordered"])
                body = table.find('tbody')
                rows = body.findAll('tr')
                for row in rows:
                    obj = self.map_row(row)
                    obj["type"] = e
                    units[obj["unit"]] = obj
            else:
                print("No {} units".format(e))

        return self.generate_text(units, "Stratus", True)

class McKenzie(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)
        self.URL = "https://sightmap.com/app/api/v1/6m9pzykzvk1/sightmaps/1106"

    def new_listings(self):
        req = requests.get(self.URL).json()["data"]
        ret = None
        rem = ""
        fp = req["floor_plans"]
        units = req["units"]
        floor_plans = {}
        formatted_units = {}
        for f in fp:
            if f["bedroom_count"] == 2 and f["bathroom_count"] == 2:
                floor_plans[f["id"]] = f

        for u in units:
            if u["floor_plan_id"] in floor_plans:
                formatted_units[u["unit_number"]] = {
                    "sqft": u["display_area"].split(" ")[0],
                    "rent": u["display_price"][1:],
                    "unit": u["unit_number"],
                    "available": u["display_available_on"]
                }

        return self.generate_text(formatted_units, "McKenzie")

class Cirrus(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)
        self.URL_exts = ['b1', 'b2-2bed2', 'b3']
        self.URL_BASE = "https://www.cirrusseattle.com/floorplans/"

    def map_row(self, row):
        info = row.findAll('td')
        date = info[4].get_text().strip().split(":")[1]
        ret = {
            "unit": int(info[0].get_text().strip().split('#')[1]),
            "sqft": info[1].get_text().strip(),
            "rent": info[2].get_text().strip().split(":")[1],
            "available": "now" if date == "Available" else date
        }
        return ret

    def new_listings(self):
        ret = None
        units = {}
        rem = ""
        for e in self.URL_exts:
            req = requests.get(self.URL_BASE + e)
            soup = BeautifulSoup(req.content, 'html.parser')
            if b'Units are not available under selected Floor plan(s)' not in req.content:
                table = soup.find("table", class_=["table", "table-bordered"])
                body = table.find('tbody')
                rows = body.findAll('tr')
                for row in rows:
                    obj = self.map_row(row)
                    obj["type"] = e
                    units[obj["unit"]] = obj

        return self.generate_text(units, "Cirrus", True)

if __name__ == "__main__":
    dummy = {
        "unit": 3807,
        "type": "b4",
        "baths": 2,
        "sqft": 1215,
        "floor": 19,
        "rent": 4940
    }
    thicc = {
        "unit_number": '3706',
        "floor_plan_id": '16968',
        "display_area": "1215 wut",
        "display_price": "$11234"
    }
    apt = Stratus()
    apt.seen_listings[dummy["unit"]]=dummy
    print(apt.new_listings())
    print(apt.seen_listings)
