import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time

class scrape_class():
    
    def __init__(self, web_site="https://data.worldbank.org/country"):
        
        results=requests.get(web_site)

        # print(type(results))
        # print(results.status_code)
        
        df= pd.DataFrame()
        if(results.status_code==200 or results.status_code==202):
            try:
                country_main_page=self.country_scraping_main_page_data(results)
                df1= pd.DataFrame.from_dict(country_main_page)
                df=df1
                print(df)
                df.to_csv("DataFile/table_country_name_v1.csv",index=False)
                df.to_xml("DataFile/table_country_name_v1.xml",index=False)  
                df.to_json("DataFile/table_country_name_v1.json",index=False)  #fastapi
                print("Save File csv, json and XML for table of country name")
            except:
                print("Error in the scraping main table !!")
            
            df_more_information=pd.DataFrame()    
            
            if len(df["Link_of_country"])>0:
                for i in range(len(df['Link_of_country'])):        #try the 5th of country for testing only .    len(df['Link of country'])
                    time.sleep(5)
                    print(f"country index: {i}")
                    try:
                        results=requests.get(df['Link_of_country'][i])
                        if(results.status_code==200 or results.status_code==202):
                            mini_data_frame=self.Scraping_each_country(results,df['Names_country'][i])
                            df_more_information=pd.concat([df_more_information, mini_data_frame],ignore_index=True)
                    except:
                        print(f"Error of scraping in the {df['Names_country'][i]}")
                        
                print("More informaion :")     
                print(df_more_information.info())
                # print(df_more_information)
                df_more_information.to_csv("DataFile/more_information_each_country.csv")
                df_more_information.to_xml("DataFile/more_information_each_country.xml",index=False)  #database
                df_more_information.to_json("DataFile/more_information_each_country.json",index=False)  # FastAPI
                print("Save File csv,json and XML for table of more information about each country")    
        
    def country_scraping_main_page_data(self,results):
        src=results.content
        #print(src)

        soup= BeautifulSoup(src,"lxml")
        # print(soup)

        List_of_Section_Country_names =soup.find_all("section",{"class":"nav-item"})
        # print(List_of_Section_Country_names)

        Country={
            "First_char_in_the_country_name_group":[],
            "Names_country":[],
            "Link_of_country":[],
        }

        for section in List_of_Section_Country_names:
            # section=BeautifulSoup(section,"lxml")
            country_names=section.find_all("li")
            for i in range(len(country_names)):
                
                Country["Names_country"].append(country_names[i].text)
                Country["First_char_in_the_country_name_group"].append(country_names[i].text[0])
                Country["Link_of_country"].append("https://data.worldbank.org"+country_names[i].find("a").attrs['href'])
        
        return Country

    def Scraping_each_country(self,results,country_name):
        src=results.content
        #print(src)
        try:
            soup= BeautifulSoup(src,"lxml")
            links_of_data_of_each_country=soup.find("div",{"class":"buttonGroup"})
            
            link_of_data_of_each_country=links_of_data_of_each_country.find("a",{"class":"btn-item databank"}).attrs['href']
            # print(link_of_data_of_each_country)
            results=requests.get(link_of_data_of_each_country)
            if(results.status_code==200 or results.status_code==202):
                src=results.content
                
                soup=BeautifulSoup(src,'lxml')
                
                table=soup.find("table",{"class":"dxgvControl_GridDefaultTheme dxgv","id":"grdTableView"})
                df_header = pd.read_html(StringIO(str(table)))
                
                if len(df_header)>1:
                    df_header = df_header[1]
                else:
                    df_header = df_header[0]
                # print(df_header)

                
                # print(df_header.columns)
                List_of_header=["Year_"+str(int(cell)) for row in df_header.values for cell in row if pd.notnull(cell)]
                List_of_header.insert(0,"element")
                List_of_header.append("country_Name")
                
                # print(List_of_header)
                
                main_table=soup.find("table",{"id":"grdTableView_DXMainTable"})
                
                all_data=[]
                
                if main_table:
                    rows=main_table.find_all("tr")
                    for row in rows:
                        cells=row.find_all("td")
                        row_data=[td.get_text(strip=True)for td in cells]
                        if any(cell.strip() for cell in row_data):
                            all_data.append(row_data)
                else:
                    print("error in read body for the table !!")
                
                num_col_of_body=max(len(r) for r in all_data) if all_data else 0
                
                # print(len(List_of_header),num_col_of_body)
                
                if len(List_of_header)==num_col_of_body:
                    
                    df=pd.DataFrame(all_data,columns=List_of_header)
                else:
                    column_name=[ ("col_"+str(i)) for i in range(num_col_of_body)]
                    df=pd.DataFrame(all_data,column_name)
                
                for i in range(len(df)):
                    df.loc[i, "country_Name"]=country_name
                    
                
                # print(df)
                print(df.info())
                return df
        except:
            print(f"Error in scraping in {country_name}")
            return pd.DataFrame()
    

# scrape_class()