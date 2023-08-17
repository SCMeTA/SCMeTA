import requests

HMDB_API_URL = "https://hmdb.ca/metabolites/"
TOKEN = "5ZhBVFkIpe43Jh00ULwNIipGjfJCxrqpCnsvS1jj31sAFHoGg57vd46Tk95PhLfDVQ0J2vpb4kme86GldFkE5w%3D%3D"
header = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
}


def gen_data(mz_list: list[float]):
    query = "\n".join([str(mz) for mz in mz_list])
    data = {
        "utf8": "✓",
        "authenticity_token": TOKEN,
        "query_masses": query,
        "ms_search_ion_mode": "positive",
        "adduct_type": "M+H",
        "tolerance_unit": "ppm",
        "ccs_predictor": "",
        "ccs_tolerance": 0.01,
        "commit": "Search",
    }
    return data


def get_hmdb_id(name):
    season = requests.post(HMDB_API_URL, data=gen_data([name]), headers=header)
