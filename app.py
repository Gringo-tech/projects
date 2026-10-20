#import sys
#print(sys.executable)
import streamlit as st
import requests
import folium
import math as mt
from streamlit_folium import st_folium


#cd "C:\Users\ANDREA ERBA\OneDrive\Desktop"
#& "C:\Users\ANDREA ERBA\anaconda3\python.exe" -m streamlit run "app.py"

#NOMINATIM API REQUEST
#############################################################################################
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

#OSRM API REQUEST 
#############################################################################################

def route (start_point_coordinates, end_point_coordinates) : 
    coordinates=(
            f"{start_point_coordinates[1]},{start_point_coordinates[0]};"
            f"{end_point_coordinates[1]},{end_point_coordinates[0]}")
    req = requests.get(
    #OSRM wants inverted coordinates lon-lat 
        
    #url
    f"http://router.project-osrm.org/route/v1/driving/{coordinates}",
        
    params = {
        "overview": "full",       # Add overview geometry
        "geometries": "geojson",  # coordinates in list form [lon, lat]
        "alternatives": "true"},   # search for alternative routes   
        
    headers={"User-Agent": "swiss-traffic-safety-andrea-app"}, # identification
    timeout=15)
    
    results = req.json()
    return(results)
##############################################################################################


#BODY
##############################################################################################
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
       
       route_coordinates=route(start_point_coordinates ,end_point_coordinates)
       #recall route function, store the API answer here
       #st.write(route_coordinates)
       
       
       route_coords_list = route_coordinates["routes"][0]["geometry"]["coordinates"]
       #extraction of coordinates, since the answer of OSRM is an annidate dictionary
       # we shall visualize it on stramlit to figure out how to access to what we need 
       #st.write(route_coords)
       
       
#VISUALIZE ROUTE 
################################################################################
       if route_coordinates.get("code") == "Ok":
       # API request was succesful if the answer starts with "code" : "Ok"
          
          #inversion of elements in the list since folium requires [lat, lon], menawhile
          #OSRM provide [lon, lat]
          route_points = [[lat, lon] for lon, lat in route_coords_list]

         #Center the map Switzerland
          m = folium.Map(location=[46.8, 8.2], zoom_start=8)

         #Visualize route
          folium.PolyLine(route_points, color="blue", weight=5, opacity=0.8).add_to(m)

         #Marker Start point and End point
          folium.Marker(route_points[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
          folium.Marker(route_points[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(m)

         #Zoom on the route
          m.fit_bounds(route_points)

         #Visualize on streamlit
          st_folium(m, width=700, height=500, returned_objects=[])
       else : 
           st.error("Error : No route has been found")
      
    
    
    

       
       


