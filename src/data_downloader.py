import csv
import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


class DataDownloader:
    def __init__(self, url="https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/",
                 folder="data") -> None:
        self.url = url
        self.folder = Path(folder)
        pass

    """
    Module: download
    Function: downloads csv files with data from the page
    """

    def download(self, number_of_files: int = None):
        headers = {'User-Agent': 'Mozilla/5.0', }

        os.makedirs(self.folder, exist_ok=True)

        # Gets HTML form of a page.
        r = requests.get(self.url, headers=headers, allow_redirects=True)
        soup = BeautifulSoup(r.content, "html.parser")

        # Gets names of csv files from page.
        CsvFiles = []
        for file in re.findall(r'"url":"[1-9a-z-]*.csv', str(soup)):
            CsvFiles.append(file[7:])

        if number_of_files:
            number_of_files = min(number_of_files, len(CsvFiles))
        else:
            number_of_files = len(CsvFiles)
        cnt = 0

        # Saves csv file into data folder.
        for csvFileName in CsvFiles:
            if cnt >= number_of_files:
                break

            csvFilePath = Path(os.path.join(self.folder, csvFileName))
            jsonFilePath = csvFilePath.with_suffix('.json')

            print(f"\rJSON files created: {cnt}/{number_of_files}", end='', flush=True)
            cnt += 1

            # Do not download or convert the json file if it already exists.
            if not os.path.isfile(jsonFilePath):
                # Do not download the csv file if it already exists.
                if not os.path.isfile(csvFilePath):
                    r = requests.get(self.url + csvFileName)
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
                with open(csvFilePath, 'r+', encoding='utf-8-sig') as csvFile:
                    reader = csv.DictReader(csvFile)

                    with open(jsonFilePath, 'a+') as jsonFile:
                        jsonFile.write("[")
                        json.dump(reader.__next__(), jsonFile, indent=2)
                        for row in reader:
                            jsonFile.write(',\n')
                            json.dump(row, jsonFile, indent=2)
                        jsonFile.write("]")

            print(f"\rJSON files created: {cnt}/{number_of_files}", end='', flush=True)
        print('')  # Print a new line after last processed file.


if __name__ == "__main__":
    Downloader = DataDownloader()
    Downloader.download()
