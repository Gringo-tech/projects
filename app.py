import sys
print(sys.executable)
import streamlit as st
import requests


#############################################################################################
#NOMINATIM REQUEST API
def geolocalization (x) : 
    #nominatim request : url + dictionary of requests (query) 
    req =requests.get(
        "https://nominatim.openstreetmap.org/search", #url of nominatim API
        
    params={ 
        "city":x,
        "format" : "json",
        "countrycodes" : "ch",
        },
    #dictionary that contains the specifed information for the query
    # keys must have fixed names, nominatim API can recognize only them 
    #q is the key for the name of the place
    #format is the key for the data format that you want to get
    #countrycodes is the key for the country in which you wanna search
    
    
    headers={"User-Agent": "swiss-traffic-safety-andrea-app"},#identification
        timeout=10 #server time out 10s
    )
    results=req.json() # assigns the value of the request to a variable results
    return(results)

#############################################################################################


st.title("Route Map : insert starting and ending point")# title


start_point=st.text_input("starting point") #input of statrting point (str)
end_point = st.text_input("ending point") #input of ending point (str)
list_point = [start_point,end_point]

left,center,right=st.columns([1,1,1])# set up columns (remain in the whole app)

with center : 
    done = st.button("done",use_container_width=True)#assign button "done" a central poisition
    

if done : #if done = true => user pressed it (he has inserted 2 locations)
    if start_point.strip() == '' or end_point.strip() == '' :
        st.error("insert valid locations")#avoid empty locations are passed
    elif start_point==end_point: 
        st.error("starting point and ending point cannot be equal")#avoid end=start
    else : 
        # if locations are valid, pass them to geolocalization function
    
        #note that Nominatim passes results in this form : [{},...{}]
        #so the resultes are 2 dictionaries stored in 2 different lists, one for the start
        #and for the end. When list(map()) is executed, the results of the function are 
        #stored into a list => [[{dict_start_point}],[{dict_end_point}]]
        
       dict_start_point= list(map(geolocalization,list_point))[0][0]
       dict_end_point =  list(map(geolocalization,list_point))[1][0]
       #isolating dictionaries for both places
       
       end_point_coordinates = [float(dict_end_point["lat"]),float(dict_end_point["lon"])]
       start_point_coordinates = [float(dict_start_point["lat"]),float(dict_start_point["lon"])]
       #extracting lat and long coordinates and stored as float in a list
       
       st.write(f'coordinates of start point are :  {start_point_coordinates}')
       st.write(f'coordinates of end point are :  {end_point_coordinates}')
       



