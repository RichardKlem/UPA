import json
import os
from pathlib import Path

import src.loader
from src.data_downloader import DataDownloader

if __name__ == "__main__":
    data_folder = 'data'
    data_file_names = 'data_file_names.txt'

    skip_download = False
    skip_insert = False
    number_of_files = None

    # Download data.
    if not skip_download:
        Downloader = DataDownloader(folder=data_folder)
        Downloader.download(number_of_files=number_of_files)

    # Insert data into database.
    if not skip_insert:
        root, _, files = os.walk(data_folder).__next__()

        # Get only JSON files
        files = list(filter(lambda filename: filename.endswith('.json'), files))
        with open(data_file_names, 'r') as f:
            selected_files = f.read().splitlines()

        # Load data into database.
        for file in files:
            if file + '.json' in selected_files:
                file = Path(os.path.join(root, file))
                collection_name = file.stem

                with open(file, 'r+') as f:
                    file_data = json.loads(f.read())
                    if not isinstance(file_data, list):
                        file_data = [file_data]
                    src.loader.load_data(collection_name=collection_name, data=file_data)
