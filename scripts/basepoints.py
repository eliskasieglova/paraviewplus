import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import string
from shapely import Point

from mpl_toolkits.mplot3d.art3d import Poly3DCollection
plt.rcParams.update({'font.family': 'DejaVu Sans'})

class BasePoints:
    def __init__(self, gdf, df):
        self.gdf = gdf
        self.df = df
    
    def get_title(self, variable_name):
        """ Get title of variable (used for plotting). """
        titles = {
            "Tair": "Air Temperature",
            "WindSpeed": "Wind Speed",
            "Tsurf": "Surface Temperature",
            "RelatHumid": "Relative Humidity",
            "ET": "ET",
            "UTCI": "Felt Temperature - UTCI"
        }
        return titles[variable_name]
    
    def get_units(self, variable_name):
        """ Get units of variable (used for plotting). """

        units = {
            "Tair": "Degrees (°C)",
            "Tsurf": "Degrees (°C)",
            "RelatHumid": "Percentage (%) x 0.01",
            "UTCI": "Degrees (°C)"
        }
        return units[variable_name]
    
    def get_layout(self, layout_item, variable_name):

        layouts = {
            "ylims": {
                "Tair": (9, 50),
                "Tsurf": (9, 60),
                "UTCI": (9, 50),
                "RelatHumid": (0, 1)
            },
            "yticks": {
                "Tair": (np.arange(10, 51, step=10)),
                "Tsurf": (np.arange(10, 51, step=10)),
                "UTCI": (np.arange(10, 51, step=10)),
                "RelatHumid": (np.arange(0, 1.1, step=0.1))
            },
            "minorticklocator": {
                "Tair": 1,
                "Tsurf": 1,
                "UTCI": 1,
                "RelatHumid": 0.05
            },
            "majorticklocator": {
                "Tair": 10,
                "Tsurf": 10,
                "UTCI": 10,
                "RelatHumid": 0.1
            },
            "note": {
                "Tair": "air temperatures",
                "RelatHumid": "relative humidity",
                "Tsurf": "surface temperatures",
                "UTCI": "felt temperatures"
            }
        }
    
        return layouts[layout_item][variable_name]
    
    def plot_areas_of_interest(self, outdir, aois, show=True):
        """ Plots areas of interest (list of shapely polygons) on map. """

        self.gdf.plot()

        for aoi in aois:
            x,y = aoi.exterior.xy
            plt.plot(x, y, c='blue')

        plt.savefig(outdir + '/aois.png')

        if show:
            plt.show()

    def _apply_plot_layout(self, ax, variable_name):
        """Helper method to apply consistent layout settings to a plot."""
        # Apply x and y axis
        ax.set_xlim(1, 23)  # Assuming 23 timesteps
        ax.set_xticks(np.arange(1, 24, 1))  # X-axis ticks
        ax.set_ylim(self.get_layout("ylims", variable_name))
        ax.set_yticks(self.get_layout("yticks", variable_name))
        ax.set_xlabel("Time")
        ax.set_ylabel(self.get_units(variable_name))

        # Apply gridlines
        linestyle = '-'
        linewidth = 0.7
        ax.yaxis.set_major_locator(ticker.MultipleLocator(self.get_layout("majorticklocator", variable_name)))
        ax.grid(True, axis='y', which='major', color='gray', alpha=0.3, linestyle=linestyle, linewidth=linewidth)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if variable_name == "UTCI":
            self._apply_utci_background(ax)
        else:
            ax.set_facecolor((0.99, 0.99, 0.99, 0.1))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(self.get_layout("minorticklocator", variable_name)))
            ax.grid(True, axis='y', which='minor', color='lightgray', linestyle=linestyle, linewidth=linewidth)

    def _apply_utci_background(self, ax):
        """Adds UTCI-specific background shading to the plot."""
        ax.axhspan(9, 26, facecolor='lightgreen', alpha=0.2)
        ax.axhspan(26, 32, facecolor='orange', alpha=0.2)
        ax.axhspan(32, 38, facecolor='orangered', alpha=0.2)
        ax.axhspan(38, 46, facecolor='red', alpha=0.2)
        ax.axhspan(46, 50, facecolor='darkred', alpha=0.2)
        ax.set_ylim(9, 46)    

    def _plot_legend(self, ax):
        """Adds the legend and note text to the plot."""
        ax.legend(loc='center', bbox_to_anchor=(0.5, 1.05), ncol=4, fontsize=8, frameon=False)
        
    def _plot_note_text(self, variable_name):
        """ Adds the note text to the bottom center of the plot. """
        
        plt.figtext(0.5, 0.05, r"$\mathbfit{" + "Note:" + "}$" +
                    f"The above graph shows the average {self.get_layout("note", variable_name)} "
                    "for Area A, Area B, Area C, and Area D from the simulation results.",
                    wrap=True, horizontalalignment='center', fontsize=10, fontstyle='italic')  

        
    def _add_img(self, img_path):
        """ Add image to plot upper right corner (map of areas of interest). """

        # TODO (???)

        return  

    def plot_single_point(self, variable_name, outdir, x=None, y=None, cell_ID=None, show=True):
        """ Plot variable over time for single point. TODO take average of points around point. """

        if ((x is None) | (y is None)) & (cell_ID is None):
            raise ValueError("Either (x and y) coordinates or cell_ID must be specified.")
        
        if cell_ID is not None:
            x, y = self.gdf[self.gdf['cell_ID'] == cell_ID].geometry.x.tolist()[0], self.gdf[self.gdf['cell_ID'] == cell_ID].geometry.y.tolist()[0]
    
        # extract data
        values = [x for x in self.df[self.df['cell_ID'] == cell_ID][[variable_name]].values]
        timesteps = [x for x in self.df[self.df['cell_ID'] == cell_ID][["Time"]].values]
        
        fig, ax = plt.subplots(figsize=(10, 6))

        # plot values
        plt.plot(timesteps, values, c="red")

        # apply layout
        self._apply_plot_layout(ax, variable_name)
        self._plot_legend(ax)
        self._plot_note_text(variable_name)

        plt.title(f"{self.get_title(variable_name)} at ({x}, {y})", fontsize=18, fontweight='bold', y=1.05)
        plt.subplots_adjust(top=0.83, bottom=0.2)
        
        plt.savefig(outdir + f'/{cell_ID}_{variable_name}.png')
        if show:
            plt.show()

    def _build_plot(self, simulation, aois, variable_name, colors=['blue', 'red', 'yellow', 'green'], show=False):
        """
        Builds a plot of a specific variable over time for the defined areas of interest (AOIs) without displaying it.
        Prepares parameters for visualization (background grid, axis ticks and labels).

        Parameters:
        ----------
        simulation : pandas.DataFrame
            DataFrame representing a single simulation's data.
        variable_name : str
            The variable to plot (e.g., "Tair" for air temperature).
        colors : list of str, optional
            A list of colors to use for the different AOIs in the plot. Defaults to ['blue', 'red', 'yellow', 'green'].

        Returns:
        -------
        matplotlib.pyplot
            Plot object for further customization or display (does not show plot).
        """

        # load data
        gdf = self.gdf  # point data
        df = simulation  # attr data

        if variable_name not in df.columns:
            print("Invalid variable.")

        # plot values for each aoi
        for idx, aoi in enumerate(aois):
            # subset
            cell_IDs = gdf[gdf.within(aoi, align=True)]["cell_ID"].values.tolist()
            subset = df[df['cell_ID'].isin(cell_IDs)].dropna()

            cell_IDs = np.unique(subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
            timesteps = np.unique(subset.Time.values).tolist()  # get time steps
            avg_values = np.mean([subset[subset['cell_ID'] == id][variable_name].values for id in cell_IDs], axis=0)
            plt.plot(timesteps, avg_values, color=colors[idx], label=f"Area {list(string.ascii_uppercase)[idx]}")

        return

    def plot_single_simulation(self, variable_name, aois, outdir, colors=['blue', 'red', 'yellow', 'green'], show=False):
        """
        Generates and displays a plot for a single simulation variable over time for all AOIs.

        Parameters:
        ----------
        variable : str
            The variable to plot (e.g., "Tair", "Tsurf", "UTCI"). Defaults to "Tair".
        colors : list of str, optional
            A list of colors for the areas of interest (AOIs). Defaults to ['blue', 'red', 'yellow', 'green'].
        """

        fig, ax = plt.subplots(figsize=(12, 6))
        
        # plot values
        self._build_plot(self.df, aois, variable_name, colors=colors)

        # apply layouts
        self._apply_plot_layout(ax, variable_name)
        self._plot_legend(ax)
        self._plot_note_text(variable_name)
        plt.title(self.get_title(variable_name), fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)

        plt.savefig(f'{outdir}/' + f'{variable_name}.png')

        if show:
            plt.show()
    
    def plot_variable_comparison(self, df2, variable_name, aois, colors=None, show=True):

        colors = ['red', 'blue']
        for a, aoi in enumerate(aois):
            fig, ax = plt.subplots(figsize=(12, 6))

            # loop through simulations
            for i, simulation in enumerate([self.df, df2]):

                # plot values
                cell_IDs = self.gdf[self.gdf.within(aoi, align=True)]["cell_ID"].values.tolist()
                subset = simulation[simulation['cell_ID'].isin(cell_IDs)].dropna()

                cell_IDs = np.unique(subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
                timesteps = np.unique(subset.Time.values).tolist()  # get time steps
                avg_values = np.mean([subset[subset['cell_ID'] == id][variable_name].values for id in cell_IDs], axis=0)
                
                plt.plot(timesteps, avg_values, c=colors[i], label=f"Simulation {i+1}")

            # apply layouts
            self._apply_plot_layout(ax, variable_name)
            self._plot_legend(ax)
            if variable_name == "UTCI":
                self._apply_utci_background(ax)
            #self._plot_note_text(variable_name)
            plt.title(f"Area {a+1}: {self.get_title(variable_name)}", fontsize=18, fontweight='bold', y=1.1)
            plt.subplots_adjust(top=0.85, bottom=0.2)

            if show:
                plt.show()

        return
    
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
        plt.title('Slice')

        if show:
            plt.show()

    def plot_slice_3d(self, slice, show=True, variable_name=None):
        """
        Plots a 3D scatterplot of air points and a slice surface. Colors the points by variable if selected.

        Params:
        -------
        - slice
            Slice (shapely LineString)
        - show
            boolean, shows plot if true
        - variable_name
            specify variable if you want to color the air points by variable
        
        Returns:
        --------
        Shows a matplotlib plot if show==True, saves plot as figure to folder 'figs/'.
        """

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

        # Plot the polygon as a vertical surface using Poly3DCollection
        poly = Poly3DCollection([polygon_vertices], color='red', alpha=0.3)
        ax.add_collection3d(poly)

        # Add a colorbar to the plot
        if variable_name is not None:
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label(self.units[variable_name])  

        # Set title
        plt.title('3D Slice' if variable_name is None else f"{self.titles[variable_name]}: 3D Slice")
        ax.set_zlim(0, 150)

        # Save figure, show if selected
        plt.savefig("paraviewplus/figs/3dslice.png")
        if show:
            plt.show()


    def plot_points_3d(self, colorby=None):

        if colorby is not None:
            gdf = pd.merge(self.gdf, self.df)
            gdf = gdf[gdf["Time"] == 1]


        fig = plt.figure() 
        ax = fig.add_subplot(111, projection='3d') 

        ax.scatter(self.gdf.geometry.x, self.gdf.geometry.y, self.gdf.geometry.z, c=gdf[colorby] if colorby is not None else None, s=1)
        ax.set_zlim(0,150)

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
