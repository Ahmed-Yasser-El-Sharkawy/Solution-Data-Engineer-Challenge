import streamlit as st
import pandas as pd
import sys
import os
import json
import  plotly.graph_objects as go
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.country_models import country

def load_data():
    with open("New_DataFile\countries.json",'r') as f:
        row_data=json.load(f)
    return [country(**item)for item in row_data]

db=load_data()

def Countries_render_ui_ver3(db):
    countries = db

    st.set_page_config(
    page_title="📊 Interactive Country Dashboard",
    page_icon="🔬",
    layout="wide"
    )
    

    # --- Select a Country ---
    country_names = [c.Name for c in countries]
    selected_country_name = st.selectbox("Select a Country", country_names)
    selected_country = next(c for c in countries if c.Name == selected_country_name)

    # --- Prepare display ---
    st.markdown("### Key Indicators")
    for info in selected_country.important_information:
        values = [v for v in info.Values if v.value != ".."]
        if not values:
            col1, col2, col3 = st.columns([4, 2, 4])
            col1.markdown(f"**{info.Element}**")
            col2.markdown("_No data available_")
            col3.markdown("")
            continue

        # Extract latest and trend
        latest = values[-1]
        years = [int(v.year.split("_")[1]) for v in values]
        vals = [float(v.value.replace(",", "")) for v in values]
        df = pd.DataFrame({"Year": years, "Value": vals})

        # Display in three columns
        col1, col2, col3 = st.columns([4, 2, 4])
        col1.markdown(f"**{info.Element}**")
        col2.markdown(
            f"<span style='font-size:24px; font-weight:bold'>{latest.value}</span>"
            f"<br><sub>({latest.year.split('_')[1]})</sub>",
            unsafe_allow_html=True
        )

        # Plotly Line + Points Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Year"],
            y=df["Value"],
            mode='lines+markers',
            line=dict(shape="spline"),
            marker=dict(size=6),
            name=info.Element
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=150,
            showlegend=False
        )
        col3.plotly_chart(fig, use_container_width=True)
        
        
        
    # Compare Two Countries
    st.markdown("---")
    st.subheader("Compare Two Countries")
    
    #select countries to compare
    col1 , col2 = st.columns(2)
    compare_country_1=col1.selectbox("Select First Country", country_names , key="comp1")
    compare_country_2=col2.selectbox("Select Sconed Country", country_names , key="comp2")
    
    c1 = next(c for c in db if c.Name== compare_country_1)
    c2 = next( c for c in db if c.Name == compare_country_2)
    
    elements_1={item.Element :item for item in c1.important_information}
    elements_2={item.Element :item for item in c2.important_information}

    common_elements=set(elements_1.keys()) &set(elements_2.keys())
    
    
    labels , values_1 , values_2 =[] , [] ,[]
    
    for elem in common_elements:
        v1_list=[v for v in elements_1[elem].Values if v.value !=".."]
        v2_list=[v for v in elements_2[elem].Values if v.value !=".."]
        if v1_list and v2_list:
            v1=float(v1_list[-1].value.replace(",",""))
            v2=float(v2_list[-1].value.replace(",",""))
            labels.append(elem)
            values_1.append(v1)
            values_2.append(v2)
    
    # Threshold to separate high vs low values
    threshold = 300  

    # Split indicators into high and low value lists
    high_labels, high_v1, high_v2, high_avg = [], [], [], []
    low_labels, low_v1, low_v2, low_avg = [], [], [], []

    for label, v1, v2 in zip(labels, values_1, values_2):
        avg = (v1 + v2) / 2
        if max(v1, v2) > threshold:
            high_labels.append(label)
            high_v1.append(v1)
            high_v2.append(v2)
            high_avg.append(avg)
        else:
            low_labels.append(label)
            low_v1.append(v1)
            low_v2.append(v2)
            low_avg.append(avg)
    
    def render_comparison_chart(title, labels, v1, v2, avg):
        fig = go.Figure()
        
        fig.add_trace(go.Bar(x=labels, y=v1, name=compare_country_1, marker=dict(color="deepskyblue")))
        fig.add_trace(go.Bar(x=labels, y=v2, name=compare_country_2, marker=dict(color="mediumorchid")))
        
        fig.add_trace(go.Scatter(
            x=labels,
            y=avg, name="Average",
            mode="lines+markers",
            line=dict(color="white", width=2))
            )

        fig.update_layout(
            title=title,
            xaxis_title="Indicator",
            yaxis_title="Value",
            barmode="group",
            plot_bgcolor="#111",
            paper_bgcolor="#111",
            font=dict(color='white'),
            height=1200,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.1,
                xanchor='center',
                x=0.5
            )
        )
        st.plotly_chart(fig, use_container_width=True)


    # Show two separate charts
    if high_labels:
        render_comparison_chart("High-Value Indicators Comparison", high_labels, high_v1, high_v2, high_avg)

    if low_labels:
        render_comparison_chart("Low-Value Indicators Comparison", low_labels, low_v1, low_v2, low_avg)

        
    # fig_comparsion= go.Figure()
    
    # fig_comparsion.add_trace(go.Bar(x=labels, y=values_1, name=compare_country_1, marker=dict(color="deepskyblue")))
    # fig_comparsion.add_trace(go.Bar(x=labels, y=values_2, name=compare_country_2, marker=dict(color="mediumorchid")))
    
    # avg_values=[(v1+v2)/2 for v1,v2 in zip(values_1,values_2)]
    # fig_comparsion.add_trace(go.Scatter(
    #     x=labels,
    #     y=avg_values,
    #     name="Average",
    #     mode="lines+markers",
    #     line=dict(color="white",width=2)
    # ))
    
    # fig_comparsion.update_layout(
    #     title="country Comprision by indicator",
    #     xaxis_title="Indicator",
    #     yaxis_title="Value",
    #     barmode="group",
    #     plot_bgcolor="#111",
    #     paper_bgcolor="#111",
    #     font=dict(color='white'),
    #     height=900,
    #     legend=dict(orientation='h', y=1.05 ,x=0.5, yanchor="bottom" , xanchor="cent")
    # )
    # st.plotly_chart(fig_comparsion,use_container_width=True)



Countries_render_ui_ver3(db)
        