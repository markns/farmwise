import json
import os

import pandas as pd
import requests

# URL to send the form data to
url = "https://suitability.kalro.org/api/cropSuitability_new/"

crops = pd.read_csv("../kalro/crops.csv")


def main():
    for row in crops.itertuples():
        # Form data as a dictionary
        form_data = {
            "crop_type": row.category,
            "crop_name": row.crop.replace("/", " "),
            "variety": row.variety.replace("/", " "),
        }

        out_file = f"../kalro/suitability/{form_data['crop_name']}-{form_data['variety']}.json"
        print(f"{form_data} - {out_file}")
        if not os.path.exists(out_file):
            response = requests.post(url, data=form_data)
            response.raise_for_status()
            suitability = response.json()
            with open(out_file, "w") as f:
                json.dump(suitability, f)


if __name__ == "__main__":
    main()
