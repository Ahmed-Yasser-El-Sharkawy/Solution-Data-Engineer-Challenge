from pydantic import BaseModel

class Value_Year(BaseModel):
    year: str
    value: str
    
class more_information(BaseModel):
    Element: str
    Values:list[Value_Year]
    
class country(BaseModel):
    Id: int
    Name: str
    important_information: list[more_information]  
    
    
    """
    {
        Id:1,
        Name:"Egypt",
        important_informtion: [{
            element: "Population, total",
            ["Year_1990": 45222 , "Year_2000": 45222 ,"Year_2007": 45222]
            
        },
        {
            element: "Population, total",
            ["Year_1990": 45222 , "Year_2000": 45222 ,"Year_2007": 45222]
            
        },
        ]
        
    }
    
    """

    