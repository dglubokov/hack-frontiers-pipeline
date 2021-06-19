import requests
from bs4 import BeautifulSoup

import pandas as pd

session = requests.session()

response = session.get("https://www.greenlight.guru/blog/top-100-medical-device-startups")

if response.status_code == 200:
    print("Success")
else:
    print("Bad result")


column_names = ['Startup name', 'Year founded', 'Total money raised', 'Amount raised in last round',
'Announcement date of last round', 'Number of employees', 'Website', 'Description']

df_startups = pd.DataFrame(columns = column_names)


soup = BeautifulSoup(response.text, 'html.parser')
elements = soup.find_all(['h3', 'p'])

for i in range(len(elements)):
    if 'Year founded' in elements[i].text:
        #print(elements[i])
        append_string =  [elements[i-1].text, elements[i].text, elements[i+1].text, elements[i+2].text,
                          elements[i+3].text, elements[i+4].text, elements[i+5].text, elements[i+6].text]
        #print(append_string)
        a_series = pd.Series(append_string, index = df_startups.columns)
        df_startups = df_startups.append(a_series, ignore_index=True)
        #print(append_string)
        
        
df_startups