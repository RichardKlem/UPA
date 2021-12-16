import pandas as pd
from data_files import data_files
import matplotlib.pyplot as plt
import numpy as np


def outliers_iqr(data):
    quartile_1, quartile_3 = np.percentile(data, [25, 75])
    iqr = quartile_3 - quartile_1
    lower_bound = quartile_1 - (iqr * 1.5)
    upper_bound = quartile_3 + (iqr * 1.5)

    outliers = []

    for x in data:
        if (x > upper_bound) | (x < lower_bound):
            outliers += [x]

    return outliers


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


def B2_load_stats_for_last_12_month(csv_data, last_12_months_dates, vaccinated=False):
    choosed_county_nuts = "CZ010"
    choosed_county_name = "Hlavní město Praha"
    citizens_in_choosed_county = 1300000 #approximately
    citizens_in_cr = 10700000 #approximately

    stats = { "choosed_county": {}, "all_counties": {}}

    # remove day from date
    csv_data['datum'] = csv_data['datum'].str[:-3]

    # remove too old data
    csv_data.drop(csv_data[~csv_data.datum.isin(last_12_months_dates)].index, inplace=True)

    if vaccinated:
        # count only fully vaccinated and only once
        csv_data.drop(csv_data[(csv_data.poradi_davky != 2) & (csv_data.vakcina == "Comirnaty")].index, inplace=True)
        csv_data.drop(csv_data[(csv_data.poradi_davky != 2) & (csv_data.vakcina == "SPIKEVAX")].index, inplace=True)
        csv_data.drop(csv_data[(csv_data.poradi_davky != 2) & (csv_data.vakcina == "VAXZEVRIA")].index, inplace=True)
        csv_data.drop(csv_data[(csv_data.poradi_davky > 1) & (csv_data.vakcina == "COVID-19 Vaccine Janssen")].index, inplace=True)

    for month_date in last_12_months_dates:
        stats["choosed_county"][month_date] = len(csv_data[(csv_data.datum == month_date) & (csv_data.kraj_nuts_kod == choosed_county_nuts)])
        stats["all_counties"][month_date] = len(csv_data[csv_data.datum == month_date])

        # normalize data to number of citizens in county/czech republic
        stats["choosed_county"][month_date] *= (100 / citizens_in_choosed_county)
        stats["all_counties"][month_date] *= (100 / citizens_in_cr)

    return stats


class DataVisualizer:
    """ The class uses data in CSV format and creates a set of graphs which
        describe the data. """

    def __init__(self):
        pass

    def visualizeA1(self, output_path, output_path_tests, hospitalized_path, infected_path, tests_path, cured_path):
        print("Creating graph A1... ", end="", flush = True)

        hospitalized = pd.read_csv(hospitalized_path)
        infected = pd.read_csv(infected_path)
        tests = pd.read_csv(tests_path)
        cured = pd.read_csv(cured_path)

        # remove day from date
        hospitalized['datum'] = hospitalized['datum'].str[:-3]
        infected['datum'] = infected['datum'].str[:-3]
        tests['datum'] = tests['datum'].str[:-3]
        cured['datum'] = cured['datum'].str[:-3]

        hospitalized = hospitalized[(hospitalized.datum != '2021-12')]
        infected = infected[(infected.datum != '2021-12')]
        tests = tests[(tests.datum != '2021-12')]
        cured = cured[(cured.datum != '2021-12')]


        # sum value in month
        hospitalized = hospitalized.groupby('datum', as_index=False).sum() # dataframe
        infected = infected.groupby('datum').size() # series
        tests = tests.groupby('datum', as_index=False).sum() # dataframe
        cured = cured.groupby('datum').size() # series

        # add a line for each dataset -- hospitalized, infected and cured
        plt.figure(figsize=(10, 5))
        plt.plot(hospitalized["datum"], hospitalized["pocet_hosp"], label = "Počet hospitalizovaných")
        plt.plot(infected.index.tolist(), infected.values, label = "Počet nakažených")
        plt.plot(cured.index.tolist(), cured.values, label = "Počet vyléčených")

        plt.ylabel("Počet")
        plt.xticks(rotation=45)
        plt.title("Dotaz A1 - vývoj COVID situace")
        plt.legend(bbox_to_anchor=(0.02, 0.98), loc="upper left")

        plt.savefig(output_path, bbox_inches="tight")
        plt.close("all")

        # print tests in a different graph for better readability
        plt.figure(figsize=(7.7, 5))
        plt.plot(tests["datum"], tests["prirustkovy_pocet_testu_okres"], label = "Počet provedených testů")

        plt.ylabel("Počet")
        plt.xticks(rotation=45)
        plt.title("Dotaz A1 - vývoj COVID situace - počty provedených testů")

        plt.savefig(output_path_tests, bbox_inches="tight")
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

        # count only fully vaccinated
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "Comirnaty")].index, inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "SPIKEVAX")].index, inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "VAXZEVRIA")].index, inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky > 1) & (vaccinated.vakcina == "COVID-19 Vaccine Janssen")].index, inplace=True)

        # replace age attribute to 1 = age1, 2 = age2, 3 = age3
        vaccinated.loc[ (vaccinated.vekova_skupina == "0-11") |
                        (vaccinated.vekova_skupina == "12-15") |
                        (vaccinated.vekova_skupina == "16-17") |
                        (vaccinated.vekova_skupina == "18-24"), "vekova_skupina"] = 1

        vaccinated.loc[ (vaccinated.vekova_skupina == "25-29") |
                        (vaccinated.vekova_skupina == "30-34") |
                        (vaccinated.vekova_skupina == "35-39") |
                        (vaccinated.vekova_skupina == "40-44") |
                        (vaccinated.vekova_skupina == "45-49") |
                        (vaccinated.vekova_skupina == "50-54") |
                        (vaccinated.vekova_skupina == "55-59"), "vekova_skupina"] = 2

        vaccinated.loc[ (vaccinated.vekova_skupina == "60-64") |
                        (vaccinated.vekova_skupina == "65-69") |
                        (vaccinated.vekova_skupina == "70-74") |
                        (vaccinated.vekova_skupina == "75-79") |
                        (vaccinated.vekova_skupina == "80+"), "vekova_skupina"] = 3

        # for each county calculate stats
        for county_name in counties.keys():
            # all vaccinated
            stats["cnt"][county_name] = len(vaccinated[vaccinated.kraj_nazev == county_name])

            # all vaccinated men
            stats["men"][county_name] = len(vaccinated[(vaccinated.kraj_nazev == county_name) & (vaccinated.pohlavi == "M")])

            # all women
            stats["women"][county_name] = stats["cnt"][county_name] - stats["men"][county_name]

            # all age categories
            stats["age1"][county_name] = len(vaccinated[(vaccinated.kraj_nazev == county_name) & (vaccinated.vekova_skupina == 1)])
            stats["age2"][county_name] = len(vaccinated[(vaccinated.kraj_nazev == county_name) & (vaccinated.vekova_skupina == 2)])
            stats["age3"][county_name] = stats["cnt"][county_name] - (stats["age1"][county_name] + stats["age2"][county_name])


        x = np.arange(len(counties))

        # add data
        labels = list(counties.keys())
        labels.sort()
        data = [ stats["cnt"][county] for county in labels ]

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111)
        bar_cnt = ax.bar(x, data)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation = 45)

        plt.ylabel("Počet očkovaných")
        plt.title("Dotaz A3-1 - počty provedených očkování v jednotlivých krajích")

        ax.bar_label(bar_cnt)

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_county)
        plt.close("all")


        # add data
        labels = list(counties.keys())
        labels.sort()
        data_men = [ stats["men"][county] for county in labels ]
        data_women = [ stats["women"][county] for county in labels ]

        width=0.35
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_men = ax.bar(x - width/2, data_men, color = 'b', width=width)
        bar_women = ax.bar(x + width/2, data_women, color = 'r', width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation = 45)

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
        labels = list(counties.keys())
        labels.sort()
        data_age1 = [ stats["age1"][county] for county in labels ]
        data_age2 = [ stats["age2"][county] for county in labels ]
        data_age3 = [ stats["age3"][county] for county in labels ]

        width=0.28
        fig = plt.figure(figsize=(20, 7))
        ax = fig.add_subplot(111)
        bar_age1 = ax.bar(x - width, data_age1, color = '#00CED1', width=width)
        bar_age2 = ax.bar(x, data_age2, color = '#009ACD', width=width)
        bar_age3 = ax.bar(x + width, data_age3, color = '#104E8B', width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation = 45)

        plt.ylabel("Počet očkovaných")
        plt.title("Dotaz A3-3 - počty provedených očkování v jednotlivých krajích podle věku")
        handles = [ plt.Rectangle((0,0),1,1, color='#104E8B'),
                    plt.Rectangle((0,0),1,1, color='#009ACD'),
                    plt.Rectangle((0,0),1,1, color='#00CED1')]
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
        vaccinated_stats= B2_load_stats_for_last_12_month(vaccinated, last_12_months_dates, vaccinated=True)

        width=0.35
        x = np.arange(12)

        # add data
        labels = list(infected_stats["choosed_county"].keys())
        labels.sort()
        data_choosed_county = [ infected_stats["choosed_county"][month] for month in labels ]
        data_all_counties = [ infected_stats["all_counties"][month] for month in labels ]

        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width/2, data_choosed_county, color = "r", width=width)
        bar_all_counties = ax.bar(x + width/2, data_all_counties, color = "#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        plt.ylabel("Počet nakažených [%]")
        plt.title("Dotaz B2-1 - porovnání počtu nakažených Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0,0),1,1, color='r'), plt.Rectangle((0,0),1,1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_choosed_county, fmt='%.2f')
        ax.bar_label(bar_all_counties, fmt='%.2f')

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_infected)
        plt.close("all")

        # add data
        labels = list(dead_stats["choosed_county"].keys())
        labels.sort()
        data_choosed_county = [ dead_stats["choosed_county"][month] for month in labels ]
        data_all_counties = [ dead_stats["all_counties"][month] for month in labels ]

        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width/2, data_choosed_county, color = "#212121", width=width)
        bar_all_counties = ax.bar(x + width/2, data_all_counties, color = "#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        plt.ylabel("Počet zemřelých [%]")
        plt.title("Dotaz B2-2 - porovnání počtu zemřelých Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0,0),1,1, color='#212121'), plt.Rectangle((0,0),1,1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_choosed_county, fmt='%.3f')
        ax.bar_label(bar_all_counties, fmt='%.3f')

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_dead)
        plt.close("all")

        # add data
        labels = list(vaccinated_stats["choosed_county"].keys())
        labels.sort()
        data_choosed_county = [ vaccinated_stats["choosed_county"][month] for month in labels ]
        data_all_counties = [ vaccinated_stats["all_counties"][month] for month in labels ]

        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width/2, data_choosed_county, color = "#1E90FF", width=width)
        bar_all_counties = ax.bar(x + width/2, data_all_counties, color = "#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        plt.ylabel("Počet očkovaných [%]")
        plt.title("Dotaz B2-3 - porovnání počtu očkovaných Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0,0),1,1, color='#1E90FF'), plt.Rectangle((0,0),1,1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(1.04,0.5), loc="center left")

        ax.bar_label(bar_choosed_county, fmt='%.1f')
        ax.bar_label(bar_all_counties, fmt='%.1f')

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_vaccinated)
        plt.close("all")

        print("DONE")


    def visualizeV2(self, output_path, infected_path):
        print("Creating graph V1... ", end="", flush = True)

        infected = pd.read_csv(infected_path)

        infected['datum'] = infected['datum'].str[:-3]

        infected = infected[(infected.datum != '2021-12')]

        men = infected[(infected.pohlavi != 'M')]
        women = infected[(infected.pohlavi != 'Z')]

        men = men.groupby('datum').size() # series
        women = women.groupby('datum').size() # series

        all_women = 10700000 / 1.95
        all_men = 10700000 - all_women

        men = men.multiply(100/all_men)
        women = women.multiply(100/all_women)

        # add data
        plt.figure(figsize=(10, 5))
        plt.plot(men.index.tolist(), men.values, "b", label = "Muži")
        plt.plot(women.index.tolist(), women.values, "r", label = "Ženy")

        plt.ylabel("Počet nakažených [%]")
        plt.xticks(rotation=45)
        plt.title("Dotaz V2 - vývoj poměru nakažených jednotlivých pohlaví")
        plt.legend(bbox_to_anchor=(0.02, 0.98), loc="upper left")

        plt.savefig(output_path, bbox_inches="tight")
        plt.close("all")

        print("DONE")

    def visualizeC1(self, output_csv, infected_path, vaccinated_path, counties_stats_path, counties_codes_path, start_month):
        print("Creating data for C1... ", end="", flush = True)

        infected = pd.read_csv(infected_path)
        vaccinated = pd.read_csv(vaccinated_path)
        counties_stats = pd.read_csv(counties_stats_path)
        counties_codes = pd.read_csv(counties_codes_path)

        # remove day from date
        infected['datum'] = infected['datum'].str[:-3]
        vaccinated['datum'] = vaccinated['datum'].str[:-3]

        last_12_months_dates = get_12_last_months_dates(start_month)

        # remove data older than 1 year
        infected.drop(infected[~infected.datum.isin(last_12_months_dates)].index, inplace=True)
        vaccinated.drop(vaccinated[~vaccinated.datum.isin(last_12_months_dates)].index, inplace=True)

        # count only fully vaccinated
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "Comirnaty")].index, inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "SPIKEVAX")].index, inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "VAXZEVRIA")].index, inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky > 1) & (vaccinated.vakcina == "COVID-19 Vaccine Janssen")].index, inplace=True)

        infected = infected.groupby(['datum', 'okres_lau_kod']).size().reset_index(name='infected') # dataframe
        vaccinated = vaccinated.groupby(['datum', 'orp_bydliste_kod']).size().reset_index(name='vaccinated') # dataframe

        # replace date by 1, 2, 3 and 4 (quarters of the year)
        for df in [infected, vaccinated]:
            df.loc[ (df.datum == last_12_months_dates[0]) |
                    (df.datum == last_12_months_dates[1]) |
                    (df.datum == last_12_months_dates[2]), "datum"] = 4

            df.loc[ (df.datum == last_12_months_dates[3]) |
                    (df.datum == last_12_months_dates[4]) |
                    (df.datum == last_12_months_dates[5]), "datum"] = 3

            df.loc[ (df.datum == last_12_months_dates[6]) |
                    (df.datum == last_12_months_dates[7]) |
                    (df.datum == last_12_months_dates[8]), "datum"] = 2

            df.loc[ (df.datum == last_12_months_dates[9]) |
                    (df.datum == last_12_months_dates[10]) |
                    (df.datum == last_12_months_dates[11]), "datum"] = 1

            df.rename(columns={"datum": "quarter"}, inplace=True)

        infected = infected.groupby(['quarter', 'okres_lau_kod']).sum().reset_index() # dataframe
        vaccinated = vaccinated.groupby(['quarter', 'orp_bydliste_kod']).sum().reset_index() # dataframe

        # change orp_bydliste_kod to int
        vaccinated.orp_bydliste_kod = vaccinated.orp_bydliste_kod.astype(int)

        # use only stats from "2020-12-31"
        counties_stats.drop(counties_stats[counties_stats.casref_do != "2020-12-31"].index, inplace=True)

        # keep only rows where "pohlavi_kod" == nan, since its sum of all other values
        counties_stats = counties_stats[counties_stats['pohlavi_kod'].isna()]

        # "casref_do" and "pohlavi_kod" columns are not needed anymore
        counties_stats.drop(['casref_do', 'pohlavi_kod'], axis=1, inplace=True)

        to_remove = [   "Česká republika",
                        # "Hlavní město Praha", this is national county and also county (kraj i okres)
                        "Středočeský kraj",
                        "Jihočeský kraj",
                        "Plzeňský kraj",
                        "Karlovarský kraj",
                        "Ústecký kraj",
                        "Liberecký kraj",
                        "Královéhradecký kraj",
                        "Pardubický kraj",
                        "Kraj Vysočina",
                        "Jihomoravský kraj",
                        "Olomoucký kraj",
                        "Moravskoslezský kraj",
                        "Zlínský kraj"]

        # remove rows that are not counties
        counties_stats.drop(counties_stats[counties_stats.vuzemi_txt.isin(to_remove)].index, inplace=True)

        sum_stats = counties_stats[counties_stats.vek_txt.isna()].copy()
        age_stats = counties_stats[counties_stats.vek_txt.notna()].copy()

        # sort "vekova_skupina" into 3 categories -- 1-(0-24), 2-(25-59), 3-(60+)
        age_stats.loc[  (age_stats.vek_txt == "0 až 5 (více nebo rovno 0 a méně než 5)") |
                        (age_stats.vek_txt == "5 až 10 (více nebo rovno 5 a méně než 10)") |
                        (age_stats.vek_txt == "10 až 15 (více nebo rovno 10 a méně než 15)") |
                        (age_stats.vek_txt == "15 až 20 (více nebo rovno 15 a méně než 20)") |
                        (age_stats.vek_txt == "20 až 25 (více nebo rovno 20 a méně než 25)"), "vek_txt"] = 1

        age_stats.loc[  (age_stats.vek_txt == "25 až 30 (více nebo rovno 25 a méně než 30)") |
                        (age_stats.vek_txt == "30 až 35 (více nebo rovno 30 a méně než 35)") |
                        (age_stats.vek_txt == "35 až 40 (více nebo rovno 35 a méně než 40)") |
                        (age_stats.vek_txt == "40 až 45 (více nebo rovno 40 a méně než 45)") |
                        (age_stats.vek_txt == "45 až 50 (více nebo rovno 45 a méně než 50)") |
                        (age_stats.vek_txt == "50 až 55 (více nebo rovno 50 a méně než 55)") |
                        (age_stats.vek_txt == "55 až 60 (více nebo rovno 55 a méně než 60)"), "vek_txt"] = 2

        age_stats.loc[  (age_stats.vek_txt == "60 až 65 (více nebo rovno 60 a méně než 65)") |
                        (age_stats.vek_txt == "65 až 70 (více nebo rovno 65 a méně než 70)") |
                        (age_stats.vek_txt == "70 až 75 (více nebo rovno 70 a méně než 75)") |
                        (age_stats.vek_txt == "75 až 80 (více nebo rovno 75 a méně než 80)") |
                        (age_stats.vek_txt == "80 až 85 (více nebo rovno 80 a méně než 85)") |
                        (age_stats.vek_txt == "85 až 90 (více nebo rovno 85 a méně než 90)") |
                        (age_stats.vek_txt == "90 až 95 (více nebo rovno 90 a méně než 95)") |
                        (age_stats.vek_txt == "Od 95 (více nebo rovno 95)"), "vek_txt"] = 3

        # sum stats for each age group (1, 2, 3)
        age_stats = age_stats.groupby(['vek_txt', 'vuzemi_txt']).sum().reset_index() # dataframe

        # pick 50 counties with highest number of citizens
        choosed_counties_names = list(sum_stats.sort_values(by='hodnota', ascending=False).head(50)["vuzemi_txt"])

        output_data = pd.DataFrame([], columns=[    "okres_nazev",
                                                    "4_nakazeni",
                                                    "3_nakazeni",
                                                    "2_nakazeni",
                                                    "1_nakazeni",
                                                    "4_ockovani",
                                                    "3_ockovani",
                                                    "2_ockovani",
                                                    "1_ockovani",
                                                    "0_14_vek",
                                                    "15_59_vek",
                                                    "60_vek"])

        # remove duplicates and rows with missing values
        counties_codes.drop_duplicates(inplace=True)
        counties_codes.dropna(inplace=True)

        # add Prague manually since its missing
        counties_codes = counties_codes.append({"okres_lau_kod": "CZ0100", "okres_nazev": "Hlavní město Praha", "orp_kod": 1000}, ignore_index=True)

        # rename because of join
        vaccinated.rename(columns={"orp_bydliste_kod": "orp_kod"}, inplace=True)

        # we need county name instead of orp code or county code, so we have to join dataframes
        infected = infected.merge(counties_codes.drop(columns="orp_kod"), on="okres_lau_kod", how="left")
        vaccinated = vaccinated.merge(counties_codes.drop(columns="okres_lau_kod"), on="orp_kod", how="left")

        infected.drop_duplicates(inplace=True)
        vaccinated.drop_duplicates(inplace=True)

        infected.drop(columns="okres_lau_kod", inplace=True)
        vaccinated.drop(columns="orp_kod", inplace=True)

        infected = infected.groupby(['quarter', 'okres_nazev']).sum().reset_index() # dataframe
        vaccinated = vaccinated.groupby(['quarter', 'okres_nazev']).sum().reset_index() # dataframe

        # for each choosed county load stats
        for county_name in choosed_counties_names:
            row = { "okres_nazev": county_name,
                    "4_nakazeni": infected.loc[(infected.quarter == 4) & (infected.okres_nazev == county_name), 'infected'].iloc[0],
                    "3_nakazeni": infected.loc[(infected.quarter == 3) & (infected.okres_nazev == county_name), 'infected'].iloc[0],
                    "2_nakazeni": infected.loc[(infected.quarter == 2) & (infected.okres_nazev == county_name), 'infected'].iloc[0],
                    "1_nakazeni": infected.loc[(infected.quarter == 1) & (infected.okres_nazev == county_name), 'infected'].iloc[0],
                    "4_ockovani": vaccinated.loc[(vaccinated.quarter == 4) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                    "3_ockovani": vaccinated.loc[(vaccinated.quarter == 3) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                    "2_ockovani": vaccinated.loc[(vaccinated.quarter == 2) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                    "1_ockovani": vaccinated.loc[(vaccinated.quarter == 1) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                    "0_14_vek": age_stats.loc[(age_stats.vek_txt == 1) & (age_stats.vuzemi_txt == county_name), 'hodnota'].iloc[0],
                    "15_59_vek": age_stats.loc[(age_stats.vek_txt == 2) & (age_stats.vuzemi_txt == county_name), 'hodnota'].iloc[0],
                    "60_vek": age_stats.loc[(age_stats.vek_txt == 3) & (age_stats.vuzemi_txt == county_name), 'hodnota'].iloc[0] }

            output_data = output_data.append(row, ignore_index=True)

        # transform data from total number of infected/vaccinated to number of
        # infected/vaccinated per 1000 citizens for each county
        for county_name in output_data['okres_nazev']:
            all_citizens =  (output_data[output_data.okres_nazev == county_name]["0_14_vek"] +
                            output_data[output_data.okres_nazev == county_name]["15_59_vek"] +
                            output_data[output_data.okres_nazev == county_name]["60_vek"])
            normalisation_constant = all_citizens/1000

            for column_name in ["4_nakazeni", "3_nakazeni", "2_nakazeni", "1_nakazeni", "4_ockovani", "3_ockovani", "2_ockovani", "1_ockovani"]:
                new_value = output_data[output_data.okres_nazev == county_name][column_name] / normalisation_constant
                output_data.loc[output_data.okres_nazev == county_name, column_name] = new_value

        # check for outliers
        for column_name in ["4_nakazeni", "3_nakazeni", "2_nakazeni", "1_nakazeni", "4_ockovani", "3_ockovani", "2_ockovani", "1_ockovani"]:
            outliers = outliers_iqr(output_data[column_name])

            for x in outliers:
                # substitue each outlier by mean value of non-outlier values of the column
                output_data.loc[output_data[column_name] == x, column_name] = output_data[~output_data[column_name].isin(outliers)][column_name].mean()

        # normalize values by min-man method
        for column_name in ["4_nakazeni", "3_nakazeni", "2_nakazeni", "1_nakazeni", "4_ockovani", "3_ockovani", "2_ockovani", "1_ockovani"]:
            min = output_data[column_name].min()
            max = output_data[column_name].max()

            for county_name in output_data['okres_nazev']:
                new_value = (output_data[output_data.okres_nazev == county_name][column_name] - min) / (max - min)
                output_data.loc[output_data.okres_nazev == county_name, column_name] = new_value

        # discretize
        for column_name in ["4_ockovani", "3_ockovani", "2_ockovani", "1_ockovani"]:
            for county_name in output_data['okres_nazev']:
                curr_value = output_data[output_data.okres_nazev == county_name][column_name].iloc[0]
                new_value = None

                if 0.0 <= curr_value < 0.3:
                    new_value = "nízká"
                if 0.3 <= curr_value < 0.7:
                    new_value = "střední"
                if 0.7 <= curr_value <= 1.0:
                    new_value = "vysoká"

                output_data.loc[output_data.okres_nazev == county_name, column_name] = new_value

        output_data.to_csv(output_csv, index=False)

        print("DONE")
