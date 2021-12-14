mzcr_url = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/"
czso_url = "https://www.czso.cz/documents/62353418/143522504/"
data_files = {
    "osoby": {
        "url": mzcr_url,
        "columns": ["datum", "vek", "pohlavi", "kraj_nuts_kod", "okres_lau_kod"]
    },
    "hospitalizace": {
        "url": mzcr_url,
        "columns": ["datum", "pocet_hosp"]
    },
    "kraj-okres-testy": {
        "url": mzcr_url,
        "columns": ["datum", "kraj_nuts_kod", "prirustkovy_pocet_testu_kraj", "prirustkovy_pocet_testu_okres"]
    },
    "umrti": {
        "url": mzcr_url,
        "columns": ["datum", "kraj_nuts_kod"]
    },
    "ockovani-profese": {
        "url": mzcr_url,
        "columns": ["datum", "poradi_davky", "vakcina", "vekova_skupina",
                    "orp_bydliste_kod", "kraj_nuts_kod", "kraj_nazev", "pohlavi"]
    },
    "obce": {
        "url": mzcr_url,
        "columns": ["kraj_nuts_kod", "kraj_nazev", "okres_lau_kod", "okres_nazev", "orp_kod"]
    },
    "130142-21data043021": {
        "url": czso_url,
        "columns": ["hodnota", "vek_txt", "vuzemi_txt"]
    },
    "vyleceni": {
        "url": mzcr_url,
        "columns": ["datum"]
    },
}
