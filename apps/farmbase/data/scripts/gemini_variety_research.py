import json
import os

import pandas as pd
from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

google_search_tool = Tool(google_search=GoogleSearch())

crops = pd.read_csv("apps/farmbase/data/kalro/crops.csv")
# filter_ = ((crops.crop == 'Maize') & (crops.variety == 'DH01'))
# filter_ = ((crops.crop == 'Macadamia') & (crops.variety == 'EMB-1'))
filter_ = crops.crop != "Maize"
# filter_ = ()


# print(crops[filter_])
for category, crop, variety in crops[filter_].itertuples(index=False):
    print(f"{category}, {crop}, {variety}")

    crop_sanitized = crop.replace("/", "_")
    variety_sanitized = variety.replace("/", " ")
    filename = f"apps/farmbase/data/varieties/{crop_sanitized}/{variety_sanitized}.json"
    if os.path.exists(filename):
        continue

    prompt = f"""You are a helpful agronomic advisor. Please provide a report on the {crop} crop variety {variety}.
                 - Focus on the agronomic characteristics of the variety such as disease resistance,
                 pest resistance, optimal growing conditions, yield potential, maturity period and any
                 other special characteristics of the variety.
                 - Only include information specific to the variety.
                 - Do not include general agronomic information about growing the crop.
                 """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            # Part.from_bytes(
            #     data=filepath.read_bytes(),
            #     mime_type='application/pdf',
            # ),
            prompt
        ],
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )
    # print(response.text)
    sources = []
    if response.candidates[0].grounding_metadata.grounding_chunks:
        sources = [(c.web.title, c.web.uri) for c in response.candidates[0].grounding_metadata.grounding_chunks]
    # print([s[0] for s in sources])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        print(json.dumps(dict(output_text=response.text, sources=sources), indent=2), file=f)
