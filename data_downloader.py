import requests, os, csv, sys, re
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
        
        # saves csv file into folder data
        for file in CsvFiles:
            if not os.path.isfile(self.folder + '/' + file):
                r = requests.get(self.url + file)
                open(self.folder + '/' + file, 'wb').write(r.content)


if __name__ == "__main__":
    Downloader = DataDownloader()
    Downloader.download()