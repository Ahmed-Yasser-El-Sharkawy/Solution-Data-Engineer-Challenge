from fastapi import FastAPI
from country_models import country,more_information,Value_Year
import pandas as pd
from Scrape import scrape_class
import json
import os

def data_Scrape():
    """
    Scrope country data and save the data into file {csv , json , XML}
    """
    scrape_class()



def data_intial():
    """
        this Take the file csv and tranfer into the pydantic schema
    Returns:
        list[BaseModel]: Country_information
    """
    db: list[country]=[]
    if os.path.exists("DataFile/countries.json"):
        with open("DataFile/countries.json",'r',encoding="utf-8")as f:
            data=json.load(f)
        db=[country(**item) for item in data]
    elif not(os.path.exists("DataFile/table_country_name_v1.csv") and os.path.exists("DataFile/more_information_each_country.csv")):
        data_Scrape()
        print("data scraping")
    else:
        df_main_table=pd.read_csv("DataFile/table_country_name_v1.csv")
        df_more_information=pd.read_csv("DataFile/more_information_each_country.csv")


        list_coulnms_df_more_information=df_more_information.columns
        # print(list_coulnms_df_more_information)

        for i in range(len(df_main_table)):               
            obj_country_Id=i+1
            obj_country_Name=df_main_table.loc[i,"Names_country"]
            
            obj_country_list_of_more_informtion=[]
            
            df_mini_data_country=df_more_information[df_more_information[list_coulnms_df_more_information[-1]]==obj_country_Name]
            df_mini_data_country.reset_index(inplace=True)
            # print(df_mini_data_country)
            if not df_mini_data_country.empty:
                for j in range(len(df_mini_data_country)):
                    
                    obj_more_information_Element=df_mini_data_country.loc[j,list_coulnms_df_more_information[1]]
                    
                    list_of_value_year=[]
                    for k in range(2,14):
                        obj_Value_Year_year=list_coulnms_df_more_information[k]
                        obj_Value_Year_value=df_mini_data_country.loc[j,list_coulnms_df_more_information[k]]
                        
                        obj_Value_Year=Value_Year(year=obj_Value_Year_year,value=obj_Value_Year_value)
                        list_of_value_year.append(obj_Value_Year)
                        
                    obj_more_information_Values=list_of_value_year
                    obj_more_information=more_information(Element=obj_more_information_Element,Values=obj_more_information_Values)
                    obj_country_list_of_more_informtion.append(obj_more_information)
            obj_country = country(Id=obj_country_Id,Name=obj_country_Name,important_information=obj_country_list_of_more_informtion)
            db.append(obj_country)    

    # sve db file:
    with open("DataFile/countries.json",'w',encoding="utf-8")as f:
        json.dump([coun.model_dump() for coun in db] ,f,ensure_ascii=False,indent=2)
        
    
    
    # print(db)
    return db



app = FastAPI()

db: list[country]=data_intial()

@app.get("/")
def root():
    return db

@app.get("/country")
async def fetch_country():
    return db
