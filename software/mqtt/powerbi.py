"""
Copyright (C) 2023  Benjamin Secker, Jolon Behrent, Louis Li, James Quilty

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import time
import random

##class for data_generation


def data_generation():
    rainfall = random.randint(0, 12)
    flow = random.randint(20, 200)
    temperature = random.randint(20, 200)
    date = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().isoformat()

    return [rainfall, flow, temperature, date, time]


if __name__ == "__main__":

    REST_API_URL = "https://api.powerbi.com/beta/ece73f9a-ba85-4235-b183-688048b0c0ae/datasets/08ecd619-c874-433d-ba94-433c8f9308ff/rows?key=g1jSLfRSHxJU3pdaAvseH5wNbzfydBGEsBuanmzUI0wv37Gu2gTKCFDixtUw7Wdr946ExyDgcC%2FTYTXLcZCNZw%3D%3D"

    while True:
        data_raw = []
        for i in range(1):
            row = data_generation()
            data_raw.append(row)
            print("Raw data - ", data_raw)

        # set the header record
        HEADER = ["rainfall", "flow", "temperature", "date", "time"]

        data_df = pd.DataFrame(data_raw, columns=HEADER)
        data_json = bytes(data_df.to_json(orient="records"), encoding="utf-8")
        print("JSON dataset", data_json)

        # Post the data on the Power BI API
        req = requests.post(REST_API_URL, data_json)

        print("Data posted in Power BI API")
        time.sleep(10)
