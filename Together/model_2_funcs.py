import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import math
import geopandas
import googlemaps
from datetime import datetime
from sklearn.cluster import KMeans


def create_shapes_df(shape_file_path, shape_region_id_col = 'ZCTA5CE10'):
    '''
    Loads and formats the shape file for our regions.

    INPUT: Path to a shape file with the shape for each region
    in a 'geometry' field. Name of the column containing region IDs.

    OUTPUT: A geopandas dataframe with each row a region, it's shape polygon,
    and the shapes area and centroid.
    '''
    gdf = geopandas.read_file(shape_file_path)
    gdf['area'] = gdf.geometry.area
    gdf['centroid'] = gdf.geometry.centroid
    gdf.rename(columns={shape_region_id_col: 'region_id'}, inplace=True)
    gdf.region_id = gdf.region_id.astype(str)
    gdf.set_index('region_id', inplace=True)
    gdf = gdf[['geometry', 'area', 'centroid']] # removing any excess fields
    return gdf

def get_region_points(region_shape, region_prediction, density_factor=100):
    '''
    Calculates set of points per region based on given density factor.

    INPUT: geopandas polygon shape; prediction value for that shape; and the density factor,
    which is defined as the number of points in a region with area 0.0001 units squared.

    OUTPUT: Geopandas series of uniformly distribued points within the shape at approximately
    the given density.
    '''

    base_density = density_factor / 0.0001
    density = base_density * region_prediction
    points_per_unit = math.sqrt(density) # points per unit of length on a bounding box with given density
    step_size = 1/points_per_unit # length of side per point on a bounding box with given density

    # separating bounding box points in to x and y coordinates for easier manipulation
    x1, y1, x2, y2 = region_shape.bounds

    # creating a range of values along each axis (lon and lat) according to step_size
    # note that we add the step size to the end point to ensure that it is included in the set of points
    x = np.arange(x1,x2+step_size,step=step_size)
    y = np.arange(y1,y2+step_size,step=step_size)

    # combining axes to create list of all grid points for the grid defined by the axis values
    box_points = geopandas.geoseries.GeoSeries([geopandas.geoseries.Point(point) for point in itertools.product(x,y)])

    # extracting the bouding box points that are within the polygon
    poly_points = box_points[box_points.within(region_shape)]

    return poly_points

def create_regions_df(shape_file_path, predictions_file_path, shape_region_id_col = 'ZCTA5CE10'):
    '''
    Creates a single dataframe with shape information and the current prediction for each region.

    INPUT: file paths to the regions shape file and the predictions csv, and the name of the shape file
    column identifying the region. The shape file must contain a 'geometry' field, and the predictions csv
    should have two columns labelled 'region_id' and 'prediction'.

    OUTPUT: combined geopandas dataframe with region shape information and prediction
    '''
    shapes_df = create_shapes_df(shape_file_path, shape_region_id_col)

    predictions_df = pd.read_csv(predictions_file_path)
    predictions_df['region_id']= predictions_df.zcta.astype(str) #priya updated
    predictions_df.set_index('region_id', inplace=True)

    regions_df = shapes_df.join(predictions_df)
    return regions_df

def create_points_df(regions_df):
    '''
    Generates a dataframe of points labelled by the region that contains them.
    The density of points in each region is proportional to the size of the prediction
    for that region.

    INPUT: dataframe with region shapes and prediction, as output by create_regions_df().

    OUTPUT: geopandas dataframe with the region_id, latitude, and longitude of each point.
    '''
    points_df = pd.DataFrame(columns=['region_id', 'geometry']) # initializing dataframe
    df_list = [] # holds region dataframes for concatenation at the end

    # iterating over every region
    for region_id in regions_df.index:
        temp_region = regions_df.loc[region_id].copy()
        # get the set of points for the region, create dataframe for them with the region id added
        #priya changed to Call_counts
        temp_points = get_region_points(temp_region.geometry, temp_region.Call_counts, density_factor=50)
        temp_df = pd.DataFrame(temp_points, columns=['geometry'])
        temp_df['region_id'] = temp_region.name
        df_list.append(temp_df)

    # concatenating to form final combined dataframe
    points_df = geopandas.geodataframe.GeoDataFrame(pd.concat(df_list))
    points_df.reset_index(drop=True, inplace=True)

    # transforming point objects to a tuple of (lon, lat) for use in clustering
    points_df['lon_lat'] = points_df.geometry.apply(lambda p: (p.x, p.y))

    return points_df

def train_kmeans(ambulance_num, points_df):
    '''
    Performs a K-means clustering on the dataframe of points from create_points_df()

    INPUT: The number of ambulances to be assigned to locations (i.e. the number of clusters needed) and
    the points dataframe.

    OUTPUT: A trained K-means model, where the cluster centers are the new optimal ambulance locations
    '''
    train_data = np.array(list(points_df.lon_lat)) # reshaping coordinates to work with KMeans
    kmeans = KMeans(n_clusters=ambulance_num).fit(train_data) # fitting clusters

    return kmeans

def plot_model_2(points_df, regions_df, kmeans_model):
    '''
    Creates a plot of all regions and their density-dependent points. Points are color-coded by kmeans
    cluster, with stars showing each cluster's centroid.

    INPUT: dataframes for region points, region shapes, and a trained K-means model

    OUTPUT: the resulting plot
    '''
    points_df['cluster'] = kmeans_model.labels_ # adding cluster label to dataframe

    # Now plotting
    fig, ax = plt.subplots(1, figsize = (15,15))
    points_df.plot(ax=ax,column='cluster') # plot points, colored by cluster
    regions_df.geometry.boundary.plot(ax=ax, color='#ff33ff', linewidth=2) # show region boundaries
    plt.plot(*zip(*kmeans_model.cluster_centers_), marker='*', markersize=14, color='#ff1a1a', ls='') # show cluster centroids
    plt.plot()

def run_optimal_placement_model(shape_file_path, predictions_file_path, ambulance_num, results_file_path=None, shape_region_id_col = 'ZCTA5CE10'):
    '''
    Runs the full model for determining the optimal staging locations for the given number of ambulances.

    INPUT: File paths to a regions shape file and a csv with region predictions, the number of ambulances to place, and
    the column name identifying regions in the regions shape file.

    OUTPUT: numpy array of ambulance placements;the resulting dataframes from create_regions_df() and create_points_df;
    and a trained K-means model. If a results file path is specified, the ambulance placements are saved as a CSV with
    longitudes and latitudes.
    '''

    regions_df = create_regions_df(shape_file_path,predictions_file_path,shape_region_id_col)
    points_df = create_points_df(regions_df)
    kmeans_model = train_kmeans(ambulance_num, points_df)
    placement_locations = kmeans_model.cluster_centers_

    if results_file_path:
        centers_df = pd.DataFrame(placement_locations, columns=['lon', 'lat'])
        centers_df.to_csv(results_file_path, index=False)

    return placement_locations, regions_df, points_df, kmeans_model

def update_ambulance_assignments(amb_status_file_path, shape_file_path, predictions_file_path, results_file_path=None, shape_region_id_col = 'ZCTA5CE10'):
    '''
    Wraps everything for model 2 together, including reassigning active ambulances to new optimal placements.

    INPUT: A csv file with current ambulance statuses, and fields AMB_ID, LAT, LONG, and AVAILABLE. All other inputs required
    for run_optimal_placement_model()

    OUTPUT: An updated dataframe of current ambulance statuses, ready to be saved to overwrite the old status file.
    All active ambulances have their new LAT and LONG coordinates in the updated dataframe.
    '''

    # loading current ambulance statuses
    # This will be replaced by a database query for active ambulances
    # Currently it is the equivalent to querying for all ambulances
    amb_locations = pd.read_csv(amb_status_file_path)
    amb_locations = geopandas.geodataframe.GeoDataFrame(amb_locations)
    amb_locations = amb_locations.set_index('AMB_ID')

    # filtering down to series of active ambulance IDs and locations
    active_locations = amb_locations[amb_locations.AVAILABLE == 1].copy() # filtering for available units
    active_locations['location'] = active_locations.apply(lambda row: geopandas.geoseries.Point(row.LONG, row.LAT), axis=1)
    active_locations = active_locations['location']

    # saving list of active unit ids to keep things in order
    active_units = list(active_locations.index)
    
    # Running model to get new locations
    amb_count = len(active_units) # counting number of active ambulances to reassign
    new_placement_locations, new_regions_df, new_points_df, new_kmeans_model = run_optimal_placement_model(shape_file_path=shape_file_path,
                                                                                           predictions_file_path=predictions_file_path,
                                                                                           ambulance_num=amb_count,
                                                                                           results_file_path=results_file_path,
                                                                                           shape_region_id_col = shape_region_id_col)

    # converting coordinates to geopandas point objects
    new_locations = geopandas.geoseries.GeoSeries([geopandas.geoseries.Point(point) for point in new_placement_locations])

    # calculating pairwise distances
    # each row is an ambulance and each column a new location (i.e. cluster center).
    dist_arr = np.zeros(shape=(amb_count,amb_count)) # pairwise distance from each active unit to each new location
    for amb_index in range(amb_count):
        for target_index in range(amb_count):
            dist_arr[amb_index, target_index] = active_locations[amb_index].distance(new_locations[target_index])

    # determining new ambulance assignments
    # currently, this just takes the closest pair of ambulance and new location, assigns the amb to that location,
    # removes both from further consideration, and iterates until all have been assigned.
    # it uses linear distance, not the google maps API
    new_assignments = [0]*amb_count # stores new point for each active ambulance
    new_assignments_distances = [0]*amb_count # stores distance, for use in evaluating different methods
    max_val = dist_arr.max() + 1 # guarantees value is higher than any in array

    for i in range(amb_count): # sets number of iterations
        best_distance = dist_arr.min() # value of shortest distance
        # finds index of shortest distance in the array
        best_amb_index, best_target_index = np.unravel_index(dist_arr.argmin(), dist_arr.shape)
        # Sets new assignment for this ambulance and target
        new_assignments[best_amb_index] = new_locations[best_target_index]
        new_assignments_distances[best_amb_index] = best_distance

        # remove best_amb and best_target from consideration by setting their values to max_val
        dist_arr[best_amb_index, :] = max_val
        dist_arr[:, best_target_index] = max_val

    # finally, updates the coordinates for the active ambulances and returns the dataframe for saving
    for i in range(amb_count):
        amb_id = active_units[i]
        amb_locations.loc[amb_id, 'LONG'] = new_locations[i].x
        amb_locations.loc[amb_id, 'LAT'] = new_locations[i].y

    return amb_locations
