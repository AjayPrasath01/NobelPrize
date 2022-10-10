from typing import List

import json
import logging
import pandas as pd
import random
import requests

LOG_FILE = "log.log"

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s",
                    filename=LOG_FILE, filemode='w')


class NobelPriceParser:
    def __init__(self, laureate_url: str, country_url: str):
        """
        :arg laureate_url: url, country_url: url
        """
        # Getting response from url
        self.res_laureate = requests.get(laureate_url)
        self.res_country = requests.get(country_url)

        # Check for response from the url
        if self.res_laureate.status_code != 200:
            logging.exception("Response Status of laureate : " + self.res_laureate.status_code)
            print(
                f"There is a error with the laureate url {laureate_url} status code : {self.res_laureate.status_code}")
            exit()
        elif self.res_laureate.status_code != 200:
            logging.exception("Response Status of laureate : " + self.res_country.status_code)
            print(f"There is a error with the laureate url {laureate_url} status code : {self.res_country.status_code}")
            exit()
        # Convertig the response to dataframe
        self.laureate_dataframe = pd.json_normalize(json.loads(self.res_laureate.content.decode('utf-8'))['laureates'])
        self.country_dataframe = pd.json_normalize(json.loads(self.res_country.content.decode('utf-8'))['countries'])

    def parser(self):
        """
        No args requireds
        Funtion is called to process the data
        """
        self.laureate_dataframe["name"] = self.laureate_dataframe["firstname"] + " " + self.laureate_dataframe[
            "surname"]
        logging.debug("name column is created")

        self.laureate_dataframe.rename(columns={"born": "dob"}, inplace=True)
        logging.debug("born is renamed to dob")

        self.laureate_dataframe["unique_prize_years"] = self.laureate_dataframe["prizes"].apply(
            lambda x: self.concat_data(prize=x, prize_key="year"))
        logging.debug("unique_prize_years column is created")

        self.laureate_dataframe["unique_prize_categories"] = self.laureate_dataframe["prizes"].apply(
            lambda x: self.concat_data(prize=x, prize_key="category"))
        logging.debug("unique_prize_categories column is created")

        self.laureate_dataframe["born_country_code_mapped"] = self.laureate_dataframe["bornCountryCode"] \
            .apply(lambda x: self.born_country_code_mapper(country_code=x))
        logging.debug("born_country_code_mapped column is created")

        self.laureate_dataframe = self.laureate_dataframe[
            ["id", "name", "dob", "unique_prize_years", "unique_prize_categories", "gender",
             "born_country_code_mapped"]]
        self.laureate_dataframe.set_index("id", inplace=True)
        logging.debug("Selecting only required columns")

        logging.debug("parser completed successfully")

    def concat_data(self, prize: List[dict], prize_key: str) -> str:
        """
        :arg Prize column which is list of dictionaries
        :return string
        Helper function for concatenating data
        """
        res = [i.get(prize_key) for i in prize if i.get(prize_key)]
        return ";".join(res) if res else pd.NA

    def born_country_code_mapper(self, country_code: str):
        """
        :arg country_code: string
        """
        r = self.country_dataframe[self.country_dataframe["code"] == country_code]
        if r.size > 0:
            # Choosing random country as there are multiple countries
            # with the same symbol (mentioned in point 7 of assignment)
            r = r.head(random.randint(1, len(r)))
            return r["name"].values[0]
        else:
            return pd.NA

    def save(self, filename: str):
        self.laureate_dataframe.to_csv("out.csv")


if __name__ == '__main__':
    npp = NobelPriceParser(laureate_url="http://api.nobelprize.org/v1/laureate.json",
                           country_url="http://api.nobelprize.org/v1/country.json")
    npp.parser()
    npp.save(filename="out.csv")
