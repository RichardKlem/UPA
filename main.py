from src.data_downloader import DataDownloader
import src.loader
import json

if __name__ == "__main__":
    Downloader = DataDownloader()
    Downloader.download()

    # TODO Connect with downloader
    okresy = '<PATH TO THE DATA FILE>>'
    okresy_name = 'prehled'

    with open(okresy, encoding='utf-8') as f:
        file_data = json.load(f)
        if not isinstance(file_data, list):
            file_data = [file_data]
        src.loader.load_data(collection_name=okresy_name, data=file_data)

