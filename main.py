import json
import os
from pathlib import Path

import src.loader
from data_files import data_files
from src.data_handler import DataHandler
from src.data_visualizer import DataVisualizer
from src.mongo_to_dataframe import load_data

if __name__ == "__main__":
    data_folder = 'data'
    selected_files = list(data_files.keys())

    skip_download = True
    redownload_data = True
    skip_insert = True
    reinsert_data = True
    skip_data_extraction = False
    skip_visualize = True

    if not skip_download:
        Handler = DataHandler(data_folder=data_folder, list_of_files=selected_files, redownload=redownload_data)
        Handler.download()

    # Insert data into database.
    if not skip_insert:
        root, _, files = os.walk(data_folder).__next__()

        # Get JSON files.
        files = list(filter(lambda filename: filename.endswith('.json'), files))

        # Insert data into database.
        for file in files:
            file_name = Path(file).stem
            if file_name in selected_files:
                file = Path(os.path.join(root, file))
                with open(file, 'r+') as f:
                    file_data = json.loads(f.read())
                    if not isinstance(file_data, list):
                        file_data = [file_data]
                    if reinsert_data:
                        src.loader.load_data(collection_name=file_name, data=file_data, reinsert=True)
                    else:
                        src.loader.load_data(collection_name=file_name, data=file_data)


    # Extracts data from database and save them in CSV files into "data-part2" directory.
    if not skip_data_extraction:
        load_data()

    # Creates graphs which answer questions A1, A3, B2, V1 and V2. Furthermore it
    # prepares data for data mining task C1.
    if not skip_visualize:
        visualizer = DataVisualizer()
        visualizer.visualizeA1( "graphs/A1-statistiky.png",
                                "graphs/A1-testy.png",
                                "data-part2/A1-hospitalizace.csv",
                                "data-part2/A1-osoby.csv",
                                "data-part2/A1-kraj-okres-testy.csv",
                                "data-part2/A1-vyleceni.csv")

        visualizer.visualizeA3( "graphs/A3-kraje.png",
                                "graphs/A3-pohlavi.png",
                                "graphs/A3-vek.png",
                                "data-part2/A3-ockovani-profese.csv")

        visualizer.visualizeB2( "graphs/B2-nakazeni.png",
                                "graphs/B2-zemreli.png",
                                "graphs/B2-ockovani.png",
                                "data-part2/B2-osoby.csv",
                                "data-part2/B2-umrti.csv",
                                "data-part2/B2-ockovani-profese.csv",
                                "2021-11")

        visualizer.visualizeOwn("graphs/V1-nakazenych-podle-veku.png",
                                "data/osoby.csv",
                                "data/130142-21data043021.csv",
                                "data/obce.csv",
                                "Opava")

        visualizer.visualizeV2( "graphs/V2-nakazeni.png",
                                "data-part2/V2-osoby.csv")
