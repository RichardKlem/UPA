import requests, os, re, sys, json, csv
from bs4 import BeautifulSoup


class DataDownloader:
    def __init__(self, url="https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/",
                       folder = "data") -> None:
        self.url = url
        self.folder = folder
        pass


    """
    Module: download
    Function: downloads csv files with data from the page
    """
    def download(self):
        headers = {'User-Agent': 'Mozilla/5.0',}

        #checks if folder data exists
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder)

        # gets HTML form of a page
        r = requests.get(self.url, headers = headers, allow_redirects = True)
        soup = BeautifulSoup(r.content, "html.parser")

        # gets names of csv files from page
        CsvFiles = []
        for file in re.findall(r'"url":"[1-9a-z-]*.csv', str(soup)):
            CsvFiles.append(file[7:])

        cnt = 0

        # saves csv file into folder data
        for csvFileName in CsvFiles:
            csvFilePath = self.folder + '/' + csvFileName
            jsonFilePath = csvFilePath.split(".csv")[0] + ".json"

            sys.stdout.write(f"\rJSON files created: {cnt}/{len(CsvFiles)}")
            sys.stdout.flush()
            cnt += 1

            # do not download or tranform the json file if it already exists
            if not os.path.isfile(jsonFilePath):
                # do not download the csv file if it already exists
                if not os.path.isfile(csvFilePath):
                    # downloads a total of 4.5 GB of data,
                    # so there is an interruption to test and prevent all data downloads.
                    # Maybe we can download one file, insert the data into DB and after that move on to the next file and delet the previous one
                    r = requests.get(self.url + csvFileName)
                    open(csvFilePath, 'wb').write(r.content)

                # fast transforming, but RAM expensive
                """
                # transform csv file to json
                data = pandas.DataFrame()
                # chunksize == 10000 ~~ up to 9GB of RAM
                for chunk in pandas.read_csv(csvFilePath, chunksize=50000):
                    chunk.to_json(jsonFilePath, orient = "records", indent=4)

                    #data = pandas.concat([data, chunk], ignore_index=True)

                    data.to_json(jsonFilePath, orient = "records", indent=4)
                """

                # slow transforming, but does not run out of RAM (max RAM usage around 6GB)
                with open(csvFilePath, 'r', encoding='utf-8-sig') as csvFile:
                    reader = csv.DictReader(csvFile)

                    with open(jsonFilePath, 'a') as jsonFile:
                        jsonFile.write("[")
                        for row in reader:
                            json.dump(row, jsonFile, indent=2)
                            jsonFile.write(',\n')

                        # remove trailing comma and EOL
                        jsonFile.truncate(jsonFile.tell() - 2)
                        jsonFile.write("]")
                # os.remove(csvFilePath)

        sys.stdout.write(f"\rJSON files created: {cnt}/{len(CsvFiles)}\n")


if __name__ == "__main__":
    Downloader = DataDownloader()
    Downloader.download()
