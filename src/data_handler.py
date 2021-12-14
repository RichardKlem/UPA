import os
from pathlib import Path

import pandas as pd
import requests

from data_files import data_files


class DataHandler:
    def __init__(self,
                 data_folder="data",
                 list_of_files=[], redownload=False) -> None:
        self.folder = Path(data_folder)
        self.list_of_files = list_of_files
        self.redownload = redownload

    def download(self):
        os.makedirs(self.folder, exist_ok=True)

        # Saves csv file into data folder.
        for csv_file_name in self.list_of_files:
            csv_file_path = Path(os.path.join(self.folder, csv_file_name)).with_suffix(".csv")
            json_file_path = csv_file_path.with_suffix('.json')

            # Do not download or convert the json file if it already exists.
            if self.redownload or not os.path.isfile(json_file_path):
                # Do not download the csv file if it already exists.
                if self.redownload or not os.path.isfile(csv_file_path):
                    r = requests.get(data_files.get(csv_file_name).get('url') + csv_file_name + ".csv")
                    open(csv_file_path, 'wb').write(r.content)
                print(f"{csv_file_path} downloaded")

                self.save_as_json(csv_file_name, csv_file_path, json_file_path)

    @staticmethod
    def save_as_json(csv_file_name: Path, csv_file_path, json_file_path):
        df = pd.read_csv(csv_file_path, usecols=data_files.get(csv_file_name).get('columns'))
        df.to_json(json_file_path, orient="records")
        print(f"{json_file_path} was created")


if __name__ == "__main__":
    Handler = DataHandler()
    Handler.download()
