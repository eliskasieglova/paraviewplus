import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely import Point, LineString
import scipy.interpolate as interp

class SurfacePoints:
    def __init__(self, gdf, df):
        self.gdf = gdf
        self.df = df
                 # Titles, units, and layout settings
        self.titles = {
            "Tair": "Air Temperature",
            "WindSpeed": "Wind Speed",
            "Tsurf": "Surface Temperature",
            "RelatHumid": "Relative Humidity",
            "ET": "ET",
            "UTCI": "Felt Temperature - UTCI"
        }
        self.units = {
            "Tair": "Degrees (°C)",
            "Tsurf": "Degrees (°C)",
            "RelatHumid": "Percentage (%) x 0.01",
            "UTCI": "Degrees (°C)"
        }


    def _slice(self, line, b=1):

        # create a small buffer around line
        buff = line.buffer(b)

        # plot values along line
        points_along_line = self.gdf[self.gdf.within(buff)]

        # count distance from origin
        points_along_line["dist_from_origin"] = [Point(line.coords[0]).distance(Point(point.x, point.y)) for point in points_along_line.geometry]

        return points_along_line
    
    def plot_slice_on_map(self, slice, show=True):

        fig, ax = plt.subplots()

        sc = ax.scatter(self.gdf.geometry.x, self.gdf.geometry.y, c=self.gdf.geometry.z, cmap="Spectral_r", s=1)
        slice_gdf = gpd.GeoSeries([slice]) 
        slice_gdf.plot(ax=ax, color='black', linewidth=2, label='Slice')

        # Add a colorbar to the plot
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Height (m)')  # You can change the label to describe what the color represents

        plt.legend()
        plt.title('Surface Points')

        if show:
            plt.show()

    def plot_slice_points(self, line, variable_name, time):

        # create the slice
        points_along_line = self._slice(line)

        # plot based on distance from origin
        for df in self.df:
                
            # Merge gdf with df
            points_along_line = points_along_line[["cell_ID", "geometry", "dist_from_origin"]]
            merged = pd.merge(points_along_line, df, how="left", on="cell_ID")

            # Plot the data
            cmap = plt.get_cmap("Spectral_r")
            time = 1  
            subset = merged[merged["Time"] == time]

            # Create a copy of the subset to avoid setting on a copy warning
            subset = subset.sort_values("dist_from_origin").copy()

            # Assign colors based on variable_name

            # Define the min and max values for color mapping
            min_value = subset[variable_name].min()  # Set your own min value
            max_value = subset[variable_name].max()  # Set your own max value

            # Normalize the variable values for color mapping
            norm = plt.Normalize(vmin=min_value, vmax=max_value)

            # Assign colors based on variable_name using vmin and vmax for normalization
            subset["color"] = [cmap((value - min_value) / (max_value - min_value)) for value in subset[variable_name].values]

            # Plot using the color values
            plt.style.use('dark_background')
            sc = plt.scatter(subset["dist_from_origin"], subset.geometry.z, c=subset[variable_name], cmap=cmap, norm=norm, s=1.5)
            # Add a colorbar to the plot
            cbar = plt.colorbar(sc)
            cbar.set_label(self.units[variable_name])

            plt.xlabel('Distance from Origin')
            plt.ylabel('Height')
            plt.title(f'Scatter Plot of {self.titles[variable_name]}')
            plt.show()
            
        return
    
    def plot_slice_lines(self, line, variable_name, time):

        # create the slice
        points_along_line = self._slice(line)

        # plot based on distance from origin
        for df in self.df:
            # Merge gdf with df
            points_along_line = points_along_line[["cell_ID", "geometry", "dist_from_origin"]]
            merged = pd.merge(points_along_line, df, how="left", on="cell_ID")

            # Plot the data
            cmap = plt.get_cmap("Spectral_r")
            time = 1  
            subset = merged[merged["Time"] == time]

            # Create a copy of the subset to avoid setting on a copy warning
            subset = subset.sort_values("dist_from_origin").copy()

            # Define the min and max values for color mapping
            min_value = subset[variable_name].min()  # Set your own min value
            max_value = subset[variable_name].max()  # Set your own max value

            # Normalize the variable values for color mapping
            norm = plt.Normalize(vmin=min_value, vmax=max_value)

            # Create line segments between points
            points = np.array([subset["dist_from_origin"], subset.geometry.z]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # Create a LineCollection from the segments with the colormap applied
            from matplotlib.collections import LineCollection
            lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=2)
            lc.set_array(subset[variable_name].values)

            # Plot the line collection with a black background
            plt.style.use('dark_background')
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('black')  # Set the figure background color to black
            ax.set_facecolor('black')         # Set the axes background color to black

            ax.add_collection(lc)
            ax.autoscale()
            ax.set_xlim(subset["dist_from_origin"].min(), subset["dist_from_origin"].max())
            ax.set_ylim(subset.geometry.z.min(), subset.geometry.z.max())

            # Set the color of the axis labels, title, and ticks to white for better visibility
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.tick_params(colors='white')  # Set the tick marks color to white

            # Add a colorbar to the plot
            cbar = plt.colorbar(lc, ax=ax)
            cbar.set_label(self.units[variable_name], color='white')  # Set the colorbar label to white
            cbar.ax.yaxis.set_tick_params(color='white')  # Set the color of the colorbar ticks to white
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')  # Set the color of colorbar tick labels

            # Add labels and title
            plt.xlabel('Distance from Origin')
            plt.ylabel('Height')
            plt.title(f'Line Plot of {self.titles[variable_name]}')

            plt.show()
            
        return


class AirPoints:
    def __init__(self, gdf, df):
        self.gdf = gdf
        self.df = df

        # Titles, units, and layout settings
        self.titles = {
            "Tair": "Air Temperature",
            "WindSpeed": "Wind Speed",
            "Tsurf": "Surface Temperature",
            "RelatHumid": "Relative Humidity",
            "ET": "ET",
            "UTCI": "Felt Temperature - UTCI",
        }
        self.units = {
            "Tair": "Degrees (°C)",
            "Tsurf": "Degrees (°C)",
            "RelatHumid": "Percentage (%) x 0.01",
            "UTCI": "Degrees (°C)",
            "WindSpeed": "m/s"
        }


    def _slice(self, line, b=1):

        # create a small buffer around line
        buff = line.buffer(b)

        # plot values along line
        points_along_line = self.gdf[self.gdf.within(buff)]

        # count distance from origin
        points_along_line["dist_from_origin"] = [Point(line.coords[0]).distance(Point(point.x, point.y)) for point in points_along_line.geometry]

        return points_along_line
    
    def plot_slice_on_map(self, slice, show=True):

        fig, ax = plt.subplots()

        sc = ax.scatter(self.gdf.geometry.x, self.gdf.geometry.y, c=self.gdf.geometry.z, cmap="Spectral_r", s=1)
        slice_gdf = gpd.GeoSeries([slice]) 
        slice_gdf.plot(ax=ax, color='black', linewidth=2, label='Slice')

        # Add a colorbar to the plot
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Height (m)')  # You can change the label to describe what the color represents

        plt.legend()
        plt.title('Air Points')

        if show:
            plt.show()


    def plot_slice_fishnet(self, line, variable_name, resolution=10):

        # Create slice and extract relevant points along the line
        points_along_line = self._slice(line, resolution)

        # Plot based on distance from origin


        # Merge gdf with df
        points_along_line = points_along_line[["cell_ID", "geometry", "dist_from_origin"]]
        merged = pd.merge(points_along_line, self.df, how="left", on="cell_ID")

        # Filter data for the selected time
        time = 1
        subset = merged[merged["Time"] == time].sort_values("dist_from_origin").copy()

        # Create bounding box around the data points to cover the area with the fishnet
        min_x, min_y, max_x, max_y = (
            points_along_line.dist_from_origin.min(), 
            points_along_line.geometry.z.min(), 
            points_along_line.dist_from_origin.max(), 
            points_along_line.geometry.z.max()
        )

        # Generate a fishnet (grid of polygons) over the data area with specified resolution
        fishnet = []
        x_values = np.arange(min_x, max_x + resolution, resolution)
        y_values = np.arange(min_y, max_y + resolution, resolution)

        from shapely.geometry import box 

        for x in x_values:
            for y in y_values:
                cell = box(x, y, x + resolution, y + resolution)
                fishnet.append(cell)

        fishnet_gdf = gpd.GeoDataFrame(geometry=fishnet, crs=points_along_line.crs)
        # Create a GeoDataFrame where geometry is based on dist_from_origin and geometry.z
        points_gdf = gpd.GeoDataFrame(
            subset,
            geometry=[Point(x, z) for x, z in zip(subset["dist_from_origin"], subset.geometry.z)],
            crs=points_along_line.crs
        )

        # Spatial join to match points to fishnet cells
        joined = gpd.sjoin(points_gdf, fishnet_gdf, how='left', predicate='within')

        # Check if any points were joined
        print(joined['index_right'].isna().sum(), "points did not match any fishnet cell")

        # Calculate average height values (geometry.z) within each cell of the fishnet
        fishnet_avg = joined.groupby('index_right').agg({
            variable_name: lambda vals: np.nanmean([v for v in vals])  # Calculate mean z values
        }).reset_index()

        fishnet_avg['index_right'] = [int(x) for x in fishnet_avg['index_right']]

        # Merge back the average heights with the fishnet
        fishnet_gdf = pd.merge(fishnet_gdf, fishnet_avg, left_index=True, right_on='index_right', how='right')

        # colormap
        cmap = plt.get_cmap("Spectral_r")

        # Normalize the variable values for color mapping
        min_value = fishnet_gdf[variable_name].min()
        max_value = fishnet_gdf[variable_name].max()
        norm = plt.Normalize(vmin=min_value, vmax=max_value)

        # Assign colors based on variable_name using vmin and vmax for normalization
        fishnet_gdf["color"] = [cmap((value - min_value) / (max_value - min_value)) for value in fishnet_gdf[variable_name].values]

        # Plot the fishnet grid colored by the average heights
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        fishnet_gdf = fishnet_gdf.set_geometry('geometry')
        fishnet_gdf.plot(ax=ax, color=fishnet_gdf['color'], legend=True)

        # Add a colorbar to the plot
        # Add a colorbar to the plot
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # We don't need to set actual data here
        cbar = fig.colorbar(sm, ax=ax, shrink=0.5)
        cbar.set_label(self.units[variable_name])

        # Add plot labels and title
        plt.xlabel('Distance from Origin')
        plt.ylabel('Height')
        plt.title(f'Plot of {self.titles[variable_name]} using Fishnet Grid')
        plt.show()

        return
    
    def plot_matrix(self, line, variable_name, resolution=10):

        slice = self._slice(line)[["cell_ID", "geometry", "dist_from_origin"]]
        merged = pd.merge(slice, self.df, how="left", on="cell_ID")

        # Filter data for the selected time
        time = 1
        subset = merged[merged["Time"] == time].sort_values("dist_from_origin").copy()

        # Step 2: Prepare the data for the grid
        x = subset["dist_from_origin"].values
        y = subset["geometry"].apply(lambda geom: geom.z if hasattr(geom, 'z') else np.nan).values
        z = subset[variable_name].values

        # Create a regular grid to interpolate the data
        grid_x, grid_y = np.arange(x.min(), x.max(), resolution), np.arange(y.min(), y.max(), resolution)
        grid_x, grid_y = np.meshgrid(grid_x, grid_y)

        # Step 3: Interpolate the data to fill in NaN values
        interpolated_z = interp.griddata((x, y), z, (grid_x, grid_y), method='linear')

        # Step 4: Plot the matrix using a heatmap
        plt.figure(figsize=(10, 6))
        plt.imshow(interpolated_z, extent=(x.min(), x.max(), y.min(), y.max()), origin='lower', aspect='auto', cmap='Spectral_r')
        plt.colorbar(label=variable_name)
        plt.xlabel('Distance from Origin')
        plt.ylabel('Geometry Z Value')
        plt.title(f'Heatmap of {variable_name} values with Interpolation')
        plt.show()





surfacepoints = SurfacePoints(gpd.read_file('voxels/shp/surface_point_SHP.shp'), pd.read_csv('voxels/shp/surface_data_2021_07_15.csv'))
airpoints = AirPoints(gpd.read_file('voxels/shp/air_point_SHP.shp'), pd.read_csv('voxels/shp/air_data_2021_07_15.csv'))


linegeometry = LineString([(25496120, 6672150), (25496315, 6671800)])
time = 1
#surfacepoints.plot_slice_on_map(linegeometry)
#airpoints.plot_slice_on_map(linegeometry)

#surfacepoints.plot_slice_points(linegeometry, "Tair", time=1)
#surfacepoints.plot_slice_lines(linegeometry, "UTCI", time=1)
airpoints.plot_slice_fishnet(linegeometry, "WindSpeed", resolution=5)

airpoints.plot_matrix(linegeometry, "WindSpeed", resolution=5)



