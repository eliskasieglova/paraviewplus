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

# Examples

## Time Series Demonstration for Simulation Results
![image](https://github.com/user-attachments/assets/343e90dd-81de-4f74-a5b4-964a92e51fb7)

- class TimeSeriesDemonstration in scripts/TimeSeriesDemonstration.py

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
todo: specify output folder for saving pngs instead of showing the plots; specify variables for plotting (default are air temp, relative humidity, wind speed and utci felt temperature).

**Result**:

![image](https://github.com/user-attachments/assets/d8721abc-3745-4d18-87d4-518ed269ce20)

## Simulation Results


## Simulation Comparison


## UTCI Category


