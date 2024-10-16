import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from shapely import Point, LineString
import scipy.interpolate as interp
plt.rcParams.update({'font.family': 'DejaVu Sans'})

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

    def plot_slice_3d(self, show=True, variable_name=None):

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        if variable_name is not None:
            data = pd.merge(self.gdf[["cell_ID"]], self.df)
            data = data[data["Time"] == 1]

        sc = ax.scatter(self.gdf.geometry.x, self.gdf.geometry.y, self.gdf.geometry.z, s=1, c=data[variable_name] if variable_name is not None else 'black',
        cmap="Spectral_r")

        # Add a colorbar to the plot
        if variable_name is not None:
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label(self.units[variable_name])  # You can change the label to describe what the color represents

        plt.title('Air Points' if variable_name is None else f"{self.titles[variable_name]} of Air Points")

        if show:
            plt.show()


    def plot_slice_3d(self, slice, show=True, variable_name=None):

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        if variable_name is not None:
            data = pd.merge(self.gdf[["cell_ID"]], self.df)
            data = data[data["Time"] == 1]

        sc = ax.scatter(self.gdf.geometry.x, self.gdf.geometry.y, self.gdf.geometry.z, s=1, c=data[variable_name] if variable_name is not None else 'black',
                        cmap="Spectral_r")

        # plot 3d slice
        slice_2d = gpd.GeoSeries([slice]) 
        slice_coords = list(slice.coords) 
        polygon_vertices = []

        # Create the bottom face of the polygon (min_z)
        for x, y in slice_coords:
            polygon_vertices.append((x, y, 0))

        # Create the top face of the polygon (max_z)
        for x, y in reversed(slice_coords):
            polygon_vertices.append((x, y, max(self.gdf.geometry.z)))

        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        # Plot the polygon as a vertical surface using Poly3DCollection
        poly = Poly3DCollection([polygon_vertices], color='red', alpha=0.3)
        ax.add_collection3d(poly)

        # Add a colorbar to the plot
        if variable_name is not None:
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label(self.units[variable_name])  # You can change the label to describe what the color represents

        plt.title('Air Points' if variable_name is None else f"{self.titles[variable_name]} of Air Points")

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
        outpath = Path("voxels/cache/surf.shp")
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

        outpath = Path(f"voxels/cache/surfacepoints_{threshold}m.shp")
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
    
    def _merge_buildings(self, surfmesh=gpd.read_file("voxels/shp/surface_triangle_SHP.shp")):
        """
        Load a shapefile with triangular polygons, cluster triangles based on their plane similarity,
        and merge them into larger polygons representing the same objects (e.g., building walls or roofs).

        Parameters:
            input_shapefile (str): Path to the input shapefile containing triangular polygons.
            output_shapefile (str): Path to the output shapefile where merged polygons will be saved.
            eps (float): Maximum distance between normal vectors for triangles to be considered in the same cluster.
            min_samples (int): Minimum number of triangles required to form a cluster.
        """
        outpath = Path("voxels/")

        def _calculate_normal_vector(triangle):
            """Calculate the normal vector of a triangle using its vertices."""
            p1, p2, p3 = np.array(triangle.exterior.coords[:3])
            v1 = p2 - p1
            v2 = p3 - p1
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)  # Normalize the vector
            return normal

        # Step 2: Compute normal vectors for each triangle
        normals = np.array([_calculate_normal_vector(triangle) for triangle in surfmesh.geometry])

        # Step 3: Cluster triangles based on normal vectors using DBSCAN
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(normals)
        gdf['cluster'] = clustering.labels_

        # Step 4: Merge triangles that belong to the same cluster into larger polygons
        merged_polygons = []
        for cluster_label in gdf['cluster'].unique():
            cluster_triangles = gdf[gdf['cluster'] == cluster_label].geometry
            merged_polygon = cluster_triangles.unary_union  # Merge triangles into a MultiPolygon
            merged_polygons.append(merged_polygon)

        # Step 5: Create a new GeoDataFrame for the merged polygons
        merged_gdf = gpd.GeoDataFrame(geometry=merged_polygons, crs=surfmesh.crs)

        # Step 6: Save the merged polygons to a new shapefile
        merged_gdf.to_file(outpath)

        return


    def plot_streamplot(self, time, surfacemesh=gpd.read_file("voxels/shp/surface_triangle_SHP.shp"),
                        surfacepoints=gpd.read_file("voxels/shp/surface_point_SHP.shp"),
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

            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            for _, row in surfacemesh.iterrows():
                poly_coords = np.array(row.geometry.exterior.coords)
                x_surface = poly_coords[:, 0]
                y_surface = poly_coords[:, 1]
                z_surface = poly_coords[:, 2]
                
                # Create a 3D polygon and add it to the plot
                verts = [list(zip(x_surface, y_surface, z_surface))]
                ax.add_collection3d(Poly3DCollection(verts, color='gray', alpha=0.5, linewidths=0.2, edgecolors='gray'))

            # Plot the streamlines 
            ax.quiver(x, y, z, u * wind_speed, v * wind_speed, w * wind_speed, length=5, normalize=False, color=cmap(norm(wind_speed)), linewidth=1)
            ax.view_init(elev=90, azim=45, roll=15)
            ax.set_zlim(0, 100)
            ax.set_zlabel('height')
        else:
            ax = fig.add_subplot()
            surfacemesh.plot(ax=ax, color='gray', alpha=0.5, edgecolor='gray')
            ax.quiver(x, y, u, v, color=cmap(norm(wind_speed)), linewidth=0.02, scale=80, headwidth=1, headlength=1)
            
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


surfacepoints = SurfacePoints(gpd.read_file('voxels/shp/surface_point_SHP.shp'), pd.read_csv('voxels/shp/surface_data_2021_07_15.csv'))
airpoints = AirPoints(gpd.read_file('voxels/shp/air_point_SHP.shp'), pd.read_csv('voxels/shp/air_data_2021_07_15.csv'))


linegeometry = LineString([(25496120, 6672150), (25496315, 6671800)])
time = 1
#surfacepoints.plot_slice_on_map(linegeometry)
#airpoints.plot_slice_on_map(linegeometry)
#airpoints.plot_points_3d()
#airpoints.plot_slice_3d(linegeometry)

airpoints.plot_streamplot(1, gpd.read_file("voxels/shp/surface_triangle_SHP.shp"), dims=2)
#airpoints.plot_flow(1, gpd.read_file("voxels/shp/surface_triangle_SHP.shp"))

#airpoints._remove_buildings(gpd.read_file("voxels/shp/surface_point_SHP.shp"))

#surfacepoints.plot_slice_points(linegeometry, "Tair", time=1)
#surfacepoints.plot_slice_lines(linegeometry, "UTCI", time=1)
#airpoints.plot_slice_fishnet(linegeometry, "WindSpeed", resolution=5)

#airpoints.plot_matrix(linegeometry, "WindSpeed", resolution=5)



