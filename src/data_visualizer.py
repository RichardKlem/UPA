import pandas as pd
from data_files import data_files
import matplotlib.pyplot as plt
import numpy as np


def get_12_last_months_dates(start_month_date):
    months_keys = []
    curr_month_date = start_month_date

    for i in range(0,12):
        months_keys += [curr_month_date]

        year = int(curr_month_date.split("-")[0])
        month = int(curr_month_date.split("-")[1])

        if month > 1:
            curr_month_date = f"{year}-{str(month-1).zfill(2)}"
        else:
            curr_month_date = f"{year-1}-{12}"

    return months_keys


def B2_load_stats_for_last_12_month(csv_data, last_12_months_dates):
    choosed_county_nuts = "CZ010"
    choosed_county_name = "Hlavní město Praha"
    citizens_in_choosed_county = 1300000 #approximately
    citizens_in_cr = 10700000 #approximately

    stats = { "choosed_county": {}, "all_counties": {}}

    for month_date in last_12_months_dates:
        stats["choosed_county"][month_date] = 0
        stats["all_counties"][month_date] = 0

    for row in csv_data.iterrows():
        data = row[1]
        month_date = data["datum"][:-3]

        if month_date not in last_12_months_dates:
            continue

        if data["kraj_nuts_kod"] == choosed_county_nuts:
            stats["choosed_county"][month_date] += 1

        stats["all_counties"][month_date] += 1


    # normalize data to number of citizens in county/czech republic
    for month_date in stats["all_counties"].keys():
        stats["choosed_county"][month_date] *= (100 / citizens_in_choosed_county)
        stats["all_counties"][month_date] *= (100 / citizens_in_cr)

    return stats


class DataVisualizer:
    """ The class uses data in CSV format and creates a set of graphs which
        describe the data. """

    def __init__(self):
        pass

    def visualizeA1(self, output_path, hospitalized_path, infected_path, tests_path, cured_path):
        print("Creating graph A1... ", end="", flush = True)

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
        plt.title("Dotaz A1 - vývoj COVID situace")
        plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left")

        plt.savefig(output_path, bbox_inches="tight")
        plt.close("all")

        print("DONE")


    def visualizeA3(self, output_path_county, output_path_sex, output_path_age, vaccinated_path):
        print("Creating graph A3... ", end="", flush = True)

        vaccinated = pd.read_csv(vaccinated_path)

        counties = {
            "Hlavní město Praha": 0,
            "Středočeský kraj": 0,
            "Jihočeský kraj": 0,
            "Plzeňský kraj": 0,
            "Karlovarský kraj": 0,
            "Ústecký kraj": 0,
            "Liberecký kraj": 0,
            "Královéhradecký kraj": 0,
            "Pardubický kraj": 0,
            "Kraj Vysočina": 0,
            "Jihomoravský kraj": 0,
            "Olomoucký kraj": 0,
            "Zlínský kraj": 0,
            "Moravskoslezský kraj": 0
        }

        stats = {
            "cnt": counties.copy(),
            "men": counties.copy(),
            "women": counties.copy(),
            "age1": counties.copy(),
            "age2": counties.copy(),
            "age3": counties.copy()
        }

        for row in vaccinated.iterrows():
            data = row[1]
            stats["cnt"][data["kraj_nazev"]] += 1

            if data["pohlavi"] == "M":
                stats["men"][data["kraj_nazev"]] += 1
            else:
                stats["women"][data["kraj_nazev"]] += 1

            if data["vekova_skupina"] in ("60-64", "65-69", "70-74", "75-79", "80+"):
                stats["age3"][data["kraj_nazev"]] += 1
            elif data["vekova_skupina"] in ("25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59"):
                stats["age2"][data["kraj_nazev"]] += 1
            else:
                stats["age1"][data["kraj_nazev"]] += 1

        x = np.arange(len(counties))

        # add data
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111)
        bar_cnt = ax.bar(counties.keys(), list(stats["cnt"].values()))
        ax.set_xticks(x)
        ax.set_xticklabels(counties.keys(), rotation = 45)

        plt.ylabel("Počet očkovaných")
        plt.title("Dotaz A3-1 - počty provedených očkování v jednotlivých krajích")

        ax.bar_label(bar_cnt)

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_county)
        plt.close("all")


        # add data
        width=0.35
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_men = ax.bar(x - width/2, list(stats["men"].values()), color = 'b', width=width)
        bar_women = ax.bar(x + width/2, list(stats["women"].values()), color = 'r', width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(counties.keys(), rotation = 45)

        plt.ylabel("Počet očkovaných")
        plt.title("Dotaz A3-2 - počty provedených očkování v jednotlivých krajích podle pohlaví")
        handles = [plt.Rectangle((0,0),1,1, color='blue'), plt.Rectangle((0,0),1,1, color='red')]
        plt.legend(handles, ("Muži", "Ženy"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_men)
        ax.bar_label(bar_women)

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_sex)
        plt.close("all")


        # add data
        width=0.28
        fig = plt.figure(figsize=(20, 7))
        ax = fig.add_subplot(111)
        bar_age1 = ax.bar(x - width, list(stats["age1"].values()), color = '#00BFFF', width=width)
        bar_age2 = ax.bar(x, list(stats["age2"].values()), color = '#00688B', width=width)
        bar_age3 = ax.bar(x + width, list(stats["age3"].values()), color = '#104E8B', width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(counties.keys(), rotation = 45)

        plt.ylabel("Počet očkovaných")
        plt.title("Dotaz A3-3 - počty provedených očkování v jednotlivých krajích podle věku")
        handles = [ plt.Rectangle((0,0),1,1, color='#104E8B'),
                    plt.Rectangle((0,0),1,1, color='#00688B'),
                    plt.Rectangle((0,0),1,1, color='#00BFFF')]
        plt.legend(handles, ("60+", "25-59", "0-24"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_age1)
        ax.bar_label(bar_age2)
        ax.bar_label(bar_age3)

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_age)
        plt.close("all")

        print("DONE")


    def visualizeB2(self, output_path_infected, output_path_dead, output_path_vaccinated, infected_path, dead_path, vaccinated_path, start_month):
        print("Creating graph B2... ", end="", flush = True)

        infected = pd.read_csv(infected_path)
        dead = pd.read_csv(dead_path)
        vaccinated = pd.read_csv(vaccinated_path)

        last_12_months_dates = get_12_last_months_dates(start_month)

        infected_stats = B2_load_stats_for_last_12_month(infected, last_12_months_dates)
        dead_stats = B2_load_stats_for_last_12_month(dead, last_12_months_dates)
        vaccinated_stats= B2_load_stats_for_last_12_month(vaccinated, last_12_months_dates)

        width=0.35
        x = np.arange(12)

        # add data
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width/2, list(infected_stats["choosed_county"].values()), color = "r", width=width)
        bar_all_counties = ax.bar(x + width/2, list(infected_stats["all_counties"].values()), color = "#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(last_12_months_dates)

        plt.ylabel("Počet nakažených [%]")
        plt.title("Dotaz B2-1 - porovnání počtu nakažených Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0,0),1,1, color='r'), plt.Rectangle((0,0),1,1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_choosed_county)
        ax.bar_label(bar_all_counties)

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_infected)
        plt.close("all")

        # add data
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width/2, list(dead_stats["choosed_county"].values()), color = "#212121", width=width)
        bar_all_counties = ax.bar(x + width/2, list(dead_stats["all_counties"].values()), color = "#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(last_12_months_dates)

        plt.ylabel("Počet zemřelých [%]")
        plt.title("Dotaz B2-2 - porovnání počtu zemřelých Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0,0),1,1, color='#212121'), plt.Rectangle((0,0),1,1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_choosed_county)
        ax.bar_label(bar_all_counties)

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_dead)
        plt.close("all")

        # add data
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width/2, list(vaccinated_stats["choosed_county"].values()), color = "#1E90FF", width=width)
        bar_all_counties = ax.bar(x + width/2, list(vaccinated_stats["all_counties"].values()), color = "#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(last_12_months_dates)

        plt.ylabel("Počet očkovaných [%]")
        plt.title("Dotaz B2-3 - porovnání počtu očkovaných Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0,0),1,1, color='#1E90FF'), plt.Rectangle((0,0),1,1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_choosed_county)
        ax.bar_label(bar_all_counties)

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_vaccinated)
        plt.close("all")

        print("DONE")
