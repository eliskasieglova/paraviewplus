import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from shapely import Point
import scipy.interpolate as interp
from windrose import WindroseAxes
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import rcParams
rcParams['font.family'] = 'DejaVu Sans'


class DataPoints:
    def __init__(self, gdf, df):
        self.gdf = gdf
        self.df = df
        self.output_folder = "paraviewplus/figs"
    
    def get_title(self, variable_name):
        """ Get title of variable (used for plotting). """
        titles = {
            "Tair": "Air Temperature",
            "WindSpeed": "Wind Speed",
            "Tsurf": "Surface Temperature",
            "RelatHumid": "Relative Humidity",
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
    
    def get_timesteps(self, df=None):
        """ Return the time steps in the dataset """
        if df is None:
            df = self.df

        return [x for x in np.unique(df.Time)]
    
    def get_columns(self, df=None):
        """ Get the columns (variables) of chosen dataset"""
        if df is None:
            df = self.df
        return [x for x in df.columns]
    
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


class SurfacePoints(DataPoints):
    def __init__(self, gdf, df, aois=None):
        super().__init__(gdf, df)

        self.aois = aois
        self.output_folder = "paraviewplus/figs"

    def get_layout(self, layout_item, variable_name):

        layouts = {
            "ylims": {
                "Tair": (9, 50),
                "Tsurf": (9, 60),
                "UTCI": (9, 50),
                "RelatHumid": (0, 1), 
                "ET": ()
            },
            "yticks": {
                "Tair": (np.arange(10, 51, step=10)),
                "Tsurf": (np.arange(10, 51, step=10)),
                "UTCI": (np.arange(10, 51, step=10)),
                "RelatHumid": (np.arange(0, 1.1, step=0.1)), 
                "ET": ()
            },
            "minorticklocator": {
                "Tair": 5,
                "Tsurf": 5,
                "UTCI": 1,
                "RelatHumid": 0.05,
                "ET": None,
            },
            "majorticklocator": {
                "Tair": 10,
                "Tsurf": 10,
                "UTCI": 10,
                "RelatHumid": 0.1,
                "ET": None
            },
            "note": {
                "Tair": "air temperatures",
                "RelatHumid": "relative humidity",
                "Tsurf": "surface temperatures",
                "UTCI": "felt temperatures",
                "ET": "ET"
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

        # if the variable isnt in the layouts, add it based on user input?????
        if self.get_title(variable_name) == "unknown":
            units = "unknown"
            ylims = None
            yticks = None
            minorticklocator = None
            majorticklocator = None
        else:
            ylims = self.get_layout("ylims", variable_name)
            yticks = self.get_layout("yticks", variable_name)
            units = self.get_units(variable_name)
            majorticklocator = self.get_layout("majorticklocator", variable_name)
            minorticklocator = self.get_layout("minorticklocator", variable_name)

        timesteps = self.get_timesteps(self.df)
        
        # Apply x and y axis
        ax.set_xlim(timesteps[0], timesteps[-1])
        ax.set_xticks(np.arange(timesteps[0], timesteps[-1]))  
        ax.set_ylim(ylims)
        ax.set_yticks(yticks)
        ax.set_xlabel("Time")
        ax.set_ylabel(units)

        # Apply gridlines
        linestyle = '-'
        linewidth = 0.7
        ax.yaxis.set_major_locator(ticker.MultipleLocator(majorticklocator))
        ax.grid(True, axis='y', which='major', color='gray', alpha=0.3, linestyle=linestyle, linewidth=linewidth)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if variable_name == "UTCI":
            self._apply_utci_background(ax)
        else:
            ax.set_facecolor((0.99, 0.99, 0.99, 0.1))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(minorticklocator))
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
        letters = ['A', 'B', 'C', 'D']
        # load data
        gdf = self.gdf  # point data
        df = simulation  # attr data

        if not variable_name in df.columns:
            print("Invalid variable.")

        # plot values for each aoi
        for idx, aoi in enumerate(aois):
            # subset
            cell_IDs = gdf[gdf.within(aoi, align=True)]["cell_ID"].values.tolist()
            subset = df[df['cell_ID'].isin(cell_IDs)].dropna()

            cell_IDs = np.unique(subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
            timesteps = np.unique(subset.Time.values).tolist()  # get time steps
            avg_values = np.mean([subset[subset['cell_ID'] == id][variable_name].values for id in cell_IDs], axis=0)
            plt.plot(timesteps, avg_values, color=colors[idx], label=f"Area {letters[idx]}")

        return
    
    def plot_slice_points(self, line, variable_name, time):
        """ 
        Plot slice as a scatterplot, colored by variable name.
        """

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
    
    def _layout_time_series_sim(self, fig, ax, contour, levels, ticks, variable_name):

        # Add a horizontal colorbar below the plot
        cax = ax.inset_axes([0.65, -0.05, 0.4, 0.02]) 
        cbar = fig.colorbar(contour, cax=cax, orientation='horizontal', ticks=levels, shrink=0.6, spacing='proportional')
        cbar.ax.tick_params(labelsize=8)
        cbar.set_ticks(ticks)  # set ticks only on some of the levels (actual numbers above the cbar)
        cbar.ax.set_title(self.get_title(variable_name), pad=6, fontsize=8, loc='center') 
        cbar.ax.xaxis.set_ticks_position('top')

        cbar.outline.set_visible(False)

        # Remove the axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)
        
        return
    
    def _plot_time_series_sim(self, fig, ax, variable_name, cmap, time, walls, rooftops, airpoints=None, airdata=None):

        if airpoints is not None:
            merged = gpd.GeoDataFrame(pd.merge(airdata, airpoints[["cell_ID", "geometry"]])).dropna()
            subset = merged[merged["Time"] == time]
        else:
            merged = gpd.GeoDataFrame(pd.merge(self.df, self.gdf[["cell_ID", "geometry"]])).dropna()
            subset = merged[merged["Time"] == time]

        # plot the surface
        import matplotlib.tri as tri
        triang = tri.Triangulation(subset.geometry.x, subset.geometry.y)
        if variable_name == "UTCI":
            levels = [9, 26, 32, 38, 46, 50]  # levels same as ticks for utci
            ticks = levels
            norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
            contour = ax.tricontourf(triang, subset[variable_name], levels=levels, cmap=cmap, norm=norm)
        else: 
            min_value = 10 * (min(merged[variable_name]) // 10)
            max_value = 10 * (max(merged[variable_name]) // 10)
            if variable_name == "Tair":
                levels = np.arange(min_value, max_value + 1, 1)
                ticks = np.arange(min_value, max_value + 1, 5)
            elif variable_name == "WindSpeed":
                levels = np.arange(min_value, max_value + 1, 1)
                ticks = np.arange(min_value, max_value + 1, 5)
            elif variable_name == "RelatHumid":
                levels = np.arange(0, 1.1, 0.1)
                ticks = np.arange(0, 1.1, 0.2)

            contour = ax.tricontourf(triang, subset[variable_name], levels=levels, cmap=cmap)
        
        # plot the buildings (walls)
        walls.plot(ax=ax, edgecolor='black', linewidth=0.5)
        rooftops.plot(ax=ax, edgecolor='black', linewidth=0.5, color='white')

        self._layout_time_series_sim(fig, ax, contour, levels, ticks, variable_name)

        return


    def plot_simulation_timeseries(self, walls, rooftops, airpoints, airdata):

        for time in self.get_timesteps():
    
            fig, axs = plt.subplots(2, 2, figsize=(9, 9))

            # first plot --> air temperature
            plt.subplot(2, 2, 1) 
            self._plot_time_series_sim(fig, axs[0, 0], "Tair", 'coolwarm', time, walls, rooftops)

            # second subplot --> relative humidity
            plt.subplot(2, 2, 2)
            self._plot_time_series_sim(fig, axs[0, 1], "RelatHumid", 'Purples', time, walls, rooftops)

            # third subplot --> wind speed
            plt.subplot(2, 2, 3)
            self._plot_time_series_sim(fig, axs[1, 0], "WindSpeed", 'Blues', time, walls, rooftops, airpoints=airpoints, airdata=airdata)

            # fourth subplot --> utci
            plt.subplot(2, 2, 4)
            self._plot_time_series_sim(fig, axs[1, 1], "UTCI", ListedColormap(['green', 'orange', 'orangered', 'red', 'darkred']),
                                        time, walls, rooftops)

            plt.suptitle(f"Time: {time}", fontsize = 40)

            plt.savefig(f"{self.output_folder}/timeseriessimulation_time{time}.png")

        return


    def plot_UTCI_category(self, walls=gpd.read_file('paraviewplus/cache/walls.shp'), rooftops=gpd.read_file('paraviewplus/cache/rooftops.shp'), cat='moderate'):

        walls_path = Path("paraviewplus/cache/walls.shp")
        rooftops_path = Path("paraviewplus/cache/rooftops.shp")
        
        # if walls and rooftops havent been made yet --> make them.
        if walls_path.exists | rooftops_path.exists:
            walls = gpd.read_file(walls_path)
            rooftops = gpd.read_file(rooftops_path)
            
        else:
            from surfacemesh import SurfaceMesh
            walls, ground, rooftops = SurfaceMesh()._classify_surfaces()

        # Define UTCI categories and plotting colors
        utci_categories = {
            'extreme': {'bounds': (46, 50), 'color': 'darkred'},
            'very_strong': {'bounds': (38, 46), 'color': 'red'},
            'strong': {'bounds': (32, 38), 'color': 'orangered'},
            'moderate': {'bounds': (26, 32), 'color': 'orange'},
            'no': {'bounds': (9, 26), 'color': 'lightgreen'}
        }

        for time in self.get_timesteps():

            fig, ax = plt.subplots()

            # extract area with UTCI according to selected temperature
            temps = self.df[["cell_ID", "UTCI", "Time"]].dropna()
            temps = temps.where(temps["Time"] == time).dropna()
            #temps = temps.where((temps["UTCI"] > utci[cat]['bounds'][0]) & (temps["UTCI"] < utci[cat]['bounds'][1])).dropna()  # select the UTCI category

            # merge csv with gpd
            subset = gpd.GeoDataFrame(pd.merge(temps, self.gdf[["cell_ID", "geometry"]]))

            contour = ax.tricontourf(subset.geometry.x, subset.geometry.y, subset.UTCI, levels=utci[cat]['bounds'], colors=utci[cat]["color"])

            # plot the surface (walls)
            walls.plot(ax=ax, edgecolor='black', linewidth=0.5)
            rooftops.plot(ax=ax, edgecolor='black', linewidth=0.5, color='white')
            ax.axis('off')
            plt.title(f'UTCI: {cat} (hour {time})')
            plt.show()

        return
    
    def plotSimulationComparison(self, df2, df3=None, df4=None, variable_names=["Tair", "RelatHumid", "UTCI"]):

        if isinstance(variable_names, str):
            self.variable_names = [variable_names]
        else:
            self.variable_names = variable_names

        dfs = [self.df, df2, df3, df4]

        # TODO raise error if df2 or aois are empty

        colors = ['red', 'blue', 'green', 'yellow']
        letters = ['A', 'B', 'C', 'D']
        for variable_name in self.variable_names:
            for a, aoi in enumerate(self.aois):
                fig, ax = plt.subplots(figsize=(12, 6))

                # loop through simulations
                for i, simulation in enumerate(dfs):
                    if simulation is None:
                        continue

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
                plt.title(f"{self.get_title(variable_name)} (Area {letters[i]}): Existing vs. New Design{'s' if dfs[2] is not None else ''}",
                        fontsize=18, fontweight='bold', y=1.1)
                plt.subplots_adjust(top=0.85, bottom=0.2)

                plt.savefig(f"{self.output_folder}/comparison_{variable_name}_area{letters[i]}.png")
                
                plt.show()

        return




class AirPoints(DataPoints):
    def __init__(self, gdf, df, output_folder):
        super().__init__(gdf, df, output_folder)
        self.gdf = gdf
        self.df = df
        self.output_folder = output_folder

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
    
    def plot_windflow(self, time, surfacemesh=gpd.read_file("paraviewplus/shp/surface_triangle_SHP.shp"),
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


    def plot_windrose(self, color_map=plt.cm.YlOrRd_r, levels=None):
        """
        Plots a windrose showing the distribution of wind direction and wind speed.
        
        Parameters:
        color_map (matplotlib.colors.Colormap): The color map to use for the contour levels. Default is Yellow-Orange-Red.
        levels (list of int): The bin edges for wind speed categories. Default is [0, 1, 2, 3, 4, 5, 7, 10].

        Returns:
        None
        """

        # Ensure required columns exist in DataFrame
        required_columns = {'WindX', 'WindY', 'WindSpeed'}
        if not required_columns.issubset(self.df.columns):
            raise ValueError(f"DataFrame must contain the columns: {required_columns}")

        # Calculate wind directions (0-360 degrees) based on vector components in WindX and WindY
        wd = [(270 - np.degrees(np.arctan2(y, x))) % 360 for x, y in zip(self.df.WindX.values, self.df.WindY.values)]
        ws = self.df.WindSpeed.values

        # calculate the levels if not specified
        if levels is None:
            levels = np.arange(int(np.floor(min(ws))), int(np.ceil(max(ws))) + 1, (min(ws) + max(ws)) / 10)
            levels = np.unique(np.round(levels).astype(int))

        # Set up the windrose plot
        ax = WindroseAxes.from_ax()
        
        # Plot filled contours with specified color map and levels
        ax.contourf(wd, ws, bins=levels, cmap=color_map, edgecolor="black")

        # Add legend
        ax.set_legend(title="Wind Speed (m/s)", loc='upper left')

        # Save the plot
        plt.savefig(f"{self.output_folder}/windrose.png")


        
class SurfaceMesh():
    def __init__(self, surfmesh=gpd.read_file("paraviewplus/shp/surface_triangle_SHP.shp"), surfdata=pd.read_csv("paraviewplus/shp/surface_data_2021_07_15.csv")):
        self.surfmesh = surfmesh
        self.surfdata = surfdata

    def plot_by_height(self):
        """ Plot 2D plot of surface mesh colored by height. """

        self.gdf['height'] = self.gdf.geometry.apply(
            lambda geom: np.mean([coord[2] for coord in geom.exterior.coords if len(coord) == 3])
        )
        self.gdf.plot(column='height', legend=True, legend_kwds={"label": "Height (m)"})
        plt.axis('equal')

        plt.title("Scatterplot of surface mesh colored by height")
        plt.xlabel("longitude")
        plt.ylabel("latitude")

        plt.show()

    
    def _classify_surfaces(self):

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

        self.surfmesh["normal"] = [_calculate_normal_vector(triangle) for triangle in self.surfmesh.geometry]

        angles = []
        for n in self.surfmesh.normal:
            if (n[2] == 1) | (n[2] == -1):  # perfectly horizontal
                angles.append(1)

            elif (n[2] == 0) | (n[2] == -0):  # vertical -- walls
                angles.append(2)
            
            else:
                angles.append(3) # the rest aka the ground

        self.surfmesh['surftype'] = angles

        # Step 4: Merge triangles that belong to the same cluster into larger polygons
        
        surftypes = [[], [], []]
        surfnames = ['walls', 'ground', 'rooftops']
        outfiles = []

        for i, surftype in enumerate(self.surfmesh['surftype'].unique()):
            cluster = self.surfmesh[self.surfmesh['surftype'] == surftype].geometry
            if surftype == 2: 
                cluster = cluster.buffer(0.001)
            merged_polygon = cluster.union_all()
            surftypes[i].append(merged_polygon)

        for i in range(len(surftypes)):
            gdf = surftypes[i]
            gdf = gpd.GeoDataFrame(geometry=surftypes[i], crs=self.surfmesh.crs)
            gdf = gdf.assign(group=1).dissolve(by='group')
            outfiles.append(gdf)
            gdf.to_file(Path(f"{outpath}/{surfnames[i]}.shp"))

        return outfiles
    

    


