#import sys
#print(sys.executable)
import streamlit as st
import requests
import folium
import math 
from streamlit_folium import st_folium
import time
import shapely
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#cd "C:\Users\andre\OneDrive\Desktop"
#& "C:\Users\andre\anaconda3\python.exe" -m streamlit run "app.py"

#NOMINATIM API REQUEST
#############################################################################################
def geolocalization(x):
    req = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": x,
            "format": "json",
            "countrycodes": "ch",
            "limit": 2,
        },
        headers={"User-Agent": "swiss-traffic-safety-andrea-app (tuo_indirizzo@email.com)"},
        timeout=10,
    )
    if req.status_code != 200:
        st.error(f"Nominatim error {req.status_code}: {req.text[:200]}")
        st.stop()
    return req.json()

#############################################################################################

#OSRM API REQUEST 
#############################################################################################

def route (start_point_coordinates, end_point_coordinates,mid_point=None) : 
    
    if mid_point is not None :  #in the successive call we have a mid point, and we can ask OSRM to find a route that even from that mid point
                                #NOTE : the mid point is exactly the transalted point calculated in the function below
                                
       # we want to create a list that contains : [start piint coordinates, mid point coordinates , end point coordinates] and ask OSRM to provide us a route that pass from these 3 points
       # 1) list of start point coordinates 
       alt_coords_list = [f"{start_point_coordinates[1]},{start_point_coordinates[0]}"]
       
       for j in mid_point : 
           alt_coords_list.append(f"{j[0]},{j[1]}")
           # 2) we append at the initial list the coordinates of the mid point 
           
       alt_coords_list.append(f"{end_point_coordinates[1]},{end_point_coordinates[0]}")
       # 3) in coinclusion we append the coordinates of the end point
       # now we have a list 
       
       coordinates = ";".join(alt_coords_list)
       
       
    else : #in the first call the route calculated is the main one, since the mid point is estracted from the main route
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
        #"alternatives": "true"
        },                        
    #After many tests, we came at the conclusion that even if we specify alternatives as true, the API will hardly provide us with alternative 
    #routes by defualt, this is why we had to implemnt the transaltion function in order to force the API to give us back an alternative route 
    #that pass from the translated mid point.    
   
    headers={"User-Agent": "swiss-traffic-safety-andrea-app"}, # identification
    timeout=15)
    
    results = req.json()
    return(results)
##############################################################################################


#MID POINT TRANSALTION 90° RESPECT THE MAIN ROUTE 
##############################################################################################
def offset_midpoint(route_coords_list, distance_km):
    R=6371000  # Earth radius in meters

    # Select midpoint and nearby points to estimate direction
    n=len(route_coords_list)
    idx =n//2

    p1 = route_coords_list[max(0, idx - 5)]
    p2 = route_coords_list[min(n - 1, idx + 5)]

    # OSRM coordinates are [lon, lat], we need to invert them 
    lon0, lat0 = route_coords_list[idx]
    lon1, lat1 = p1
    lon2, lat2 = p2

    # Convert nearby coordinates to local metric coordinates
    lat0_rad = math.radians(lat0)

    #Calculation of translataed points
    x1 = R * math.cos(lat0_rad) * math.radians(lon1 - lon0)
    y1 = R * math.radians(lat1 - lat0)

    x2 = R * math.cos(lat0_rad) * math.radians(lon2 - lon0)
    y2 = R * math.radians(lat2 - lat0)

    # Direction vector of the route
    dx = x2 - x1
    dy = y2 - y1

    #calcualtion of the effective vector's length
    length = math.hypot(dx, dy)

    # Unit vector perpendicular to the route
    perp_x = -dy / length
    perp_y = dx / length

    # Offset distance in meters
    d = distance_km * 1000

    # Two alternative waypoints
    waypoints = []
    
    #creation of transalted points in opposite direction with respect to the main route
    for sign in (1, -1):
        x = sign * d * perp_x
        y = sign * d * perp_y

        lon = lon0 + math.degrees(
            x / (R * math.cos(lat0_rad))
        )
        lat = lat0 + math.degrees(y / R)

        #translated poiints are stored in a list 
        waypoints.append([lon, lat])
        
    #the function return a list of two transalted points [[lon,lat],[lon,lat]]=> pay attention, it is an annidated list (2 lists in a list)
    return waypoints
##############################################################################################

#VISUALIZATION FUNCTION
############################################################################################
def visualization(routes_to_show):
    colors = ["blue", "red", "green"]
    m = folium.Map(location=[46.8, 8.2], zoom_start=8)

    all_points = []
    for i, coords in routes_to_show:
        points = [[lat, lon] for lon, lat in coords]   # inversion of lat lon => lon lat
        folium.PolyLine(points, color=colors[i], weight=5, opacity=0.8).add_to(m)
        all_points.extend(points)

    if all_points:
        m.fit_bounds(all_points)

    st_folium(m, use_container_width=True, height=500, returned_objects=[])
##########################################################################################

#FIND ROUTES' POINTS IN SWISSTZERLAND AND SEPARE THEM FROM POINT OUTSIDE
##########################################################################################
def split_route(coords):
#function that receives in input one route (list of points)   
    
    #define two lists, one for inside points and one for outside points
    inside = []
    outside = []
    
    #with the for loop go through every point containd in the route 
    for lon, lat in coords:
        
        #if the point is inside the polygon => it is in switzerland, append it to internal points list
        if ch.contains(Point(lon, lat)):
            inside.append([lon, lat])
            
        #if it is outside => append to outside points list
        else:
            outside.append([lon, lat])
            
    #return both lists      
    return [inside, outside]
###########################################################################################

#FIND INCIDENTS ON THE ROUTE GIVE THE ROUTE
#NOTE : WE USE ONLY SWISS'S POINTS OF THE ROUTE (INSIDE)
############################################################################################
def route_points_near_incidents_finder(inside_points,incident_points) : 
    
    ns_buffer = 0.000449
    eo_buffer = 0.000655
    #In swiss, approximately : 
    # A differnce of 50m Nord-Sud is equal to a difference of 0,000449° of latitude 
    # A differnce of 50m Est-Ovest is equal to a difference of 0,000655° of longitude
    
    incident_on_route=0
    incidents_arr = np.array(incident_points)
    tracker=np.array([False]*len(incident_points))
   
    #search for points on route that are close to at least 1 incidet.
    #The idea is to select every route's point that has an incident in the vicinity (in this case a buffer space of 50m * 50m). 
    #To do that we just need to confront the points of Swiss routes (inside) with the points contained in the list of incidents 
    #calculating the delta of longitude and latitude between route's point and incident point, if the delta, in absolute value is less
    #than the buffer, it means that the incident is happend near the route's point
  
    for i in inside_points: 
       box = ((abs(incidents_arr[:,0]-i[0])<=eo_buffer) &
              (abs(incidents_arr[:,1]-i[1])<=ns_buffer))
       
       #box is an array of booleans, true value represent an incident point close to a point on the route, 
       #meanwhile false indicates that the incident point is not in the route's vicinity.
       #NOTE : here we are calculating how many points on the route are close to at least 1 incident, therefore, if in box there is one true or 
       #hundreds true, the point will be counted equally, since at least one incident incurred near it.
       if box.any():
           incident_on_route = incident_on_route + 1
    
       
       tracker = tracker | box
       #The purpose of tracker is to track the incident occourred near a given route. 
       #Note : this is different from the purpose of box, because here we are tracking the number of incident occurred on the route, meanwhile
       #previously we were tracking the routes' points which had at least one incidient in the vicinity.
    
    
    return(incident_on_route,tracker)
    #return a list that contains the number of points on the route close to an incidet and array of booleans which will be used to select
    #from the dataset of incidentes the specific incidents for the specific route in order to calcualte other relevant informations.
############################################################################################

#FUNCTION THAT SELECT INCIDENTS ON SPECIFIC ROUTE
############################################################################################
def incidents_on_route (list_of_coords_incidents,tracker):
    incident_on_route=[]
    for i in range(0,len(list_of_coords_incidents)) : 
        if tracker[i]==True : 
            incident_on_route.append( list_of_coords_incidents[i])
    return(incident_on_route)
###########################################################################################    

#FUNCTION THAT COUNT INCIDENT WITH SEVERE INJURIES FOR INCIDENTES ON EACH ROUTE
##########################################################################################
def injuries_counter (tracker,all_incidents_features) :
    counter_severe=0 
    counter_non_severe=0
    for i in range(0,len(all_incidents_features)):
        if tracker[i]==True : 
            if all_incidents_features[i]["properties"]["AccidentSeverityCategory_en"]=="Accident with severe injuries" :
                counter_severe = counter_severe+1
            else : 
                counter_non_severe=counter_non_severe+1
    return(counter_severe,counter_non_severe)

#BODY
############################################################################################
st.title("Route Map : insert starting and ending point")# title


start_point=st.text_input("starting point") #input of statrting point (str)
end_point = st.text_input("ending point") #input of ending point (str)
list_point = [start_point,end_point]

left,center,right=st.columns([1,1,1])# set up columns 

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
       
       #st.write(f'coordinates of start point are :  {start_point_coordinates}')
       #st.write(f'coordinates of end point are :  {end_point_coordinates}')
       
       route_coordinates=route(start_point_coordinates ,end_point_coordinates)
       #recall route function, store the API answer here
       #st.write(route_coordinates)
       
       
       route_coords_list = route_coordinates["routes"][0]["geometry"]["coordinates"]
       #extraction of coordinates, since the answer of OSRM is an annidate dictionary
       # we shall visualize it on stramlit to figure out how to access to what we need 
       #st.write(route_coordinates)
       
       
       distance_main_route_km = route_coordinates["routes"][0]["legs"][0]["distance"] / 1000
       #extraction of distance between start and end point of main route in meters, then converted in km by dividing for 1000
       #st.write(distance_main_route)
             
       
#MID POINT GENERATION
################################################################################
       
       mid_point_mod_1=[]
       mid_point_mod_2=[]
       mid_point=route_coords_list[len(route_coords_list)//2]
       
       mid_point_mod = offset_midpoint(route_coords_list,distance_km=distance_main_route_km * 0.28)
       mid_point_mod_1=[mid_point_mod[0]]
       mid_point_mod_2=[mid_point_mod[1]]
       
    #GENERATION OF 2 ALTERNATIVE ROUTES       
       route_coordinates_1=route(start_point_coordinates ,end_point_coordinates, mid_point_mod_1)
       route_coordinates_2=route(start_point_coordinates ,end_point_coordinates, mid_point_mod_2)
       route_coords_list_1 = route_coordinates_1["routes"][0]["geometry"]["coordinates"]
       route_coords_list_2 = route_coordinates_2["routes"][0]["geometry"]["coordinates"]
       
       #save routes here, streamlit rerun every time a button is pressed, thereby if we not save them somewhere, streamlit will forget the routes 
       st.session_state["routes"] = [route_coords_list, route_coords_list_1,route_coords_list_2] 


#################################################################################
#define a polygon which is an approximation of switzerland, if a point is outside of the polygon => not in switzerland 
    switzerland = Polygon([
                (5.95, 46.13),   # Geneva ovest
                (6.80, 47.35),   # Giura nord-ovest
                (7.60, 47.60),   # Basel
                (8.60, 47.80),   # Schaffausen
                (9.55, 47.55),   # Costance lake
                (9.60, 47.05),   # Liechtenstein/Grigioni
                (10.50, 46.85),  # Engadin est
                (10.10, 46.25),  # Poschiavo
                (9.00, 45.82),   # Tessin sud (Chiasso)
                (8.40, 46.00),   # Tessin ovest
                (7.00, 45.90),   # Vallese sud-ovest
                                ])

    ch = prep(switzerland) 
#make it faster, run the polygon before calling the function that divides swiss points from foreigner points

    inside_outside = list(map(split_route,st.session_state["routes"]))
#create a list of lists that has the following structure : 
#[[points inside swiss for main route , points outside for main route],[points inside swiss for alt 1 , points outside for alt 1 ],[points inside for alt 2 , points outside for alt 2 ]]
#now we have a list that contains, for each route in a fixed order (main , alt 1 , alt2), the respective lists with inside and outside points

#extract inside and outside points for each route (main , alt 1 , alt 2)
    inside_main= inside_outside[0][0]
#outside_main=inside_outside[0][1]

    inside_alt_1=inside_outside[1][0]
#outside_alt_1 =inside_outside[1][1]

    inside_alt_2= inside_outside[2][0]
#outside_alt_2 = inside_outside[2][1]

    inside_list = [ inside_main,inside_alt_1,inside_alt_2]

#import data frame downloaded from : https://data.geo.admin.ch/browser/index.html#/collections/ch.astra.unfaelle-personenschaeden_alle/items/unfaelle-personenschaeden_alle?.asset=asset-unfaelle-personenschaeden_alle_4326-json-zip
#NOTE : data frame contains only information about incidentes with injuries to persons 
    df = pd.read_json(r"C:\Users\andre\OneDrive\Desktop\dati\data.json")
    all_incidents_feautures = df["features"][:1000]
   
#extract all the incidents locations in format [[lat, lon],[lat,lon],...[lat,lon]]
    list_of_coords_incidents = []
    for i in range(0,len(df["features"][:1000])) : 
            list_of_coords_incidents.append(df["features"][i]["geometry"]["coordinates"])

    
#Call the function incidents finder and pass to it every route and obtain for each one the number of route's point in the vicinity of an incident :
#incidents_on_route, which is a list of 3 integer. Then tracker_list is a list that contains 3 array of booleans, each of them are associated with 
#incidents happend on that specific route   
    point_on_route_near_incident= []
    tracker_list=[]
    for p in [inside_main, inside_alt_1, inside_alt_2]:
                incidents,tracker = route_points_near_incidents_finder(p, list_of_coords_incidents)
                point_on_route_near_incident.append(incidents)
                tracker_list.append(tracker)
    
    
    risky_index=[]
    for i in range(0,3) : 
        risky_index.append(point_on_route_near_incident[i]/len(inside_list[i])*100)
    
    st.session_state["index"]= risky_index
    
#call the function incidents_on_route and passing the tracker of each route and the same list of incidentes, store the result in the list : " incident_on_route_list".
#This list will contain 3 lists, one for each route.
    incident_on_route_list=[]
    for t in tracker_list:
        incident_on_route_list.append(incidents_on_route(list_of_coords_incidents,t))
        
    injuries_counter_list=[]    
    for z in tracker_list : 
        injuries=injuries_counter(z,all_incidents_feautures)
        injuries_counter_list.append(injuries)
    st.session_state["injuries"] = injuries_counter_list
        
    
    

#VISUALIZE ROUTES BUTTONS
################################################################################
colors = ["blue", "red", "green"]

if "routes" in st.session_state:
    st.header("Routes Visualization")
    left, center, right = st.columns(3)

    with left:
        show_main = st.checkbox("Main route", value=True)
    with center:
        show_alt1 = st.checkbox("Alternative 1")
    with right:
        show_alt2 = st.checkbox("Alternative 2")

    flags = [show_main, show_alt1, show_alt2]

    #Fix colour on the same alternative (for example main is always blue)
    routes_to_show = [
        (i, r) for i, (r, show) in enumerate(zip(st.session_state["routes"], flags)) if show
    ]

    visualization(routes_to_show)
    
    
    

routes = ["Main", "Alt 1", "Alt 2"]

n_severe = [g for g, n in st.session_state["injuries"]]
n_not_severe = [n for g, n in st.session_state["injuries"]]
tot_injuries = [g + n for g, n in st.session_state["injuries"]]

fig, ax = plt.subplots(figsize=(7, 5))

ax.bar(routes, n_not_severe, label="Non-severe injuries", color="#f0b429")
ax.bar(routes, n_severe, bottom=n_not_severe, label="Severe injuries", color="#d64545")

# totale sopra ogni barra
for i, tot in enumerate(tot_injuries):
    ax.text(i, tot, str(tot), ha="center", va="bottom", fontweight="bold")

# numeri dentro i segmenti
for i, (g, n) in enumerate(zip(n_severe, n_not_severe)):
    if n > 0:
        ax.text(i, n / 2, str(n), ha="center", va="center", color="black")
    if g > 0:
        ax.text(i, n + g / 2, str(g), ha="center", va="center", color="white")

ax.set_ylabel("Number of incidents")
ax.set_title("Incidents in routes' vicinity")
ax.set_ylim(0, max(tot_injuries) * 1.15 if max(tot_injuries) > 0 else 1)
ax.legend()
plt.tight_layout()

st.pyplot(fig)


st.write(f"the main route has a risky index of {st.session_state['index'][0]}%")
st.write(f"the 1° alternative has a risky index of {st.session_state['index'][1]}%")  
st.write(f"the 2° alternative has a risky index of {st.session_state['index'][2]}%") 
 

 

