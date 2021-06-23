from bs4 import BeautifulSoup
import requests
import json


class ApartmentBase:
    def __init__(self):
        self.seen_listings = {}

    def new_listings(self):
        return "Im unimplemented!"


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

        for number, info in units.items():
            if number not in self.seen_listings:
                if ret is None:
                    ret = "KIARA LISTING(s):\n"
                self.seen_listings[number] = info
                formatted = "Unit {} available {}, {} sqft for ${}/month on floor {}\n".format(info["unit"], info["available"], info["sqft"], info["rent"], info["floor"])
                ret += formatted
        for number, u in dict(self.seen_listings).items():
            if number not in units:
                rem += "Unit {}, {} sqft, ${} no longer available\n".format(u["unit"], u["sqft"], u["rent"])
                del self.seen_listings[number]
            elif units[number]["rent"] != u["rent"]:
                rem += "Unit {}, {} sqft, went from ${} to ${}\n".format(u["unit"], u["sqft"], units[number]["rent"], u["rent"])
                self.seen_listings[number] = u

        if ret is None and len(rem) > 0:
            ret = "KIARA LISTING(s):\n"
            ret += "\n{}".format(rem)
        elif ret is not None and len(rem) > 0:
            ret += "\n{}".format(rem)
        return ret

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
        ret = None
        rem = ""
        units = {}
        for e in self.URL_exts:
            req = requests.get(self.URL_BASE + e)
            soup = BeautifulSoup(req.content, 'html.parser')
            if b'Units are not available under selected Floor plan(s)' not in req.content:
                table = soup.find("table", class_=["table", "table-bordered"])
                body = table.find('tbody')
                rows = body.findAll('tr')
                these_units = {}

                for row in rows:
                    obj = self.map_row(row)
                    obj["type"] = e
                    these_units[obj["unit"]] = obj
                for number, info in these_units.items():
                    if number not in self.seen_listings:
                        self.seen_listings[number] = info
                        if ret is None:
                            ret = "STRATUS LISTING(s):\n"
                        formatted = "{} unit {} available {}, {} sqft with rent range of {}\n".format(e, info["unit"], info["available"], info["sqft"], info["rent"])
                        ret += formatted
                units.update(these_units)
            else:
                print("No {} units".format(e))
        for number, u in dict(self.seen_listings).items():
            if number not in units:
                rem += "{} unit {}, {} sqft, ${} no longer available\n".format(u["type"], u["unit"], u["sqft"], u["rent"])
                del self.seen_listings[number]
            elif units[number]["rent"] != u["rent"]:
                rem += "{} unit {} went from [{}] to [{}]".format(u["type"], u["unit"], u["rent"], units[number]["rent"])
                self.seen_listings[number] = units[number]

        if ret is None and len(rem) > 0:
            ret = "STRATUS LISTING(s):\n"
            ret += rem
        elif ret is not None and len(rem) > 0:
            ret += rem
        return ret

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
        for f in fp:
            if f["bedroom_count"] == 2 and f["bathroom_count"] == 2:
                floor_plans[f["id"]] = f


        for u in units:
            if u["floor_plan_id"] in floor_plans and u["unit_number"] not in self.seen_listings:
                self.seen_listings[u["unit_number"]] = u
                if ret is None:
                    ret = "McKenzie LISTING(s)\n"
                formatted = "unit {} {}, {} sqft with rent of ${}\n".format(u["unit_number"], u["display_available_on"], u["display_area"].split(" ")[0], u["display_price"][1:])
                ret += formatted
        for number, u in dict(self.seen_listings).items():
            if u["floor_plan_id"] not in floor_plans:
                rem += "unit {}, {} sqft ${} no longer available\n".format(u["unit_number"], u["display_area"].split(" ")[0], u["display_price"][1:])
                del self.seen_listings[number]
            else:
                for old in units:
                    if old["unit_number"] == number and old["display_price"] != u["display_price"]:
                        rem += "Unit {}, {} sqft went from ${} to ${}".format(u["unit_number"], u["display_area"].split(" ")[0],u["display_price"][1:], old["display_price"][1:])
                        self.seen_listings[number] = old


        if ret is None and len(rem) > 0:
            ret = "McKenzie LISTING(s):\n"
            ret += rem
        elif ret is not None and len(rem) > 0:
            ret += rem
        return ret


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
                these_units = {}
                for row in rows:
                    obj = self.map_row(row)
                    obj["type"] = e
                    these_units[obj["unit"]] = obj
                for number, info in these_units.items():
                    if number not in self.seen_listings:
                        self.seen_listings[number] = info
                        if ret is None:
                            ret = "Cirrus LISTING(s):\n"
                        formatted = "{} unit {} available {}, {} sqft with rent range of {}\n".format(e, info["unit"], info["available"], info["sqft"], info["rent"])
                        ret += formatted
                units.update(these_units)
            else:
                print("No {} units".format(e))
        for number, u in self.seen_listings.items():
            if number not in units:
                rem += "{} unit {}, {} sqft, ${} no longer available\n".format(u["type"], u["unit"], u["sqft"], u["rent"])
                del self.seen_listings[number]
            elif units[number]["rent"] != u["rent"]:
                rem += "{} unit {} went from [{}] to [{}]".format(u["type"], u["unit"], u["rent"], units[number]["rent"])
                self.seen_listings[number] = units[number]

        if ret is None and len(rem) > 0:
            ret = "Cirrus LISTING(s):\n"
            ret += rem
        elif ret is not None and len(rem) > 0:
            ret += rem
        return ret




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
    apt = Cirrus()
    apt.seen_listings[dummy["unit"]]=dummy
    print(apt.new_listings())
