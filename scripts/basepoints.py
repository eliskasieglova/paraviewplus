import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'DejaVu Sans'})


class BasePoints:
    def __init__(self, type, gdf, df):
        self.type = type
        self.gdf = gdf
        self.df = df

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

    def get_title(self, variable_name):
        """ Get title of variable (used for plotting). """
        return self.title[variable_name]
    
    def get_units(self, variable_name):
        """ Get units of variable (used for plotting). """
        return self.units[variable_name]
    
    def _slice(self, line, b=1):
        """ Selects subset of the points along selected line. Works for 2d and 3d. """

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
        plt.title('Points')

        if show:
            plt.show()
    
    def _classify_surfaces(self, surfmesh=gpd.read_file("paraviewplus/shp/surface_triangle_SHP.shp")):

        outpath = Path("paraviewplus/cache")

        # cache
        roof_path = Path(f"{outpath}/rooftops.shp")
        wall_path = Path(f"{outpath}/walls.shp")
        ground_path = Path(f"{outpath}/ground.shp")

        if roof_path.is_file():
            return gpd.read_file(wall_path), gpd.read_file(ground_path), gpd.read_file(roof_path)

        def _calculate_normal_vector(triangle):
            """Calculate the normal vector of a triangle using its vertices."""
            p1, p2, p3 = np.array(triangle.exterior.coords[:3])
            v1 = p2 - p1
            v2 = p3 - p1
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)  # Normalize the vector
            return normal

        # Step 2: Compute normal vectors for each triangle
        #normals = np.array([_calculate_normal_vector(triangle) for triangle in surfmesh.geometry])

        surfmesh["normal"] = [_calculate_normal_vector(triangle) for triangle in surfmesh.geometry]

        angles = []
        for n in surfmesh.normal:
            if (n[2] == 1) | (n[2] == -1):  # perfectly horizontal
                angles.append(1)

            elif (n[2] == 0) | (n[2] == -0):  # vertical -- walls
                angles.append(2)
            
            else:
                angles.append(3) # the rest aka the ground

        surfmesh['surftype'] = angles

        # Step 4: Merge triangles that belong to the same cluster into larger polygons
        
        surftypes = [[], [], []]
        surfnames = ['walls', 'ground', 'rooftops']
        outfiles = []

        for i, surftype in enumerate(surfmesh['surftype'].unique()):
            cluster = surfmesh[surfmesh['surftype'] == surftype].geometry
            if surftype == 2: 
                cluster = cluster.buffer(0.001)
            merged_polygon = cluster.union_all()
            surftypes[i].append(merged_polygon)

        for i in range(len(surftypes)):
            gdf = surftypes[i]
            gdf = gpd.GeoDataFrame(geometry=surftypes[i], crs=surfmesh.crs)
            gdf = gdf.assign(group=1).dissolve(by='group')
            outfiles.append(gdf)
            gdf.to_file(Path(f"{outpath}/{surfnames[i]}.shp"))

        return outfiles

    def _plot_multisurface(self, ax, multipolygon, color='lightgrey'):
        """ Plots multipolygon on ax. """

        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        for polygon in multipolygon.iloc[0].geometry.geoms:
            # Get the exterior coordinates of the Polygon
            poly_coords = np.array(polygon.exterior.coords)
            x_surface = poly_coords[:, 0]
            y_surface = poly_coords[:, 1]
            try:
                z_surface = poly_coords[:, 2]
            except:
                print(polygon)
            # Create a 3D polygon and add it to the plot
            verts = [list(zip(x_surface, y_surface, z_surface))]
            ax.add_collection3d(Poly3DCollection(verts, color=color, alpha=0.5, linewidths=0.2, edgecolors='gray'))

        return
