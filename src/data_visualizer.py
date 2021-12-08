import pandas as pd
from data_files import data_files
import matplotlib.pyplot as plt


class DataVisualizer:
    """ The class uses data in CSV format and creates a set of graphs which
        describe the data. """

    def __init__(self):
        pass

    def visualizeA1(self, output_path, hospitalized_path, infected_path, tests_path, cured_path):
        hospitalized = pd.read_csv(hospitalized_path)
        infected = pd.read_csv(infected_path)
        tests = pd.read_csv(tests_path)
        cured = pd.read_csv(cured_path)

        # remove day from date
        for i in hospitalized.index:
            hospitalized.at[i, 'datum'] = hospitalized.at[i, 'datum'][:-3]

        for i in infected.index:
            infected.at[i, 'datum'] = infected.at[i, 'datum'][:-3]

        for i in tests.index:
            tests.at[i, 'datum'] = tests.at[i, 'datum'][:-3]

        for i in cured.index:
            cured.at[i, 'datum'] = cured.at[i, 'datum'][:-3]

        # sum value in month
        hospitalized = hospitalized.groupby('datum', as_index=False).sum()
        infected = infected.groupby('datum', as_index=False).sum()
        tests = tests.groupby('datum', as_index=False).sum()
        cured = cured.groupby('datum', as_index=False).sum()

        # add a line for each dataset
        plt.plot(hospitalized["datum"], hospitalized["pocet"], label = "Počet hospitalizovaných")
        plt.plot(infected["datum"], infected["pocet"], label = "Počet nakažených")
        plt.plot(tests["datum"], tests["pocet"], label = "Počet provedených testů")
        plt.plot(cured["datum"], cured["pocet"], label = "Počet vyléčených")

        plt.ylabel("Počet")
        plt.title("Dotaz A1")
        plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left")

        plt.savefig(output_path, bbox_inches="tight")
