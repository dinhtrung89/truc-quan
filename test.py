import requests
import pandas as pd

indicators_map = {
    'NY.GDP.MKTP.KD.ZG': 'GDP', 
    'FM.LBL.BMNY.GD.ZS': 'M2',
    'FP.CPI.TOTL.ZG': 'INF',
    'FR.INR.RINR': 'R',
    'NE.TRD.GNFS.ZS': 'TRADE'
}

countries = ['VNM','CHN','LAO','THA','SGP']

dfs = []
country_str = ";".join(countries)
for ind_code, ind_name in indicators_map.items():
    url = f"http://api.worldbank.org/v2/country/{country_str}/indicator/{ind_code}?date=2010:2024&format=json&per_page=1000"
    resp = requests.get(url)
    if resp.status_code == 200 and len(resp.json()) == 2:
        data = resp.json()[1]
        if data:
            df = pd.DataFrame(data)
            df['country'] = df['country'].apply(lambda x: x['value'])
            df = df[['country', 'date', 'value']]
            df.columns = ['country', 'year', ind_name]
            dfs.append(df)

if dfs:
    final_df = dfs[0]
    for i in range(1, len(dfs)):
        final_df = pd.merge(final_df, dfs[i], on=['country', 'year'], how='outer')
    print(final_df.head(5))
else:
    print("Failed")
