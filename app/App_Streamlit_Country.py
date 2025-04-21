import streamlit as st
import pandas as pd
import json 
from typing import List
from country_models import country
from pydantic import BaseModel



def load_data():
    with open(".\DataFile\countries.json",'r') as f:
        row_data=json.load(f)
    return [country(**item)for item in row_data]

countries=load_data()

# streamlit App
st.title("interactive Country Dashboard")

country_names= [country.Name for country in countries]

selected_country_name = st.selectbox("Select a Country " , country_names)

selected_country= next(c for c in countries if c.Name==selected_country_name)

# Elements
st.subheader("Latest Data")
elements = [item.Element for item in selected_country.important_information]

selected_emlement = st.multiselect("select Indicators", elements, default=elements[:1])

st.subheader("latest data ")
summary=[]

for item in selected_country.important_information:
    if item.Element in selected_emlement:
        Values=[v for v in item.Values if v.value!=".."]
        if Values:
            latest= Values[-1]
            summary.append({
                "Element" : item.Element,
                "Latest Year" : latest.year,
                "value": latest.value
                })
if summary:
    st.dataframe(pd.DataFrame(summary))
else:
    st.info("NO recent data available for Selected indicators.")
            
            
# visualization
st.subheader("Trands over Time ")
for item in selected_country.important_information:
    if item.Element in selected_emlement:
        valuess=[v for v in item.Values if v.value!='..']
        if len(valuess)>=2:
            years=[int(v.year.split("_")[1])for v in valuess]
            vals=[float(v.value.replace(",","")) for v in valuess]
            df=pd.DataFrame({"Year":years , "Value":vals}).set_index("Year")

        st.line_chart(df)
        st.caption(item.Element)