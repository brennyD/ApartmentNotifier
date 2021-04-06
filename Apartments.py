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
        ret = "NEW KIARA LISTING(s):\n"
        for r in data:
            info = self.map_row(r)
            if info["type"] == "2 Bedroom" and info["unit"] not in self.seen_listings:
                self.seen_listings.append(info["unit"])
                formatted = "{} unit {}, {} sqft for ${}/month on floor {}\n".format(info["type"], info["unit"], info["sqft"], info["rent"], info["floor"])
                ret += formatted


        return ret

class Stratus(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)

    def new_listings(self):
        return ""

class McKenzie(ApartmentBase):
    def __init__(self):
        ApartmentBase.__init__(self)

    def new_listings(self):
        return ""




if __name__ == "__main__":
    k = Kiara()
    print(k.new_listings())
