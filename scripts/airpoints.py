import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from shapely import Point
import scipy.interpolate as interp
plt.rcParams.update({'font.family': 'DejaVu Sans'})

from datapoints import DataPoints

class AirPoints(DataPoints):
    def __init__(self, gdf, df):
        super().__init__(gdf, df)

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

    def _remove_buildings(self, surf):
        """
        Creates a subset of surface mesh (surface_points_shp) without buildings, only ground.

        Params:
        -------
        surf: surface_points_shp.shp

        Returns:
        -------
        Returns gdf of surface points without buildings. Caching included.  
        """

        # cache
        outpath = Path("paraviewplus/cache/surf.shp")
        if outpath.is_file():
            return gpd.read_file(outpath)

        surf['x'] = [str(x)[:-5] for x in surf.geometry.x]
        surf['y'] = [str(x)[:-5] for x in surf.geometry.y]
        surf['z'] = surf.geometry.z
        surf['xy'] = surf.x + " " + surf.y

        # find unique xy points
        for xy in np.unique(surf.xy.values):

            # find all points at the same location
            subset = surf.where(surf.xy == xy).dropna()

            # remove all the cell ids that are larger than minimum z
            try: 
                minz = min(subset.z)
            except: 
                continue  # bc they might have been removed in the next step
            drop_ids = [int(id) for id in subset.where(subset.z > minz).dropna().cell_ID.values]

            # look into the average of the nearest points
            buff = subset.buffer(20).iloc[0]
            within_buff = surf[surf.within(buff)]

            for id in within_buff.where(within_buff.z > minz + 10).dropna().cell_ID.values:
                drop_ids.append(int(id))

            for id in drop_ids:
                surf = surf[surf['cell_ID'] != id]

        surf.to_file(outpath)

        return surf

    def _above_surface(self, surfacepoints, threshold):

        outpath = Path(f"paraviewplus/cache/surfacepoints_{threshold}m.shp")
        if outpath.is_file():
            return gpd.read_file(outpath)

        # compute vertical distance
        surfacepoints["z_surf"] = surfacepoints.geometry.z
        self.gdf["z_air"] = self.gdf.geometry.z

        #fig = plt.figure() 
        #ax = fig.add_subplot(111, projection='3d') 

        #ax.scatter(surfacepoints.geometry.x, surfacepoints.geometry.y, surfacepoints.geometry.z, s=1, c='red')  
        
        subset = gpd.sjoin_nearest(self.gdf, surfacepoints, how="left")
        subset["z_diff"] = subset["z_air"] - subset["z_surf"]
        subset = subset[subset["z_diff"] < threshold]
        subset = subset[subset["z_diff"] >= 0]

        # style
        subset["cell_ID"] = subset["cell_ID_left"]
        subset = subset[["cell_ID", "geometry"]]

        subset.to_file(outpath)

        return subset
    
    def plot_streamplot(self, time, surfacemesh=gpd.read_file("paraviewplus/shp/surface_triangle_SHP.shp"),
                        surfacepoints=gpd.read_file("paraviewplus/shp/surface_point_SHP.shp"),
                        threshold=2,
                        dims=3):

        surf = self._remove_buildings(surfacepoints)
        subset = self._above_surface(surf, threshold)

        # prepare data
        data = pd.merge(subset, self.df)
        data = data[data["Time"] == time]

        # Define the grid for the flow 
        x = np.array(data.geometry.x.values, dtype=np.float32)
        y = np.array(data.geometry.y.values, dtype=np.float32)
        
        # Define the direction components of the fluid flow 
        u = np.array(data.WindX.values, dtype=np.float32) 
        v = np.array(data.WindY.values, dtype=np.float32)  
        
        # Define the Speed of the fluid flow
        wind_speed = np.array(data.WindSpeed.values, dtype=np.float32)

        # Normalize the wind direction vectors (U, V, W) by the wind speed to maintain direction
        u_normalized = u * wind_speed 
        v_normalized = v * wind_speed

        # Define 3D values
        if dims == 3:
            z = np.array(data.geometry.z.values, dtype=np.float32)
            w = np.array(data.WindZ.values, dtype=np.float32) 
            w_normalized = w * wind_speed 

        walls, ground, rooftops = self._classify_surfaces()

        # Create a 3D figure 
        fig = plt.figure(figsize=(12, 8)) 

        # Normalize wind speeds for colormap
        from matplotlib import cm
        from matplotlib.colors import Normalize, BoundaryNorm
        # Normalize wind speeds for colormap
        min_wind_speed = 0  # Set minimum wind speed
        max_wind_speed = 10  # Set maximum wind speed
        levels = np.linspace(min_wind_speed, max_wind_speed, 11)  # Custom intervals

        norm = BoundaryNorm(levels, ncolors=256, clip=True)
        cmap = plt.get_cmap('Blues')

        if dims == 3:
            ax = fig.add_subplot(111, projection='3d')

            self._plot_multisurface(ax, ground, 'grey')
            #self._plot_multisurface(ax, walls, 'brown')
            self._plot_multisurface(ax, rooftops, 'red')

            # Plot the streamlines 
            ax.quiver(x, y, z, u * wind_speed, v * wind_speed, w * wind_speed, length=5, normalize=False, color=cmap(norm(wind_speed)), linewidth=1)
            ax.view_init(elev=90, azim=45, roll=15)
            ax.set_zlim(0, 100)
            ax.set_zlabel('height')
        else:
            ax = fig.add_subplot()
            surfacemesh.plot(ax=ax, color='gray', alpha=0.5, edgecolor='gray')
            ground.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.5)
            walls.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.5)
            rooftops.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.5)
            ax.quiver(x, y, u, v, color=cmap(norm(wind_speed)), linewidth=0.1, scale=80, headwidth=2, headlength=2)
            
        # Add a color bar to show the wind speed scale
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
        cbar_ax = inset_axes(ax, width="50%", height="3%", loc='lower center', borderpad=2.5) 
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array(wind_speed)
        cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal', label='Wind Speed on the 2D Surface (m/s)')
        cbar.ax.tick_params(labelsize=8)

        ax.axis('off')
        
        # Show the plot 
        plt.show()     