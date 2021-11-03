import csv
import json
import os
import re
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup


class DataHandler:
    def __init__(self, url="https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/",
                 folder="data",
                 listOfFiles=[]) -> None:
        self.url = url
        self.folder = Path(folder)
        self.listOfFiles = listOfFiles
        pass

    """
    Module: download
    Function: downloads csv files with data from the page
    """

    def download(self):
        headers = {'User-Agent': 'Mozilla/5.0', }

        os.makedirs(self.folder, exist_ok=True)

        # Gets HTML form of a page.
        # r = requests.get(self.url, headers=headers, allow_redirects=True)
        # soup = BeautifulSoup(r.content, "html.parser")

        # Gets names of csv files from page.
        # CsvFiles = []
        # for file in re.findall(r'"url":"[1-9a-z-]*.csv', str(soup)):
        #     CsvFiles.append(file[7:])

        # if numberOfFiles:
        #     numberOfFiles = min(numberOfFiles, len(CsvFiles))
        # else:
        #     numberOfFiles = len(CsvFiles)
        # cnt = 0

        # Saves csv file into data folder.
        for csvFileName in self.listOfFiles:
            # if cnt >= numberOfFiles:
            #     break

            csvFilePath = Path(os.path.join(self.folder, csvFileName+".csv"))
            jsonFilePath = csvFilePath.with_suffix('.json')

            # print(f"\rJSON files created: {cnt}/{numberOfFiles}", end='', flush=True)
            # cnt += 1

            # Do not download or convert the json file if it already exists.
            if not os.path.isfile(jsonFilePath):
                # Do not download the csv file if it already exists.
                if not os.path.isfile(csvFilePath):
                    if csvFileName == "130142-21data043021":
                        r = requests.get("https://www.czso.cz/documents/62353418/143522504/130142-21data043021.csv/760fab9c-d079-4d3a-afed-59cbb639e37d?version=1.1")
                    else:
                        r = requests.get(self.url + csvFileName+".csv")
                    open(csvFilePath, 'wb').write(r.content)

                # Fast transforming, but RAM expensive.
                """
                # transform csv file to json
                data = pandas.DataFrame()
                # chunksize == 10000 ~~ up to 9GB of RAM
                for chunk in pandas.read_csv(csvFilePath, chunksize=50000):
                    chunk.to_json(jsonFilePath, orient = "records", indent=4)

                    #data = pandas.concat([data, chunk], ignore_index=True)

                    data.to_json(jsonFilePath, orient = "records", indent=4)
                """

                # Slow transforming, but does not run out of RAM (max RAM usage around 6GB).
                """
                with open(csvFilePath, 'r+', encoding='utf-8-sig') as csvFile:
                    reader = csv.DictReader(csvFile)

                    with open(jsonFilePath, 'a+') as jsonFile:
                        jsonFile.write("[")
                        json.dump(reader.__next__(), jsonFile, indent=2)
                        for row in reader:
                            jsonFile.write(',\n')
                            json.dump(row, jsonFile, indent=2)
                        jsonFile.write("]")
                """

                if csvFileName == self.listOfFiles[0]:
                    df = pd.read_csv(csvFilePath, usecols = ["datum", "vek", "pohlavi", "kraj_nuts_kod", "okres_lau_kod"])
                    df.to_json(jsonFilePath, orient = "records")
                elif csvFileName == self.listOfFiles[1]:
                    df = pd.read_csv(csvFilePath, usecols = ["datum", "pocet_hosp"])
                    df.to_json(jsonFilePath, orient = "records")
                elif csvFileName == self.listOfFiles[2]:
                    df = pd.read_csv(csvFilePath, usecols = ["datum", "kraj_nuts_kod", "okres_lau_kod", "prirustkovy_pocet_testu_okres", "prirustkovy_pocet_testu_kraj"])
                    df.to_json(jsonFilePath, orient = "records")
                # elif csvFileName == self.listOfFiles[3]:
                # ockovani-zakladni-prehled
                #     df = pd.read_csv(csvFilePath, usecols = ["poradi_davky", "vakcina", "vekova_skupina", "orp_bydliste_kod"])
                #     df.to_json(jsonFilePath)
                # elif csvFileName == self.listOfFiles[3]:
                # ockovani
                # df = pd.read_csv(csvFilePath, usecols = ["poradi_davky", "vakcina", "vekova_skupina", "orp_bydliste_kod"])
                # df.to_json(jsonFilePath)
                elif csvFileName == self.listOfFiles[3]:
                    df = pd.read_csv(csvFilePath, usecols = ["datum", "kraj_nuts_kod"])
                    df.to_json(jsonFilePath, orient = "records")
                elif csvFileName == self.listOfFiles[4]:
                    df = pd.read_csv(csvFilePath, usecols = ["datum", "poradi_davky", "vakcina", "vekova_skupina", "orp_bydliste_kod", "kraj_nuts_kod", "kraj_nazev", "pohlavi"])
                    df.to_json(jsonFilePath, orient = "records")
                elif csvFileName == self.listOfFiles[5]:
                    df = pd.read_csv(csvFilePath, usecols = ["datum", "kraj_nuts_kod"])
                    df.to_json(jsonFilePath, orient = "records")
                elif csvFileName == self.listOfFiles[6]:
                    df = pd.read_csv(csvFilePath, usecols = ["hodnota", "vek_txt", "vuzemi_txt"])
                    df.to_json(jsonFilePath, orient = "records")
                else:
                    df = pd.read_csv(csvFilePath, usecols = ["datum"])
                    df.to_json(jsonFilePath, orient = "records")

            # print(f"\rJSON files created: {cnt}/{numberOfFiles}", end='', flush=True)
        # print('')  # Print a new line after last processed file.


if __name__ == "__main__":
    Handler = DataHandler()
    Handler.download()
