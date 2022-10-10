from typing import List

import requests, json, pandas as pd


class NobelPriceParser:
    def __init__(self):
        # Getting data for laureate
        self.res_laureate = requests.get("http://api.nobelprize.org/v1/laureate.json")
        self.json_data_laureate = json.loads(self.res_laureate.content.decode('utf-8'))

        self.res_country = requests.get("http://api.nobelprize.org/v1/country.json")
        self.json_data_country = json.loads(self.res_country.content.decode('utf-8'))

        # print(type(self))
        self.laureate_dataframe = pd.json_normalize(self.json_data_laureate['laureates'])
        self.country_dataframe = pd.json_normalize(self.json_data_country['countries'])

    def debug(self):
        print(self.laureate_dataframe)

    def parser(self):
        self.laureate_dataframe["name"] = self.laureate_dataframe["firstname"] + " " + self.laureate_dataframe[
            "surname"]
        self.laureate_dataframe = self.laureate_dataframe.rename({"born": "dob"})
        d = self.laureate_dataframe.loc[0, "prizes"]

        self.laureate_dataframe["unique_prize_years"] = self.laureate_dataframe["prizes"].apply(
            lambda x: self.concat_data(prize=x, prize_key="year"))
        self.laureate_dataframe["unique_prize_categories"] = self.laureate_dataframe["prizes"].apply(
            lambda x: self.concat_data(prize=x, prize_key="category"))
        print(self.laureate_dataframe)

    def concat_data(self, prize: List[dict], prize_key: str) -> str:
        res = [i.get(prize_key) for i in prize if i.get(prize_key)]
        return ";".join(res) if res else pd.NA


if __name__ == '__main__':
    npp = NobelPriceParser()
    npp.parser()
    # npp.view_laureate()
    # res = requests.get("http://api.nobelprize.org/v1/laureate.json")
    # print(json.loads(res.content.decode("utf-8")))
