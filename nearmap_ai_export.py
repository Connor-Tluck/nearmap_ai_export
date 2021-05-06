import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import os
import glob
import pandas as pd
import json
import time
import numpy as np
import tqdm
import logging
from collections import OrderedDict
import geopandas as gpd
import shapely.geometry
import shapely.wkt
from IPython.display import display
import re
import tkinter as tk
from tkinter import filedialog
import sys
import matplotlib.colors
from matplotlib import pyplot as plt

application_window = tk.Tk()


input_file_types = [('all files', '.*'), ('geojson', '.geojson')]
output_file_types = [('all files', '.*'), ('text files', '.txt')]



while True:
    try:
        # Note: Python 2.x users should use raw_input, the equivalent of 3.x's input
        key = str(input("Please Enter your API Key "))
    except ValueError:
        print("Sorry, I didn't understand that.")
        #better try again... Return to the start of the loop
        continue
    else:
        #age was successfully parsed!
        #we're ready to exit the loop.
        break
print("Thanks, your api key was set as: " + key)


#user select the geojson file to process
file_path = filedialog.askopenfilename(parent=application_window,
                                    initialdir=os.getcwd(),
                                    title="Please select a GEOJSON file, 3D files will be converted",
                                    filetypes=input_file_types)
with open(file_path) as f:
    data = json.loads(f.read())
    print("Thanks, your geojson is loaded ")
    print(data)
    
    bounding_box = data['features'][0]['geometry']['coordinates'][0]
    if len(data['features'][0]['geometry']['coordinates'][0][0]) == 3:
        two_2d_bounding_box = []
        for i in bounding_box:
            two_2d_bounding_box.append(i[0:2])
        bounding_box = two_2d_bounding_box
    else:
        bounding_box = data['features'][0]['geometry']['coordinates'][0]
bounding_box

def geometry_convert(bounding_box):
    out_string = ''
    for i in bounding_box:
        out_string += str(i[0])
        out_string += ' '
        out_string += str(i[1])
        out_string += ', '
    out_string = out_string[:-2]
    return(out_string)

bounding_box = geometry_convert(bounding_box)



file_defined_name = filedialog.asksaveasfilename(parent=application_window,
                                      initialdir=os.getcwd(),
                                      title="Please select a file name for saving:",
                                      filetypes=output_file_types)


while True:
    try:
        # Note: Python 2.x users should use raw_input, the equivalent of 3.x's input
        projection = str(input("Please your ESPG code"))
    except ValueError:
        print("Sorry, I didn't understand that.")
        #better try again... Return to the start of the loop
        continue
    else:
        if projection == '':
            projection = '4326'
            print('Default Projection System Choosen, 4326')
            break
        else:
        #age was successfully parsed!
        #we're ready to exit the loop.
            print("Thanks, your epsg number was set as: " + projection)
            break



pd.set_option('max_colwidth', 80)

API_KEY = key # Store your Nearmap API Key in an environment variable so it doesn't appear in the notebook.

FEATURES_URL = "https://api.nearmap.com/ai/features/v3/features.json"
CLASSES_URL = "https://api.nearmap.com/ai/features/v3/classes.json" # Classes is not yet operational on v3.

import matplotlib.pyplot as plt

logging.root.setLevel(logging.WARNING)

s = requests.Session()

retries = Retry(total=7,
                backoff_factor=0.1,
                status_forcelist=[ 408, 429, 500, 502, 503, 504 ])

s.mount('https://', HTTPAdapter(max_retries=retries))

def get_payload(request_string):
    '''
    Basic wrapper code to retrieve the JSON payload from the API, and raise an error if no response is given.
    Using urllib3, this also implements exponential backoff and retries for robustness.
    '''
    response = s.get(request_string, )

    if response.ok:
        logging.info(f'Status Code: {response.status_code}')
        logging.info(f'Status Message: {response.reason}')
        payload = response.json()
        return payload
    else:
        logging.error(f'Status Code: {response.status_code}')
        logging.error(f'Status Message: {response.reason}')
        logging.error(str(response))
        payload = response.content
        logging.error(str(payload))
        return None


df_parcels = [

    {'parcel_id': 1, 'description': file_defined_name, 'geometry': 'Polygon ((' + bounding_box + '))'}
]

df_parcels = pd.DataFrame(df_parcels).set_index('parcel_id')
df_parcels['geometry'] = df_parcels.geometry.apply(lambda s: shapely.wkt.loads(s))
df_parcels = gpd.GeoDataFrame(df_parcels, crs='EPSG:4326')
df_parcels

def poly2coordstring(poly):
    '''
    Turn a shapely polygon into the format required by the API for a query polygon.
    '''
    coords = poly.boundary.coords[:]
    flat_coords = np.array(coords).flatten()
    coordstring = ','.join(flat_coords.astype(str))
    return coordstring

df_parcels.loc[1, 'description']

# Get a shapely polygon object for the first query AOI in our data frame, and convert it into the right format for the API.
#Rural Sandy
poly_obj = df_parcels.loc[1, 'geometry']
poly_obj
display('Visualisation of the Query AOI:')
display(poly_obj)
display(f'WKT of Query AOI: {shapely.wkt.dumps(poly_obj)}')
polygon = poly2coordstring(poly_obj)
display(f'API formatted Query AOI: {polygon}')

# Specify the optional date range, fixed for now
SINCE, UNTIL = ('2016-01-01', '2021-03-31')

# Specify the AI Packs. This list represents all AI Packs that are currently available.
PACKS = ','.join(['pool', 'solar', 'building', 'building_char', 'roof_char', 'construction', 'trampoline', 'vegetation', 'surfaces'])


request_string = f"{FEATURES_URL}?polygon={polygon}&since={SINCE}&until={UNTIL}&packs={PACKS}&apikey={API_KEY}"
response = s.get(request_string)

print('Request string (with API KEY removed):')
print(request_string[:-len(API_KEY)])

payload = get_payload(request_string)

payload['credits']
payload['link'] # First feature in the payload



# Subset of available classes for visualisation. Note that in a robust application, you should always code against the "classId" rather than the "description". We do this here for clarity and readability, but description text may change over time (e.g. "solar panel" may change to "Solar PV Panel", whereas 'classId' is a robust, unique identifier for each class.

class_dic = OrderedDict((
    ('Parcel Polygon', '#eeeeee'),
    ('Water Body', '#00cee3'),
    ('Swimming Pool', '#a6cee3'),
    ('Trampoline', '#e31a1c'),
    ('Construction Site','#e7298a'),
    ('Building', '#b15928'),
    ('Roof', '#ff7f00'),
    ('Metal Roof', '#b2df8a'),
    ('Shingle Roof', '#fdbf6f'),
    ('Tile Roof','#fb9a99'),
    ('Medium & High Vegetation (>2m)','#00ff00'),
    ('Tree Overhang','#33a02c'),
    ('Solar Panel','#ffff99'),
))

class_list = list(class_dic.keys())
colour_list = list(class_dic.values())
cmap = matplotlib.colors.ListedColormap(colour_list)

class_dic # Set up colours for display.


def get_parcel_as_geodataframe(payload, parcel_poly):
    '''
    Convert each feature in the payload into a row of a geopandas GeoDataFrame, and its attributes as a nested dictionary parsed from the json as an "attributes" column.
    '''
    df_features = [{'geometry': parcel_poly, 'description': 'Parcel Polygon', 'classId': 0, 'link': '', 'systemVersion': payload["systemVersion"], 'confidence': 1}]

    for feature in payload['features']:
        poly = shapely.geometry.shape(feature['geometry'])
        feature_tmp = feature.copy()
        feature_tmp['geometry'] = poly

        feature_tmp['parentId'] = str(feature['parentId'])
        feature_tmp['link'] = payload['link']
        feature_tmp['systemVersion'] = payload['systemVersion']
        if 'attributes' in feature:
            feature_tmp['attributes'] = feature['attributes']
        df_features.append(feature_tmp)

    df_features = gpd.GeoDataFrame(df_features, crs='EPSG:4326')
    projection_string = 'EPSG:' + projection
    df_features = df_features.to_crs(projection_string)


    df_features['description'] = pd.Categorical(df_features.description)
    df_features = df_features.sort_values('description')
    return df_features

def process_payload(payload, poly_obj, out_name, save=True):
    '''
    Visualise payload as a dataframe and plot, and export as a geopackage file.
    '''

    df_features = get_parcel_as_geodataframe(payload, poly_obj)

    if save:
        with open(f"{file_defined_name}.json", 'w') as f:
            json.dump(payload, f)

        df_features_saveable = (df_features.assign(
            description=df_features.description.astype('str'),
        ))
        if len(df_features) > 1: # Not just parcel polygon
            df_features_saveable['attributes'] = df_features_saveable.attributes.apply(lambda j: json.dumps(j, indent=2)) # Render attributes as string so it can be saved as a geopackage
        df_features_saveable.to_file(f"{file_defined_name}.gpkg", driver="GPKG")
    return df_features

def process_payload_parse(payload, poly_obj, out_name, save=True):
    '''
    Visualise payload as a dataframe and plot, and export as a geopackage file.
    '''

    df_features = get_parcel_as_geodataframe(payload, poly_obj)

    if save:
        feature_divided_dict = {}
        for key in df_features['description'].unique():
            current_key_df = df_features[df_features['description'] == key]
            feature_divided_dict[key] = current_key_df
    
        for attribute in feature_divided_dict:
            df_features = feature_divided_dict[attribute]

            with open(file_defined_name + "_" + f"{attribute}.json", 'w') as f:
                json.dump(payload, f)

            df_features_saveable = (df_features.assign(
                description=df_features.description.astype('str'),
            ))
            df_features_saveable['attributes'] = df_features_saveable.attributes.apply(lambda j: json.dumps(j, indent=2)) # Render attributes as string so it can be saved as a geopackage
            df_features_saveable.to_file(file_defined_name + "_" + f"{attribute}.gpkg", driver="GPKG")

    
    return df_features



def plot_query_aoi(df_features, class_list=class_list, min_confidence=0.3):
    df_features_plot = df_features.copy()
    df_features_plot['description'] = pd.Categorical(df_features.description, categories=class_list, ordered=True) # Restrict categories for visualisation
    df_features_plot = df_features_plot.dropna(subset=['description']).sort_values('description')
    colours = df_features_plot.description.apply(lambda d: class_dic[d])
    (df_features_plot
     .loc[df_features.confidence > min_confidence]
     .plot(figsize=(20,20), cmap=cmap, column='description', legend=True, categorical=True)
    )
    
    fig1 = plt.gcf()
    plt.show()
    plt.draw()
    fig1.savefig(file_defined_name+'.png')

def explore_example_parcel(ind, df_request_polygons, since=SINCE, until=UNTIL, packs=PACKS):
    '''
    From a geopandas Geodataframe of sample polygons, choose an index to visualise, and return a geodataframe of all features contained within it.
    '''
    poly_obj = df_request_polygons.loc[ind, 'geometry']
    polygon = poly2coordstring(poly_obj)
    desc = df_request_polygons.loc[ind,'description']
    request_string = f"{FEATURES_URL}?polygon={polygon}&since={since}&until={until}&packs={packs}&apikey={API_KEY}"
    logging.info(request_string.split('&apikey')[0])
    t1 = time.time()
    payload = get_payload(request_string)
    t2 = time.time()
    logging.info(f'Time to retrieve payload: {t2-t1:0.2f}s')
    logging.info(f'Credits used: {payload["credits"]}')
    logging.info(f'System version: {payload["systemVersion"]}')
    logging.debug(f'Payload: {payload}')

    
    df_features = process_payload_parse(payload, poly_obj, f'sample_payload_{desc}', save=True)
    df_features = process_payload(payload, poly_obj, f'sample_payload_{desc}', save=True)

    plot_query_aoi(df_features)

    return df_features


def remove_exterior_features(df_features, albers_proj, frac_of_parcel_filled_by_feature_thresh=0.5, frac_of_feature_within_parcel_thresh=0.5, parcel_feature_intersection_minimum_m2=20):
    '''
    An example algorithm for removing features from a query AOI, if they are deemed to only be included due to e.g. a parcel shift error.
    The total area of the feature within a parcel is meaningful, as some buildings may legitimately extend across multiple parcels (but at least @parcel_feature_intersection_minimum_m2 is required).
    Some features such as swimming pools often lie on a fence line, so they are best assigned based on whether half the object's area falls within the query AOI, and should not be shared between parcels.
    Lastly, some query AOIs are very small (e.g. very small parcels), and it is sufficient if the majority of the parcel is filled by the object, regardless of absolute size.

    Note that some AI Packs (Vegetation and Surfaces) that contain contiguous, potentially large areas, have results that are cropped to the query AOI. This is to ensure that a whole ocean or forest is not returned with a single query.
    '''
    df_features['area_m2'] = df_features.to_crs(ALBERS_PROJ).area
    parcel_area_m2 = df_features.loc[0, 'area_m2']
    feature_parcel_intersections = df_features.geometry.intersection(df_features.loc[0,'geometry'])
    df_features['feature_parcel_intersection_area_m2'] = feature_parcel_intersections.to_crs(ALBERS_PROJ).area
    df_features['frac_of_parcel_filled_by_feature'] = df_features.feature_parcel_intersection_area_m2 / parcel_area_m2
    df_features['frac_of_feature_within_parcel'] = df_features.feature_parcel_intersection_area_m2 / df_features.area_m2
    df_features['keep'] = (df_features.frac_of_parcel_filled_by_feature > frac_of_parcel_filled_by_feature_thresh) | (df_features.frac_of_feature_within_parcel > frac_of_feature_within_parcel_thresh) | (df_features.feature_parcel_intersection_area_m2 > parcel_feature_intersection_minimum_m2)

    # Now remove any remaining features that have their parent as a building which was removed, e.g. a bit of tree overhang
    df_removed_buildings = df_features.query('(description in ("Building", "Roof")) & ~keep')
    for removed_building in df_removed_buildings.itertuples():
        df_features.loc[df_features.parentId == removed_building.id, 'keep'] = False
    df_features = df_features.query('keep')
    return df_features

df_features = explore_example_parcel(1, df_parcels)
df_features.head()
