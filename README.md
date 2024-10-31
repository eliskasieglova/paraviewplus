# About

This code is meant to automate the generation of plots, maps, slices and 3d models for urban planning. Written in Python, main visualization library used is matplotlib.

Example data can be found in the data/ folder. Some examples of plots are in Examples.md.


# Files 
- inputs.py (for handling input data types)
- graphmaker.py (creating plots)
- main.py

### inputs.py
- AirPoints --> functions for handling air points shapefile
- SurfacePoints --> functions for handling surface points shp
- SurfaceMesh --> functions for hangling surface triangles shp

### graphmaker.py
- [TimeSeriesDemonstration](#time-series-demonstration-for-simulation-results) --> creates plot with subplots for each selected variable, plots the selected variables for each time step (1 png for each timestep. the subplots are maps colored by the selected variable)
- [SimulationResults](#simulation-results) --> creates average of selected variable for selected areas of interest (x-axis = time, y-axis = selected variable)
- [SimulationComparison](#simulation-comparison) --> creates plot comparing new vs. existing design. creates plot for each selected variable and aoi.
- [UTCICategory](#utci_category) --> plots time series of selected UTCI category (only the selected category is shown on map). creates one figure for each timestep.
- [AOIsOnMap](#map-of-areas-of-interest) --> plots polygons of areas of interest over map (either point map or mesh)
- [Windrose](#windrose) --> plots wind rose (wind directions and wind speeds of the whole area)

  
# Examples

## Time Series Demonstration for Simulation Results
![image](https://github.com/user-attachments/assets/343e90dd-81de-4f74-a5b4-964a92e51fb7)

- class TimeSeriesDemonstration in scripts/inputs.py

- inputs:
-   surfpoints (data/surface_point_shp.shp)
-   surfdata (data/surface_data_2021_07_15.csv)
-   airpoints (data/air_point_shp.shp)
-   airdata (data/air_data_2021_07_15.csv)
-   surfmesh (data/surface_triangles_shp.shp)

**run:**
```
    tsd = TimeSeriesDemonstration(
        surfpoints=gpd.read_file("data/surface_point_SHP.shp"),
        airpoints=gpd.read_file("data/air_point_SHP.shp"),
        surfmesh=gpd.read_file("data/surface_triangle_SHP.shp"),
        surfdata=pd.read_csv("data/surface_data_2021_07_15.csv"),
        airdata=pd.read_csv("data/air_data_2021_07_15.csv"),
    )

    tsd.run()
```

**Notes**:

airdata is too big for uploading on github. message and i will share through google drive. or just run ferda. but this script will not work without it (plotting windspeed).

**To-Do**: 

specify output folder for saving pngs instead of showing the plots; specify variables for plotting (default are air temp, relative humidity, wind speed and utci felt temperature). adjustable number of subplots.

**Result**:

![image](https://github.com/user-attachments/assets/d8721abc-3745-4d18-87d4-518ed269ce20)

## Simulation Results
![image](https://github.com/user-attachments/assets/3db652cd-fea3-4bee-af8e-6e5c7b209865)

- class SimulationResults in scripts/inputs.py

- inputs:
-   surface points (data/surface_point_shp.shp)
-   surface data (data/surface_data_2021_07_15.csv)
  
```
    # load data
    surfpoints = gpd.read_file("data/surface_point_shp.shp")
    surfdata = pd.read_csv("data/surface_data_2021_07_15.csv")

    # step 1: initiate the class
    sr = SimulationResults(surfpoints, surfdata)

    # step 2: add areas of interest
    sr.add_area_of_interest(aoi1)
    sr.add_area_of_interest(aoi2)
    sr.add_area_of_interest(aoi3)

    # step 3: add variables
    sr.add_variable("Tair")
    sr.add_variable("UTCI")

    # step 4: specify output folder/showing of plot
    sr.set_output_folder("paraviewplus/figs")
    sr.set_show(True)
```
**Notes**:

Specifying output folder and showing of plot is only a proposal here (not implemented in the other classes, there is just defaults to show as of now). I thought it could be helpful when in the last step the user specifies the output folder in export. The set_show could be useful if you want to visualize the plot so that the user can then adjust the colormaps etc. (this is not really thought through yet).

**Result**:

![utci](https://github.com/user-attachments/assets/88939e8b-c11e-44ad-80fd-8a9a27dbf29d)


## Simulation Comparison

![image](https://github.com/user-attachments/assets/23dd3921-64b8-4e66-bb8e-a0933fd8d0e5)

- class SimulationResults in grapmaker.py

- inputs:
-   surface points (data/surface_point_shp.shp)
-   surface data (data/surface_data_2021_07_15.csv)


```
    surfpoints = gpd.read_file("data/surface_point_shp.shp")
    surfdata = pd.read_csv("data/surface_data_2021_07_15.csv")

    # step 1: initiate class with loading surfacepoints and surface data
    sc = SimulationComparison(surfpoints, surfdata)

    # step 2: add areas of interest (either draw or upload?) and simulation(s) for comparison
    sc.add_aoi(aoi1)
    sc.add_aoi(aoi2)
    sc.add_simulation(surfdata2)

    # step 3: select variables to plot
    sc.add_variable("Tair")
    sc.add_variable("UTCI")

    # run plotting of simulation results
    sc.run()
```

**Result**:

![comparison_Air Temperature_areaD](https://github.com/user-attachments/assets/79c14f89-6c09-4a97-b443-e64906e7ff9c)


## UTCI Category

Plots maps of selected UTCI category for each timestep. Generates 1 png per each timestep in data ONLY with the selected UTCI category area.

- class UTCICategory in graphmaker.py

- inputs:
-   surface points (data/surface_point_shp.shp)
-   surface data (data/surface_data_2021_07_15.csv)
  
```
    # load data
    surfpoints = gpd.read_file("data/surface_point_shp.shp")
    surfdata = pd.read_csv("data/surface_data_2021_07_15.csv")

    # initiate class
    utci = UTCICategory(surfpoints, surfdata, surfmesh)

    # add category to plot
    utci.add_category('moderate')

    # run plotting
    utci.run()
```

**Result**:

![image](https://github.com/user-attachments/assets/81c41959-94ad-4db7-af8d-f64a8826393c)


## Map of Areas of Interest


```
    # PLOT AREAS OF INTEREST ABOVE MAP
    aoimap = AOIsOnMap(surfpoints, surfdata, surfmesh)

    # add aois
    aoimap.add_area_of_interest(aoi1)
    aoimap.add_area_of_interest(aoi2)
    aoimap.add_area_of_interest(aoi3)
    aoimap.add_area_of_interest(aoi4)

    aoimap.set_output_folder(output_folder)
    # run with point map underneath
    aoimap.run()

    # run with mesh underneath
    aoimap.set_plot_type("mesh")
    aoimap.run()
```


**Result**:

![image](https://github.com/user-attachments/assets/43638ca7-3422-41b6-a62e-189c47e453b0) ![image](https://github.com/user-attachments/assets/ecb80717-3753-48aa-9b2b-93a494c8ed5e)


## Windrose

```
    # WINDROSE
    wr = Windrose(airpoints, airdata)

    # set output folder to save output (will be possible in all plotting functions soon)
    wr.set_output_folder(output_folder)

    # run
    wr.run()
```

**Result**:

![image](https://github.com/user-attachments/assets/bb02547c-8433-416e-953c-f8e72de6000e)



