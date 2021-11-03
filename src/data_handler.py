import os
from pathlib import Path
import requests
import pandas as pd


class DataHandler:
    def __init__(self, url="https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/",
                 folder="data",
                 listOfFiles=[]) -> None:
        self.url = url
        self.folder = Path(folder)
        self.listOfFiles = listOfFiles

    """
    Module: download
    Function: downloads csv files with data from the page
    """
    def download(self):
        headers = {'User-Agent': 'Mozilla/5.0', }

        os.makedirs(self.folder, exist_ok=True)

        # Saves csv file into data folder.
        for csvFileName in self.listOfFiles:
            csvFilePath, jsonFilePath = self.getFilePath(csvFileName)

            # Do not download or convert the json file if it already exists.
            if not os.path.isfile(jsonFilePath):
                # Do not download the csv file if it already exists.
                if not os.path.isfile(csvFilePath):
                    if csvFileName == "130142-21data043021":
                        r = requests.get("https://www.czso.cz/documents/62353418/143522504/130142-21data043021.csv/760fab9c-d079-4d3a-afed-59cbb639e37d?version=1.1")
                    else:
                        r = requests.get(self.url + csvFileName+".csv")
                    open(csvFilePath, 'wb').write(r.content)

                self.saveAsJson(csvFileName, csvFilePath, jsonFilePath)


    """
    Module: getFilePath
    Function: creates a path to the file from the CSV name
    """
    def getFilePath(self, csvFileName):
        csvFilePath = Path(os.path.join(self.folder, csvFileName+".csv"))
        jsonFilePath = csvFilePath.with_suffix('.json')
        return csvFilePath, jsonFilePath


    """
    Module: saveAsJson
    Function: saves downloaded files into JSON format
    """
    def saveAsJson(self, csvFileName, csvFilePath, jsonFilePath):
        if csvFileName == self.listOfFiles[0]:
            df = pd.read_csv(csvFilePath, usecols = ["datum", "vek", "pohlavi",
                                                     "kraj_nuts_kod", "okres_lau_kod"])
            df.to_json(jsonFilePath, orient = "records")

        elif csvFileName == self.listOfFiles[1]:
            df = pd.read_csv(csvFilePath, usecols = ["datum", "pocet_hosp"])
            df.to_json(jsonFilePath, orient = "records")

        elif csvFileName == self.listOfFiles[2]:
            df = pd.read_csv(csvFilePath, usecols = ["datum", "kraj_nuts_kod",
                                                     "prirustkovy_pocet_testu_kraj"])
            df.to_json(jsonFilePath, orient = "records")

        elif csvFileName == self.listOfFiles[3]:
            df = pd.read_csv(csvFilePath, usecols = ["datum", "kraj_nuts_kod"])
            df.to_json(jsonFilePath, orient = "records")

        elif csvFileName == self.listOfFiles[4]:
            df = pd.read_csv(csvFilePath, usecols = ["datum", "poradi_davky", "vakcina",
                                                     "vekova_skupina", "orp_bydliste_kod",
                                                     "kraj_nuts_kod", "kraj_nazev", "pohlavi"])
            df.to_json(jsonFilePath, orient = "records")

        elif csvFileName == self.listOfFiles[5]:
            df = pd.read_csv(csvFilePath, usecols = ["kraj_nuts_kod", "kraj_nazev",
                                                     "okres_lau_kod", "okres_nazev",
                                                     "orp_kod"])
            df.to_json(jsonFilePath, orient = "records")

        elif csvFileName == self.listOfFiles[6]:
            df = pd.read_csv(csvFilePath, usecols = ["hodnota", "vek_txt", "vuzemi_txt"])
            df.to_json(jsonFilePath, orient = "records")

        else:
            df = pd.read_csv(csvFilePath, usecols = ["datum"])
            df.to_json(jsonFilePath, orient = "records")


if __name__ == "__main__":
    Handler = DataHandler()
    Handler.download()
