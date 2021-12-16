import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch

pd.options.mode.chained_assignment = None


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

    for i in range(0, 12):
        months_keys += [curr_month_date]

        year = int(curr_month_date.split("-")[0])
        month = int(curr_month_date.split("-")[1])

        if month > 1:
            curr_month_date = f"{year}-{str(month - 1).zfill(2)}"
        else:
            curr_month_date = f"{year - 1}-{12}"

    return months_keys


def B2_load_stats_for_last_12_month(csv_data, last_12_months_dates, vaccinated=False):
    choosed_county_nuts = "CZ010"
    choosed_county_name = "Hlavní město Praha"
    citizens_in_choosed_county = 1300000  # approximately
    citizens_in_cr = 10700000  # approximately

    stats = {"choosed_county": {}, "all_counties": {}}

    # remove day from date
    csv_data['datum'] = csv_data['datum'].str[:-3]

    # remove too old data
    csv_data.drop(csv_data[~csv_data.datum.isin(last_12_months_dates)].index, inplace=True)

    if vaccinated:
        # count only fully vaccinated and only once
        csv_data.drop(csv_data[(csv_data.poradi_davky != 2) & (csv_data.vakcina == "Comirnaty")].index, inplace=True)
        csv_data.drop(csv_data[(csv_data.poradi_davky != 2) & (csv_data.vakcina == "SPIKEVAX")].index, inplace=True)
        csv_data.drop(csv_data[(csv_data.poradi_davky != 2) & (csv_data.vakcina == "VAXZEVRIA")].index, inplace=True)
        csv_data.drop(csv_data[(csv_data.poradi_davky > 1) & (csv_data.vakcina == "COVID-19 Vaccine Janssen")].index,
                      inplace=True)

    for month_date in last_12_months_dates:
        stats["choosed_county"][month_date] = len(
            csv_data[(csv_data.datum == month_date) & (csv_data.kraj_nuts_kod == choosed_county_nuts)])
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

    def visualizeA1(self, output_path, hospitalized_path, infected_path, tests_path, cured_path):
        print("Creating graph A1... ", end="", flush=True)

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
        hospitalized = hospitalized.groupby('datum', as_index=False).sum()  # dataframe
        infected = infected.groupby('datum').size()  # series
        tests = tests.groupby('datum', as_index=False).sum()  # dataframe
        cured = cured.groupby('datum').size()  # series

        fig = plt.figure(figsize=(10, 10))
        ax1: plt.Axes = fig.add_subplot(2, 1, 1)
        ax2: plt.Axes = fig.add_subplot(2, 1, 2)

        plt.ticklabel_format(style='plain')

        # First subplot - hospitalized, infected, cured
        ax1.plot(hospitalized["datum"], hospitalized["pocet_hosp"], label="Počet hospitalizovaných")
        ax1.plot(infected.index.tolist(), infected.values, label="Počet nakažených")
        ax1.plot(cured.index.tolist(), cured.values, label="Počet vyléčených")

        ax1.set_title("Dotaz A1 - vývoj COVID situace")
        ax1.tick_params(axis="x", rotation=45)
        ax1.set_ylabel("Počet")
        ax1.set_xlabel("Datum")
        ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda y, p: format(int(y), ',')))
        ax1.grid(axis='y', linestyle='--')
        ax1.legend(bbox_to_anchor=(0.02, 0.98), loc="upper left")

        # Second subplot - tests
        ax2.plot(tests["datum"], tests["prirustkovy_pocet_testu_okres"], label="Počet provedených testů")

        ax2.set_title("Počty provedených testů")
        ax2.tick_params(axis="x", rotation=45)
        ax2.set_ylabel("Počet")
        ax2.set_xlabel("Datum")
        ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda y, p: format(int(y), ',')))
        ax2.grid(axis='y', linestyle='--')

        fig.tight_layout()
        plt.savefig(output_path)
        plt.close("all")

        print("DONE")

    def visualizeA3(self, output_path_county_sex, output_path_sex_age, vaccinated_path):
        print("Creating graph A3... ", end="", flush=True)

        vaccinated = pd.read_csv(vaccinated_path)

        # Count only fully vaccinated.
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "Comirnaty")].index,
                        inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "SPIKEVAX")].index,
                        inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "VAXZEVRIA")].index,
                        inplace=True)
        vaccinated.drop(
            vaccinated[(vaccinated.poradi_davky > 1) & (vaccinated.vakcina == "COVID-19 Vaccine Janssen")].index,
            inplace=True)

        # Replace age attribute to 1 = age1, 2 = age2, 3 = age3.
        vaccinated.loc[(vaccinated.vekova_skupina == "0-11") | (vaccinated.vekova_skupina == "12-15") | (
                vaccinated.vekova_skupina == "16-17") | (vaccinated.vekova_skupina == "18-24"), "vekova_skupina"] = 1

        vaccinated.loc[(vaccinated.vekova_skupina == "25-29") | (vaccinated.vekova_skupina == "30-34") | (
                vaccinated.vekova_skupina == "35-39") | (vaccinated.vekova_skupina == "40-44") | (
                               vaccinated.vekova_skupina == "45-49") | (vaccinated.vekova_skupina == "50-54") | (
                               vaccinated.vekova_skupina == "55-59"), "vekova_skupina"] = 2

        vaccinated.loc[(vaccinated.vekova_skupina == "60-64") | (vaccinated.vekova_skupina == "65-69") | (
                vaccinated.vekova_skupina == "70-74") | (vaccinated.vekova_skupina == "75-79") | (
                               vaccinated.vekova_skupina == "80+"), "vekova_skupina"] = 3

        # Create filtered DataFrames
        vaccinated_all = vaccinated.groupby(["kraj_nazev"]).size().reset_index(name="count")
        vaccinated_all["count"] = vaccinated_all["count"] / 1000
        vaccinated_all['count'] = vaccinated_all['count'].astype(int)

        vaccinated_sex_age = vaccinated.groupby(["kraj_nazev", "pohlavi", "vekova_skupina"]).size().reset_index(
            name="count")
        vaccinated_sex_age["count"] = vaccinated_sex_age["count"] / 1000
        vaccinated_sex_age['count'] = vaccinated_sex_age['count'].astype(int)

        vaccinated_age = vaccinated.groupby(["kraj_nazev", "vekova_skupina"]).size().reset_index(name="count")
        vaccinated_age["count"] = vaccinated_age["count"] / 1000
        vaccinated_age['count'] = vaccinated_age['count'].astype(int)

        vaccinated_sex = vaccinated.groupby(["kraj_nazev", "pohlavi"]).size().reset_index(name="count")
        vaccinated_sex["count"] = vaccinated_sex["count"] / 1000
        vaccinated_sex['count'] = vaccinated_sex['count'].astype(int)

        # -- Plotting -------
        # ---- First plot----
        fig: plt.Figure = plt.figure(figsize=(8, 9))
        ax1: plt.Axes = fig.add_subplot(2, 1, 1)
        ax2: plt.Axes = fig.add_subplot(2, 1, 2)

        fig.suptitle("Dotaz A3", fontsize=18)

        sns.barplot(ax=ax1, data=vaccinated_all, x="kraj_nazev", y="count", palette="Paired")
        ax1.tick_params(axis="x", rotation=45)
        ax1.set_ylabel("Počet očkovaných\nv tisících", fontsize=14)
        ax1.set_xlabel("")
        ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda y, p: format(int(y), ',')))
        ax1.grid(axis='y', linestyle='--')
        ax1.set_axisbelow(True)
        ax1.set_title("Počty provedených očkování v jednotlivých krajích")
        ax1.set_ylim(top=ax1.get_ylim()[1] * 1.05)

        # ---- Second plot ---
        palette = {'M': 'tab:blue', 'Z': 'tab:red', }
        sns.barplot(ax=ax2, data=vaccinated_sex, x="kraj_nazev", y="count", hue="pohlavi", palette=palette)
        ax2.tick_params(axis="x", rotation=45)
        ax2.set_ylabel("Počet očkovaných\nv tisících", fontsize=15)
        ax2.set_xlabel("")
        ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda y, p: format(int(y), ',')))
        ax2.grid(axis='y', linestyle='--')
        ax2.set_axisbelow(True)
        ax2.set_title("Počty provedených očkování v jednotlivých krajích podle pohlaví")
        patches = [Patch(color="tab:red", label="Ženy"),
                   Patch(color="tab:blue", label="Muži")]
        ax2.legend(title="Pohlaví", handles=patches, loc="upper right")
        ax2.set_ylim(top=ax2.get_ylim()[1] * 1.05)

        plt.tight_layout()
        fig.subplots_adjust(top=0.91, hspace=0.8, wspace=0.5)
        plt.savefig(output_path_county_sex)
        plt.close("all")

        # # ---- Third plot ----
        fig: plt.Figure = plt.figure(figsize=(10, 14))
        ax1: plt.Axes = fig.add_subplot(3, 1, 1)
        ax2: plt.Axes = fig.add_subplot(3, 1, 2)
        ax3: plt.Axes = fig.add_subplot(3, 1, 3)

        fig.suptitle("Dotaz A3-3: Počet očkovaných podle pohlaví a věku", fontsize=20)

        vac_male = vaccinated_sex_age[vaccinated_sex_age.pohlavi == "M"]
        vac_female = vaccinated_sex_age[vaccinated_sex_age.pohlavi == "Z"]

        sns.barplot(ax=ax1, data=vac_male, x="kraj_nazev", y="count", hue="vekova_skupina", palette="Blues_d")
        for container in ax1.containers:
            ax1.bar_label(container)
        ax1.grid(axis='y', linestyle='--')
        ax1.set_axisbelow(True)
        ax1.tick_params(axis="x", rotation=45)
        ax1.set_ylabel("Počet očkovaných\nv tisících", fontsize=13)
        ax1.set_xlabel("")
        ax1.set_title("Muži", fontsize=16)
        patches = [Patch(color=sns.color_palette("Blues_d")[0], label="0-24"),
                   Patch(color=sns.color_palette("Blues_d")[1], label="25-59"),
                   Patch(color=sns.color_palette("Blues_d")[2], label="60+")]
        ax1.legend(title="Věková skupina", handles=patches, loc="upper right")
        ax1.set_ylim(top=ax1.get_ylim()[1] * 1.05)

        sns.barplot(ax=ax2, data=vac_female, x="kraj_nazev", y="count", hue="vekova_skupina", palette="Reds")
        for container in ax2.containers:
            ax2.bar_label(container)
        ax2.grid(axis='y', linestyle='--')
        ax2.set_axisbelow(True)
        ax2.tick_params(axis="x", rotation=45)
        ax2.set_ylabel("Počet očkovaných\nv tisících", fontsize=13)
        ax2.set_xlabel("")
        ax2.set_title("Ženy", fontsize=16)
        patches = [Patch(color=sns.color_palette("Reds")[0], label="0-24"),
                   Patch(color=sns.color_palette("Reds")[1], label="25-59"),
                   Patch(color=sns.color_palette("Reds")[2], label="60+")]
        ax2.legend(title="Věková skupina", handles=patches, loc="upper right")
        ax2.set_ylim(top=ax2.get_ylim()[1] * 1.05)

        sns.barplot(ax=ax3, data=vaccinated_age, x="kraj_nazev", y="count", hue="vekova_skupina", palette="Set2")
        for container in ax3.containers:
            ax3.bar_label(container)
        ax3.grid(axis='y', linestyle='--')
        ax3.set_axisbelow(True)
        ax3.tick_params(axis="x", rotation=45)
        ax3.set_ylabel("Počet očkovaných\nv tisících", fontsize=13)
        ax3.set_xlabel("")
        ax3.set_title("Obě pohlaví", fontsize=16)
        patches = [Patch(color=sns.color_palette("Set2")[0], label="0-24"),
                   Patch(color=sns.color_palette("Set2")[1], label="25-59"),
                   Patch(color=sns.color_palette("Set2")[2], label="60+")]
        ax3.legend(title="Věková skupina", handles=patches, loc="upper right")
        ax3.set_ylim(top=ax3.get_ylim()[1] * 1.05)

        fig.tight_layout()
        fig.subplots_adjust(top=0.93, hspace=0.8)
        plt.savefig(output_path_sex_age)
        plt.close("all")

        print("DONE")

    def visualizeB2(self, output_path_infected, output_path_dead, output_path_vaccinated, infected_path, dead_path,
                    vaccinated_path, start_month):
        print("Creating graph B2... ", end="", flush=True)

        infected = pd.read_csv(infected_path)
        dead = pd.read_csv(dead_path)
        vaccinated = pd.read_csv(vaccinated_path)

        last_12_months_dates = get_12_last_months_dates(start_month)

        infected_stats = B2_load_stats_for_last_12_month(infected, last_12_months_dates)
        dead_stats = B2_load_stats_for_last_12_month(dead, last_12_months_dates)
        vaccinated_stats = B2_load_stats_for_last_12_month(vaccinated, last_12_months_dates, vaccinated=True)

        width = 0.35
        x = np.arange(12)

        # add data
        labels = list(infected_stats["choosed_county"].keys())
        labels.sort()
        data_choosed_county = [infected_stats["choosed_county"][month] for month in labels]
        data_all_counties = [infected_stats["all_counties"][month] for month in labels]

        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width / 2, data_choosed_county, color="r", width=width)
        bar_all_counties = ax.bar(x + width / 2, data_all_counties, color="#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        plt.ylabel("Počet nakažených [%]")
        plt.title("Dotaz B2-1 - porovnání počtu nakažených Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0, 0), 1, 1, color='r'), plt.Rectangle((0, 0), 1, 1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(0.02, 0.98), loc="upper left")

        ax.bar_label(bar_choosed_county, fmt='%.2f')
        ax.bar_label(bar_all_counties, fmt='%.2f')

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_infected)
        plt.close("all")

        # add data
        labels = list(dead_stats["choosed_county"].keys())
        labels.sort()
        data_choosed_county = [dead_stats["choosed_county"][month] for month in labels]
        data_all_counties = [dead_stats["all_counties"][month] for month in labels]

        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width / 2, data_choosed_county, color="#212121", width=width)
        bar_all_counties = ax.bar(x + width / 2, data_all_counties, color="#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        plt.ylabel("Počet zemřelých [%]")
        plt.title("Dotaz B2-2 - porovnání počtu zemřelých Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0, 0), 1, 1, color='#212121'), plt.Rectangle((0, 0), 1, 1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(0.02, 0.98), loc="upper left")

        ax.bar_label(bar_choosed_county, fmt='%.3f')
        ax.bar_label(bar_all_counties, fmt='%.3f')

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_dead)
        plt.close("all")

        # add data
        labels = list(vaccinated_stats["choosed_county"].keys())
        labels.sort()
        data_choosed_county = [vaccinated_stats["choosed_county"][month] for month in labels]
        data_all_counties = [vaccinated_stats["all_counties"][month] for month in labels]

        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(111)
        bar_choosed_county = ax.bar(x - width / 2, data_choosed_county, color="#1E90FF", width=width)
        bar_all_counties = ax.bar(x + width / 2, data_all_counties, color="#696969", width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        plt.ylabel("Počet očkovaných [%]")
        plt.title("Dotaz B2-3 - porovnání počtu očkovaných Hlavního města Prahy a ČR")
        handles = [plt.Rectangle((0, 0), 1, 1, color='#1E90FF'), plt.Rectangle((0, 0), 1, 1, color='#696969')]
        plt.legend(handles, ("Hlavní město Praha", "Česká Republika"), bbox_to_anchor=(0.02, 0.98), loc="upper left")

        ax.bar_label(bar_choosed_county, fmt='%.1f')
        ax.bar_label(bar_all_counties, fmt='%.1f')

        plt.axis('tight')
        plt.tight_layout()
        plt.savefig(output_path_vaccinated)
        plt.close("all")

        print("DONE")

    # source: https://stackoverflow.com/questions/43214978/seaborn-barplot-displaying-values
    # author: Secant Zhang
    # Date: Jun 26 '19 at 21:02
    def show_values_on_bars(self, axs, h_v="v", space=0.4):
        def _show_on_single_plot(ax):
            if h_v == "v":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() / 2
                    _y = p.get_y() + p.get_height()
                    value = int(p.get_height())
                    ax.text(_x, _y, value, ha="center")
            elif h_v == "h":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() + float(space)
                    _y = p.get_y() + p.get_height() - 0.3
                    value = float(p.get_width())
                    ax.text(_x, _y, value, ha="left", weight='bold')

        if isinstance(axs, np.ndarray):
            for idx, ax in np.ndenumerate(axs):
                _show_on_single_plot(ax)
        else:
            _show_on_single_plot(axs)

    def visualizeOwn(self, output_path, people_path, population_path, municipalities_path, district="Brno-město"):
        ###########################################################
        # edit zadani, ne za posledni rok ale za life time covidu #
        ###########################################################
        print("Creating graph V1... ", end="", flush=True)

        # gets data from the files
        df_people = pd.read_csv(people_path)
        df_pop = pd.read_csv(population_path)
        df_muni = pd.read_csv(municipalities_path)

        # gets lau code by the name of the district
        lau_kod = df_muni.loc[df_muni['okres_nazev'] == district, "okres_lau_kod"].iloc[0]

        # removing data that are not valid for our district
        df_infected = df_people.loc[df_people["okres_lau_kod"] == lau_kod]

        # splits data into age intervals
        df_infected["vek_skupina"] = pd.cut(df_infected.vek,
                                            [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90,
                                             95, float('inf')], include_lowest=True)
        df_infected = df_infected.groupby(["vek_skupina"])["vek_skupina"].count().reset_index(name="pocet")

        # renaming values that were not well written
        df_pop["vek_txt"] = df_pop["vek_txt"].replace(
            {'5 až 10 (více nebo rovno 5 a méně než 10)': '05 až 10 (více nebo rovno 5 a méně než 10)'})

        # removes duplicate values
        df_pop = df_pop.loc[df_pop["vuzemi_txt"] == district].loc[df_pop["pohlavi_txt"].isna()].loc[
            df_pop.vek_txt.notnull()].loc[df_pop.casref_do == "2020-12-31"]

        # group by the values
        df_pop = df_pop.groupby(["vek_txt"])["hodnota"].sum().reset_index(name="pocet")

        # redefining the data type
        df_infected = df_infected.astype({'pocet': 'float64'})

        # calculates the percentage of the values
        for i in range(len(df_pop.index)):
            result = round((df_infected.iloc[[i]].pocet / df_pop.iloc[[i]].pocet) * 100, 2)
            df_infected.loc[i:i, 'pocet'] = result

        # lables for the chart
        labels = ["0-5", "5-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "50-55",
                  "55-60", "60-65", "65-70", "70-75", "75-80", "80-85", "85-90", "90-95", ">95"]

        fig, ax = plt.subplots(1, 1, figsize=(7, 10), constrained_layout=True)

        # sets the data for the chart
        sns.barplot(palette="viridis", data=df_infected, x=df_infected.pocet, y=df_infected.vek_skupina,
                    ax=ax).set_title("Nakažení podle věkových skupin", fontsize=20, pad=10)

        # chart plotting
        ax.set(ylabel="Věk", xlabel="Nakaženžých [%]")
        ax.set_yticklabels(labels)

        # sets the values on the bars
        self.show_values_on_bars(ax, "h", -2.2)

        fig.savefig(output_path)

        plt.close(fig)

        print("DONE")

    def visualizeV2(self, output_path, infected_path):
        print("Creating graph V1... ", end="", flush=True)

        infected = pd.read_csv(infected_path)

        infected['datum'] = infected['datum'].str[:-3]

        infected = infected[(infected.datum != '2021-12')]

        men = infected[(infected.pohlavi != 'M')]
        women = infected[(infected.pohlavi != 'Z')]

        men = men.groupby('datum').size()  # series
        women = women.groupby('datum').size()  # series

        all_women = 10700000 / 1.95
        all_men = 10700000 - all_women

        men = men.multiply(100 / all_men)
        women = women.multiply(100 / all_women)

        # add data
        plt.figure(figsize=(10, 5))
        plt.plot(men.index.tolist(), men.values, "b", label="Muži")
        plt.plot(women.index.tolist(), women.values, "r", label="Ženy")

        plt.ylabel("Počet nakažených [%]")
        plt.xticks(rotation=45)
        plt.title("Dotaz V2 - vývoj poměru nakažených jednotlivých pohlaví")
        plt.legend(bbox_to_anchor=(0.02, 0.98), loc="upper left")

        plt.savefig(output_path, bbox_inches="tight")
        plt.close("all")

        print("DONE")

    def visualizeC1(self, output_csv, infected_path, vaccinated_path, counties_stats_path, counties_codes_path,
                    start_month):
        print("Creating data for C1... ", end="", flush=True)

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
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "Comirnaty")].index,
                        inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "SPIKEVAX")].index,
                        inplace=True)
        vaccinated.drop(vaccinated[(vaccinated.poradi_davky != 2) & (vaccinated.vakcina == "VAXZEVRIA")].index,
                        inplace=True)
        vaccinated.drop(
            vaccinated[(vaccinated.poradi_davky > 1) & (vaccinated.vakcina == "COVID-19 Vaccine Janssen")].index,
            inplace=True)

        infected = infected.groupby(['datum', 'okres_lau_kod']).size().reset_index(name='infected')  # dataframe
        vaccinated = vaccinated.groupby(['datum', 'orp_bydliste_kod']).size().reset_index(
            name='vaccinated')  # dataframe

        # replace date by 1, 2, 3 and 4 (quarters of the year)
        for df in [infected, vaccinated]:
            df.loc[(df.datum == last_12_months_dates[0]) |
                   (df.datum == last_12_months_dates[1]) |
                   (df.datum == last_12_months_dates[2]), "datum"] = 4

            df.loc[(df.datum == last_12_months_dates[3]) |
                   (df.datum == last_12_months_dates[4]) |
                   (df.datum == last_12_months_dates[5]), "datum"] = 3

            df.loc[(df.datum == last_12_months_dates[6]) |
                   (df.datum == last_12_months_dates[7]) |
                   (df.datum == last_12_months_dates[8]), "datum"] = 2

            df.loc[(df.datum == last_12_months_dates[9]) |
                   (df.datum == last_12_months_dates[10]) |
                   (df.datum == last_12_months_dates[11]), "datum"] = 1

            df.rename(columns={"datum": "quarter"}, inplace=True)

        infected = infected.groupby(['quarter', 'okres_lau_kod']).sum().reset_index()  # dataframe
        vaccinated = vaccinated.groupby(['quarter', 'orp_bydliste_kod']).sum().reset_index()  # dataframe

        # change orp_bydliste_kod to int
        vaccinated.orp_bydliste_kod = vaccinated.orp_bydliste_kod.astype(int)

        # use only stats from "2020-12-31"
        counties_stats.drop(counties_stats[counties_stats.casref_do != "2020-12-31"].index, inplace=True)

        # keep only rows where "pohlavi_kod" == nan, since its sum of all other values
        counties_stats = counties_stats[counties_stats['pohlavi_kod'].isna()]

        # "casref_do" and "pohlavi_kod" columns are not needed anymore
        counties_stats.drop(['casref_do', 'pohlavi_kod'], axis=1, inplace=True)

        to_remove = ["Česká republika",
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
        age_stats.loc[(age_stats.vek_txt == "0 až 5 (více nebo rovno 0 a méně než 5)") |
                      (age_stats.vek_txt == "5 až 10 (více nebo rovno 5 a méně než 10)") |
                      (age_stats.vek_txt == "10 až 15 (více nebo rovno 10 a méně než 15)") |
                      (age_stats.vek_txt == "15 až 20 (více nebo rovno 15 a méně než 20)") |
                      (age_stats.vek_txt == "20 až 25 (více nebo rovno 20 a méně než 25)"), "vek_txt"] = 1

        age_stats.loc[(age_stats.vek_txt == "25 až 30 (více nebo rovno 25 a méně než 30)") |
                      (age_stats.vek_txt == "30 až 35 (více nebo rovno 30 a méně než 35)") |
                      (age_stats.vek_txt == "35 až 40 (více nebo rovno 35 a méně než 40)") |
                      (age_stats.vek_txt == "40 až 45 (více nebo rovno 40 a méně než 45)") |
                      (age_stats.vek_txt == "45 až 50 (více nebo rovno 45 a méně než 50)") |
                      (age_stats.vek_txt == "50 až 55 (více nebo rovno 50 a méně než 55)") |
                      (age_stats.vek_txt == "55 až 60 (více nebo rovno 55 a méně než 60)"), "vek_txt"] = 2

        age_stats.loc[(age_stats.vek_txt == "60 až 65 (více nebo rovno 60 a méně než 65)") |
                      (age_stats.vek_txt == "65 až 70 (více nebo rovno 65 a méně než 70)") |
                      (age_stats.vek_txt == "70 až 75 (více nebo rovno 70 a méně než 75)") |
                      (age_stats.vek_txt == "75 až 80 (více nebo rovno 75 a méně než 80)") |
                      (age_stats.vek_txt == "80 až 85 (více nebo rovno 80 a méně než 85)") |
                      (age_stats.vek_txt == "85 až 90 (více nebo rovno 85 a méně než 90)") |
                      (age_stats.vek_txt == "90 až 95 (více nebo rovno 90 a méně než 95)") |
                      (age_stats.vek_txt == "Od 95 (více nebo rovno 95)"), "vek_txt"] = 3

        # sum stats for each age group (1, 2, 3)
        age_stats = age_stats.groupby(['vek_txt', 'vuzemi_txt']).sum().reset_index()  # dataframe

        # pick 50 counties with highest number of citizens
        choosed_counties_names = list(sum_stats.sort_values(by='hodnota', ascending=False).head(50)["vuzemi_txt"])

        output_data = pd.DataFrame([], columns=["okres_nazev",
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
        counties_codes = counties_codes.append(
            {"okres_lau_kod": "CZ0100", "okres_nazev": "Hlavní město Praha", "orp_kod": 1000}, ignore_index=True)

        # rename because of join
        vaccinated.rename(columns={"orp_bydliste_kod": "orp_kod"}, inplace=True)

        # we need county name instead of orp code or county code, so we have to join dataframes
        infected = infected.merge(counties_codes.drop(columns="orp_kod"), on="okres_lau_kod", how="left")
        vaccinated = vaccinated.merge(counties_codes.drop(columns="okres_lau_kod"), on="orp_kod", how="left")

        infected.drop_duplicates(inplace=True)
        vaccinated.drop_duplicates(inplace=True)

        infected.drop(columns="okres_lau_kod", inplace=True)
        vaccinated.drop(columns="orp_kod", inplace=True)

        infected = infected.groupby(['quarter', 'okres_nazev']).sum().reset_index()  # dataframe
        vaccinated = vaccinated.groupby(['quarter', 'okres_nazev']).sum().reset_index()  # dataframe

        # for each choosed county load stats
        for county_name in choosed_counties_names:
            row = {"okres_nazev": county_name,
                   "4_nakazeni":
                       infected.loc[(infected.quarter == 4) & (infected.okres_nazev == county_name), 'infected'].iloc[
                           0],
                   "3_nakazeni":
                       infected.loc[(infected.quarter == 3) & (infected.okres_nazev == county_name), 'infected'].iloc[
                           0],
                   "2_nakazeni":
                       infected.loc[(infected.quarter == 2) & (infected.okres_nazev == county_name), 'infected'].iloc[
                           0],
                   "1_nakazeni":
                       infected.loc[(infected.quarter == 1) & (infected.okres_nazev == county_name), 'infected'].iloc[
                           0],
                   "4_ockovani": vaccinated.loc[
                       (vaccinated.quarter == 4) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                   "3_ockovani": vaccinated.loc[
                       (vaccinated.quarter == 3) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                   "2_ockovani": vaccinated.loc[
                       (vaccinated.quarter == 2) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                   "1_ockovani": vaccinated.loc[
                       (vaccinated.quarter == 1) & (vaccinated.okres_nazev == county_name), 'vaccinated'].iloc[0],
                   "0_14_vek":
                       age_stats.loc[(age_stats.vek_txt == 1) & (age_stats.vuzemi_txt == county_name), 'hodnota'].iloc[
                           0],
                   "15_59_vek":
                       age_stats.loc[(age_stats.vek_txt == 2) & (age_stats.vuzemi_txt == county_name), 'hodnota'].iloc[
                           0],
                   "60_vek":
                       age_stats.loc[(age_stats.vek_txt == 3) & (age_stats.vuzemi_txt == county_name), 'hodnota'].iloc[
                           0]}

            output_data = output_data.append(row, ignore_index=True)

        # transform data from total number of infected/vaccinated to number of
        # infected/vaccinated per 1000 citizens for each county
        for county_name in output_data['okres_nazev']:
            all_citizens = (output_data[output_data.okres_nazev == county_name]["0_14_vek"] +
                            output_data[output_data.okres_nazev == county_name]["15_59_vek"] +
                            output_data[output_data.okres_nazev == county_name]["60_vek"])
            normalisation_constant = all_citizens / 1000

            for column_name in ["4_nakazeni", "3_nakazeni", "2_nakazeni", "1_nakazeni", "4_ockovani", "3_ockovani",
                                "2_ockovani", "1_ockovani"]:
                new_value = output_data[output_data.okres_nazev == county_name][column_name] / normalisation_constant
                output_data.loc[output_data.okres_nazev == county_name, column_name] = new_value

        # check for outliers
        for column_name in ["4_nakazeni", "3_nakazeni", "2_nakazeni", "1_nakazeni", "4_ockovani", "3_ockovani",
                            "2_ockovani", "1_ockovani"]:
            outliers = outliers_iqr(output_data[column_name])

            for x in outliers:
                # substitue each outlier by mean value of non-outlier values of the column
                output_data.loc[output_data[column_name] == x, column_name] = \
                output_data[~output_data[column_name].isin(outliers)][column_name].mean()

        # normalize values by min-man method
        for column_name in ["4_nakazeni", "3_nakazeni", "2_nakazeni", "1_nakazeni", "4_ockovani", "3_ockovani",
                            "2_ockovani", "1_ockovani"]:
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
