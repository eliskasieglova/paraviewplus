import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from windrose import WindroseAxes
from shapely import LineString, Point
import scipy.interpolate as interp
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from shapely import Polygon, Point
import os


from inputs import SurfaceMesh, AirPoints, SurfacePoints, VariableChars

def create_folder_structure():

    cachepath = Path("cache/")
    if not cachepath.exists():
        os.mkdir(cachepath)

    figspath = Path("figs/")
    if not cachepath.exists():
        os.mkdir(figspath)

    datapath = Path("data/")
    if not datapath.exists():
        os.mkdir(datapath)


class AOIsOnMap(SurfacePoints, SurfaceMesh):

    def __init__(self, surfpoints, surfdata, surfmesh):
        SurfacePoints.__init__(self, surfpoints, surfdata)
        SurfaceMesh.__init__(self, surfmesh, surfdata)

        self.surfpoints = surfpoints
        self.surfdata = surfdata

        self.output_folder = None
        self.aois = []

        self.plot_type = "points"

        # TODO add option to color by temperature etc.

    def set_plot_type(self, plottype):
        self.plot_type = plottype  # TODO can only be points or mesh

    def add_area_of_interest(self, aoi):
        self.aois.append(aoi)

    def set_output_folder(self, output_folder):
        self.output_folder = output_folder

    def plot_mesh(self):
            # create new height column
            self.surfmesh['z'] = self.surfmesh.geometry.apply(
                lambda geom: np.mean([coord[2] for coord in geom.exterior.coords if len(coord) == 3])
            )

            # plot the surface mesh
            ax = self.surfmesh.plot(column="z", cmap="Spectral_r", legend=True, markersize=1)

            return ax

    def plot_points(self):

        # assign height column to the geodataframe
        self.surfpoints["height"] = self.surfpoints.geometry.z.values

        # plot the points (and color by height)
        ax = self.surfpoints.plot(column="height", cmap="Spectral_r", legend=True, markersize=1)

        return ax

    def _create_plot(self):
        """ Plots areas of interest (list of shapely polygons) on map. """

        if self.plot_type == "points":
            ax = self.plot_points()
        elif self.plot_type == "mesh":
            ax = self.plot_mesh()

        for aoi in self.aois:
            aoi = gpd.GeoSeries(aoi)
            aoi.plot(ax=ax, color='lightgrey', alpha=0.8, edgecolor='black', linewidth=2)

        # style plot
        plt.axis('equal')
        plt.title("Scatterplot of surface points colored by height (with areas of interest)")
        plt.xlabel("longitude")
        plt.ylabel("latitude")

    def plot(self):
        """ Show the plot. """
        self._create_plot()
        plt.show()

    def export(self):
        """ Export the plot. """

        self._create_plot()
        if self.output_folder is not None:
            plt.savefig(f"{self.output_folder}/aois_{self.plot_type}")
            plt.close()

class TimeSeriesDemonstration(SurfaceMesh, SurfacePoints, AirPoints, VariableChars):
    """
    A class to visualize time-series simulation data on a 2D mesh, specifically for
    surface and air properties across multiple variables.
    
    Attributes
    ----------
    surfpoints : gpd.GeoDataFrame
        Geospatial points of the surface. (Ferda folder: surface_point_shp.shp)
    surfdata : pd.DataFrame
        Data associated with the surface points. (Ferda folder: surface_data_2021_07_15.csv)
    airpoints : gpd.GeoDataFrame
        Geospatial air points. (Ferda folder: air_point_shp.shp)
    airdata : pd.DataFrame
        Data associated with the air points. (Ferda folder: air_data_2021_07_15.csv)
    surfmesh : gpd.GeoDataFrame
        Surface mesh. (Ferda folder: surface_triangle_shp.shp)
    """

    def __init__(self, surfpoints : gpd.GeoDataFrame, surfdata : pd.DataFrame, airpoints : gpd.GeoDataFrame, airdata : pd.DataFrame, surfmesh : gpd.GeoDataFrame, 
                 base_date : str) -> None:

        self.surfpoints = surfpoints
        self.surfdata = surfdata
        self.airpoints = airpoints
        self.airdata = airdata
        self.surfmesh = surfmesh
        self.base_date = datetime.strptime(base_date, "%d.%m.%Y")

        SurfacePoints.__init__(self, self.surfpoints, self.surfdata)
        AirPoints.__init__(self, self.airpoints, self.airdata)
        SurfaceMesh.__init__(self, self.surfmesh, surfdata)
        VariableChars.__init__(self)

        # creates walls and rooftops dataframes for plotting
        self.walls, self.rooftops = self._walls_rooftops()

        self.output_folder = None
        self.vars = []

        self.time = 1

    def add_variable(self, variable_name):
        if len(self.vars) > 4:
            raise ValueError("Only a max of 4 variables is allowed, if you want more, change the code..")
        self.vars.append(variable_name)

    def set_output_folder(self, output_folder):
        self.output_folder = output_folder

    def set_time(self, time):
        if time not in self.get_timesteps():
            raise ValueError(f"Selected time not in timesteps!! You selected {time} but timesteps are: {self.get_timesteps()}")
        else:
            self.time = time
    
    def _walls_rooftops(self):
        """ 
        Check if walls and rooftop files exist. If not, create walls and rooftop files. 
        Uses the function _classify_surfaces() from SurfaceMesh.
        """

        walls, ground, rooftops = self._classify_surfaces()

        return walls, rooftops

    def _layout_time_series_sim(self, fig, ax, contour, levels, ticks, variable_name):
        """ 
        Separate function for creating the layout for the plot. 
        
        Params:
        -------
        - fig: plt.Figure (current figure)
        - ax: plt.Axes (current axis)
        - contour: the contour plot (for creating the colorbar)
        - levels: the levels for contour plotting (categories/bins)
        - ticks: the ticks to show in the colorbar (not the same as levels)
        - variable_name: str (to set title)
        """

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
    
    def _plot_time_series_sim(self, fig, ax, variable_name, cmap):
        """
        Plots one subplot of the time series simulation based on the inputs.

        Params:
        ------
        - fig: plt.Figure (current figure)
        - ax: plt.Axes (current axis)
        - variable_name: current variable
        - cmap: selected colormap from the matplotlib defined colormaps
        - time: current timestep
        """

        if variable_name in self.surfdata.columns:
            merged = gpd.GeoDataFrame(pd.merge(self.surfdata, self.surfpoints[["cell_ID", "geometry"]])).dropna()
            subset = merged[merged["Time"] == self.time]
        else:
            merged = gpd.GeoDataFrame(pd.merge(self.airdata, self.airpoints[["cell_ID", "geometry"]])).dropna()
            subset = merged[merged["Time"] == self.time]

        # plot the surface
        import matplotlib.tri as tri
        triang = tri.Triangulation(subset.geometry.x, subset.geometry.y)
        if variable_name == "UTCI":
            levels = [9, 26, 32, 38, 46, 50]  # levels same as ticks for utci
            ticks = levels
            norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
            contour = ax.tricontourf(triang, subset[variable_name], levels=levels, cmap=cmap, norm=norm)
        elif variable_name == "WindDirection":
            self.plot_windflow(self.time)
        else: 
            if variable_name == "WindSpeed":
                min_value = 5 * (min(merged[variable_name]) // 5)
                max_value = 5 * (max(merged[variable_name]) // 5)
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
        self.walls.plot(ax=ax, edgecolor='black', linewidth=0.5)
        self.rooftops.plot(ax=ax, edgecolor='black', linewidth=0.5, color='white')

        if variable_name != "WindDirection":
            self._layout_time_series_sim(fig, ax, contour, levels, ticks, variable_name)

        return
    
    def _create_plot(self):
        """
        Runs the visualization for each timestep in the surface data, plotting
        multiple variables in a 2x2 subplot layout.
        TODO redo this to being adjustable (vars, subplots etc)
        """

        if len(self.vars) == 1:
            # setup
            fig, ax = plt.subplots(figsize=(9, 9))
            name = self.vars[0]
            cmap = self.get_cmap(self.vars[0])
            #cmap = self.cmaps[0]
            # run
            self._plot_time_series_sim(fig, ax, name, cmap)

        else: 
            if len(self.vars) == 2:
                # setup
                n, m = (1, 2)
                fig, axs = plt.subplots(n, m, figsize=(16, 9))
                ax_list = [axs[0], axs[1]]

            elif len(self.vars) == 3:
                n, m  = (1, 3)
                fig, axs = plt.subplots(n, m, figsize=(9, 9))
                ax_list = [axs[0], axs[1], axs[2]]

            elif len(self.vars) == 4:
                n, m = (2, 2)
                fig, axs = plt.subplots(n, m, figsize=(9, 9))
                ax_list = [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]

            # plot selected variables
            for i in range(len(self.vars)):
                name = self.vars[i]
                cmap = self.get_cmap(self.vars[i])
                ax = ax_list[i]
                # plot
                plt.subplot(n, m, i+1) 
                self._plot_time_series_sim(fig, ax, name, cmap)

        from datetime import timedelta

        new_datetime = self.base_date + timedelta(hours=int(self.time))

        plt.suptitle(f"Date: {new_datetime.strftime("%d.%m.%Y")} Time: {new_datetime.hour}H{new_datetime.minute}M", fontsize = 40)

    def plot(self):
        """ Show the plot. """
        self._create_plot()
        plt.show()

    def export(self):
        """ Save the plot as figure in output folder. """
        for time in self.get_timesteps():
            self.time = time
            self._create_plot()
            plt.savefig(f"{self.output_folder}/timeseries_{self.time}.png")
            plt.close()
        
class SimulationResults(SurfacePoints, VariableChars):
    """ Plots the simulation results for the chosen areas of interest in one plot for each selected variable. """

    def __init__(self, surfpoints : gpd.GeoDataFrame, surfdata : pd.DataFrame, variable_name : str) -> None:

        # input data
        self.surfpoints = surfpoints
        self.surfdata = surfdata
        self.variable_name = variable_name

        SurfacePoints.__init__(self, surfpoints, surfdata)
        VariableChars.__init__(self)

        self.areas_of_interest = []
        self.output_folder = None

        # plot visualization
        self.colors = ['blue', 'red', 'yellow', 'green', 'brown', 'pink']
        self.title = self.get_title(self.variable_name)
        self.note = ""

        # tkinter window

    def set_output_folder(self, output_folder):
        self.output_folder = output_folder

    def add_area_of_interest(self, aoi):
        self.areas_of_interest.append(aoi)

    def set_export(self, selection : bool):
        self.export = selection

    def set_show(self, selection : bool):
        self.show = selection

    def set_title(self, title):
        self.title = title
        return self.title
    
    def set_note(self, note):
        self.note = note

    def set_ylim(self, ylims):
        self.ylims = ylims
    
    def set_color(self, idx, color):
        self.colors[idx] = color

    def get_colors(self):
        return ['blue', 'red', 'yellow', 'green', 'brown', 'pink'][:len(self.areas_of_interest)]

    def update_plot(self, master):
        """
        Generates and displays a plot for a single simulation variable over time for all AOIs.

        Parameters:
        ----------
        variable_names : list of strings
            The variables to plot (e.g., []"Tair", "Tsurf", "UTCI"]). If no variable is chosen it defaults to all the variables
        colors : list of str, optional
            A list of colors for the areas of interest (AOIs). Defaults to ['blue', 'red', 'yellow', 'green'].
        """

        plot_frame = ctk.CTkFrame(master)

        self.fig, self.ax = plt.subplots(figsize=(12, 5), facecolor='#F2F2F2')

        colors = self.get_colors()

        # plot values
        self._build_plot(self.surfdata, self.areas_of_interest, self.variable_name, colors=colors)

        # apply layouts
        self._apply_plot_layout(self.ax, self.variable_name)
        self._plot_legend(self.ax)
        self.note = self._plot_note_text(self.variable_name)
        self.ax.set_title(self.title, fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        #self.root.update()

        return plot_frame

    # def show(self):
    #     self.update_plot()
    #     self.root.mainloop()

    def export(self):
        self.plot()
        plt.savefig(f'{self.output_folder}/' + f'{self.variable_name}.png')  
        plt.close()
    
    def exit(self):
        self.root.destroy()


class UTCICategory(SurfacePoints, SurfaceMesh):

    def __init__(self, surfpoints : gpd.GeoDataFrame, surfdata : pd.DataFrame, surfmesh : gpd.GeoDataFrame) -> None:
        self.surfpoints = surfpoints
        self.surfdata = surfdata

        SurfaceMesh.__init__(self, surfmesh, surfdata)
        SurfacePoints.__init__(self, surfpoints, surfdata)

        self.categories = []
    
        # creates walls and rooftops dataframes for plotting
        self.walls, self.rooftops = self._walls_rooftops()

        self.output_folder = None

    def set_output_folder(self, output_folder):
        self.output_folder = output_folder

    def _walls_rooftops(self):
        """ 
        Check if walls and rooftop files exist. If not, create walls and rooftop files. 
        Uses the function _classify_surfaces() from SurfaceMesh.
        """

        walls, ground, rooftops = self._classify_surfaces()

        return walls, rooftops

    def add_category(self, category):
        """ Add category to list of categories to plot. """
        self.categories.append(category)

    def remove_category(self, category):
        """ Remove category from list of categories to plot. """
        self.categories.remove(category)

    def _create_plot(self, cat, time):

        # Define UTCI categories and plotting colors
        utci = {
            'extreme': {'bounds': (46, 50), 'color': 'darkred'},
            'very_strong': {'bounds': (38, 46), 'color': 'red'},
            'strong': {'bounds': (32, 38), 'color': 'orangered'},
            'moderate': {'bounds': (26, 32), 'color': 'orange'},
            'no': {'bounds': (9, 26), 'color': 'lightgreen'}
        }

        fig, ax = plt.subplots()

        # extract area with UTCI according to selected temperature
        temps = self.surfdata[["cell_ID", "UTCI", "Time"]].dropna()
        temps = temps.where(temps["Time"] == time).dropna()

        # merge csv with gpd
        subset = gpd.GeoDataFrame(pd.merge(temps, self.surfpoints[["cell_ID", "geometry"]]))

        # plot the UTCI category
        contour = ax.tricontourf(subset.geometry.x, subset.geometry.y, subset.UTCI, levels=utci[cat]['bounds'], colors=utci[cat]["color"])

        # plot the surface (walls)
        self.walls.plot(ax=ax, edgecolor='black', linewidth=0.5)
        self.rooftops.plot(ax=ax, edgecolor='black', linewidth=0.5, color='white')
        ax.axis('off')
        plt.title(f'UTCI: {cat} (hour {time})')

    def export(self):
        for cat in self.categories:
            for time in self.get_timesteps():
                self._create_plot(cat, time)
                plt.savefig(self.output_folder + f"/utci/utci_{cat}_{time}.png")
                plt.close()

    def show(self):
        cat = self.categories[0]
        time = self.get_timesteps()[0]
        self._create_plot(cat, time)
        plt.show()


class SimulationComparison(SurfacePoints, VariableChars):

    def __init__(self, surfpoints : gpd.GeoDataFrame, surfdata : pd.DataFrame) -> None:
        self.surfpoints = surfpoints
        self.surfdata = surfdata

        SurfacePoints.__init__(self, self.surfpoints, self.surfdata) 
        VariableChars.__init__(self)

        self.simulations = [self.surfdata]
        self.sim_names = []
        self.variable_list = []
        self.aois = []

        self.output_folder = None
        self.letters = ["A", "B", "C", "D"]
        self.colors = ['red', 'blue', 'green', 'yellow']
        self.simulation_names = []

    def set_output_folder(self, output_folder):
        self.output_folder = output_folder

    def add_simulation(self, simulation : pd.DataFrame):
        """ 
        Add simulations to the list of simulations. These will be compared with the simulation given during initializing. 
        
        Params:
        ------
        - simulation : list of tuples [(pd.DataFrame, str)] | tuple (pd.DataFrame, str)
        """
        self.simulations.append(simulation)

    def change_colors(self, idx, new_color):
        self.colors[idx] = new_color

    def set_simulation_name(self, idx, sim_name):
        self.simulation_names[idx] = sim_name

    def add_variable(self, variable : str):
        self.variable_list.append(variable)

    def add_aoi(self, aoi):
        self.aois.append(aoi)
        
    def _create_plot(self, variable_name, aoi):
        
        fig, ax = plt.subplots(figsize=(12, 6))
        for i, simulation in enumerate(self.simulations):
            # plot values
            cell_IDs = self.surfpoints[self.surfpoints.within(aoi, align=True)]["cell_ID"].values.tolist()
            subset = simulation[simulation['cell_ID'].isin(cell_IDs)].dropna()

            cell_IDs = np.unique(subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
            timesteps = np.unique(subset.Time.values).tolist()  # get time steps
            avg_values = np.mean([subset[subset['cell_ID'] == id][variable_name].values for id in cell_IDs], axis=0)
            
            plt.plot(timesteps, avg_values, c=self.colors[i], label=f"Simulation {i+1}" if len(self.simulation_names) < len(self.simulations) else self.simulation_names[i])

        # apply layouts
        self._apply_plot_layout(ax, variable_name)
        self._plot_legend(ax)
        if variable_name == "UTCI":
            self._apply_utci_background(ax)
        #self._plot_note_text(variable_name)
        plt.title(f"{self.get_title(variable_name)} (Area {self.letters[i]}): Existing vs. New Design{'s' if len(self.simulations) > 2 else ''}",
                fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)
        
        return

    def export(self):
        if self.output_folder is None:
            raise ValueError("Output folder is not set.")
        """ Function for exporting. """
        for variable_name in self.variable_list:
            for i, aoi in enumerate(self.aois):
                self._create_plot(variable_name, aoi)
                plt.savefig(f"{self.output_folder}/comparison_{variable_name}_area{self.letters[i]}.png")
                plt.close()

    def show(self, variable_name="Tair", aoi=None):
        """ Function for showing the plot. """
        if aoi is None:  # Default AOI
            aoi = self.aois[0]

        self._create_plot(variable_name, aoi)
        plt.show()


class Windrose(AirPoints):

    def __init__(self, airpoints, airdata):
        super().__init__(airpoints, airdata)

        self.airpoints = airpoints
        self.airdata = airdata

        self.output_folder = None
        self.cmap = plt.cm.YlOrRd_r  # default colormap
        self.levels = None
        self.legend_loc = "upper left"

    def set_output_folder(self, output_folder):
        """ Set output folder. """
        self.output_folder = output_folder

    def set_cmap(self, cmap):
        """ For manual adjusting of colormap (step 3 or 4). """
        self.cmap = cmap

    def set_levels(self, levels):
        """ For manual adjusting of levels/bins/categories. """
        self.levels = levels

    def set_legend_location(self, legend_loc : str):
        """ For manual setting of legend location (step 3 or 4 - together with adjusting colormap). """
        self.legend_loc = legend_loc

    def _calculate_wind_directions(self):

        # Calculate wind directions (0-360 degrees) based on vector components in WindX and WindY
        wd = [(270 - np.degrees(np.arctan2(y, x))) % 360 for x, y in zip(self.df.WindX.values, self.df.WindY.values)]

        # assign wind directions
        self.airdata["WindDirection"]= wd

    def _calculate_levels(self, ws):

        # calculate levels
        levels = np.arange(int(np.floor(min(ws))), int(np.ceil(max(ws))) + 1, (min(ws) + max(ws)) / 10)
        levels = np.unique(np.round(levels).astype(int))

        # set levels
        self.levels = levels
        
    def _create_plot(self):
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

        self._calculate_wind_directions()

        wd = self.airdata.WindDirection.values
        ws = self.airdata.WindSpeed.values

        # calculate the levels if not specified
        if self.levels is None:
            self._calculate_levels(ws)

        # Set up the windrose plot
        ax = WindroseAxes.from_ax()
        
        # Plot filled contours with specified color map and levels
        ax.contourf(wd, ws, bins=self.levels, cmap=self.cmap, edgecolor="black")

        # Add legend
        ax.set_legend(title="Wind Speed (m/s)", loc=self.legend_loc)

    def export(self):
        self._create_plot()
        plt.savefig(f"{self.output_folder}/windrose.png")
        plt.close()

    def show(self):
        self._create_plot()
        plt.show()


class Slice(AirPoints, SurfacePoints, VariableChars):

    def __init__(self, gdf : gpd.GeoDataFrame, df : pd.DataFrame, slice : LineString, variable_name : str):
        super().__init__(gdf, df)

        VariableChars.__init__(self)

        self.gdf = gdf
        self.df = df
        self.slice = slice
        self.variable_name = variable_name

        self.resolution = 10
        self.buffer = 1

        self.output_folder = ""

    def add_variable(self, variable_name):
        self.variable_list.append(variable_name)

    def set_resolution(self, resolution):
        self.resolution = resolution
        
    def set_output_folder(self, output_folder):
        self.output_folder = output_folder
    
    def set_buffer(self, buffer):
        self.buffer = buffer
    
    def _slice(self):
        """ Selects subset of the points along selected line. Works for both 2d and 3d. """

        # create a small buffer around line
        buff = self.slice.buffer(self.buffer)

        # plot values along line
        points_along_line = self.gdf[self.gdf.within(buff)]

        # count distance from origin
        points_along_line["dist_from_origin"] = [Point(self.slice.coords[0]).distance(Point(point.x, point.y)) for point in points_along_line.geometry]

        return points_along_line

    def plot_slice_on_map(self):
        """ Plot map of the slice (from above). """

        fig, ax = plt.subplots()

        sc = ax.scatter(self.gdf.geometry.x, self.gdf.geometry.y, c=self.gdf.geometry.z, cmap="Spectral_r", s=1)
        slice_gdf = gpd.GeoSeries([self.slice]) 
        slice_gdf.plot(ax=ax, color='black', linewidth=2, label='Slice')

        # Add a colorbar to the plot
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Height (m)')  # You can change the label to describe what the color represents

        plt.legend()
        plt.title('Slice')

        plt.show()

    def plot_slice_3d(self):
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

        if self.variable_name is not None:
            data = pd.merge(self.gdf[["cell_ID"]], self.df)
            data = data[data["Time"] == 1]

        sc = ax.scatter(self.gdf.geometry.x, self.gdf.geometry.y, self.gdf.geometry.z, s=1, c=data[self.variable_name] if self.variable_name is not None else 'black',
                        cmap="Spectral_r")

        # plot 3d slice
        slice_2d = gpd.GeoSeries([self.slice]) 
        slice_coords = list(self.slice.coords) 
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
        if self.variable_name is not None:
            cbar = plt.colorbar(sc, ax=ax)
            cbar.set_label(self.units[self.variable_name])  

        # Set title
        plt.title('3D Slice' if self.variable_name is None else f"{self.titles[self.variable_name]}: 3D Slice")
        ax.set_zlim(0, 150)

        # Save figure, show if selected
        plt.savefig("paraviewplus/figs/3dslice.png")
        plt.show()

    def _create_plot(self):

        # Create slice and extract relevant points along the line
        points_along_line = self._slice()

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
        x_values = np.arange(min_x * 0.9, max_x + self.resolution, self.resolution)
        y_values = np.arange(min_y * 0.9, max_y + self.resolution, self.resolution)

        from shapely.geometry import box 

        for x in x_values:
            for y in y_values:
                cell = box(x, y, x + self.resolution, y + self.resolution)
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
            self.variable_name: lambda vals: np.nanmean([v for v in vals])  # Calculate mean z values
        }).reset_index()

        fishnet_avg['index_right'] = [int(x) for x in fishnet_avg['index_right']]

        # Merge back the average heights with the fishnet
        fishnet_gdf = pd.merge(fishnet_gdf, fishnet_avg, left_index=True, right_on='index_right', how='right')

        # colormap
        cmap = plt.get_cmap(self.get_cmap(self.variable_name))

        # Normalize the variable values for color mapping
        min_value = fishnet_gdf[self.variable_name].min()
        max_value = fishnet_gdf[self.variable_name].max()
        norm = plt.Normalize(vmin=min_value, vmax=max_value)

        # Assign colors based on variable_name using vmin and vmax for normalization
        fishnet_gdf["color"] = [cmap((value - min_value) / (max_value - min_value)) for value in fishnet_gdf[self.variable_name].values]

        # Plot the fishnet grid colored by the average heights
        fig, ax = plt.subplots()
        fishnet_gdf = fishnet_gdf.set_geometry('geometry')
        fishnet_gdf.plot(ax=ax, color=fishnet_gdf['color'], legend=True)

        # Add a colorbar to the plot
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # We don't need to set actual data here
        cbar = fig.colorbar(sm, ax=ax, shrink=0.5)

        # Add plot labels and title
        plt.xlabel('Distance from Origin')
        plt.ylabel('Height')
        plt.title(f'Plot of {self.variable_name} using Fishnet Grid')
        
    def export(self):
        self._create_plot()
        plt.savefig(self.output_folder + f"/slice_{self.variable_name}.png")
        plt.close()

    def show(self):
        self._create_plot
        plt.show()            


class Frequency(SurfacePoints):
    """
    Class for creating visualizations (pie chart or bar chart) that show the frequency (percentage) of 
    time steps when the selected variable exceeds a given threshold.
    """

    def __init__(self, gdf : gpd.GeoDataFrame, df : pd.DataFrame, variable_name : str):
        super().__init__(gdf, df)
        VariableChars.__init__(self)

        self.gdf = gdf
        self.df = df
        self.variable_name = variable_name
        self.threshold = 0
        self.aois = []  # List of Areas of Interest (AOIs)
        self.output_folder = ""  # Output folder for saving charts

    def set_threshold(self, threshold):
        """Set the threshold for counting the frequency."""
        self.threshold = threshold

    def add_area_of_interest(self, aoi):
        """Add an area of interest (AOI) to the list."""
        self.aois.append(aoi)

    def remove_area_of_interest(self, aoi):
        """Remove an area of interest (AOI) from the list."""
        self.aois.remove(aoi)

    def set_output_folder(self, output_folder):
        """Set the output folder for saving charts."""
        self.output_folder = output_folder

    def count_frequency(self, aoi):
        """
        Count the number of time steps where the variable exceeds the threshold.
        Returns a list: [count_below_threshold, count_above_threshold].
        """

        if isinstance(aoi, Point):
            # Handle AOI as a single point
            cell_id = self.gdf[self.gdf.geometry.within(aoi)] ["cell_ID"].values[0]
            values = self.df[self.df['cell_ID'] == cell_id][self.variable_name].values
        elif isinstance(aoi, Polygon):
            # Handle AOI as a polygon
            cell_ids = self.gdf[self.gdf.geometry.within(aoi)]["cell_ID"].values.tolist()
            subset = self.df[self.df['cell_ID'].isin(cell_ids)].dropna()
            values = subset.groupby('cell_ID')[self.variable_name].mean().values
        else:
            raise ValueError("AOI must be a Point or Polygon.")
        
        frequency_l = sum(value < self.threshold for value in values)
        frequency_u = sum(value >= self.threshold for value in values)

        return [frequency_l, frequency_u]

    def pie_chart(self):
        """Create a pie chart for a single AOI."""
        aoi = self.aois[0]

        if isinstance(aoi, Point):
            # Expand point to a small polygon buffer
            aoi_buffer = aoi.buffer(10)
            points_within_buffer = self.gdf[self.gdf.geometry.within(aoi_buffer)]
            points_within_buffer['distance'] = points_within_buffer.geometry.distance(aoi)
            nearest_3 = points_within_buffer.nsmallest(3, 'distance')
            aoi = Polygon(list(nearest_3.geometry)).buffer(0.00001)
    
        labels = [f'< {self.threshold} °C', f'> {self.threshold} °C']
        sizes = self.count_frequency(aoi)  # count frequency
        colors = ["darkblue", "darkred"]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors)

    def bar_plot(self):
        """Create a bar chart for multiple AOIs."""
        labels = [f'Area {i+1}' for i in range(len(self.aois))]
        counts = [self.count_frequency(aoi)[1] for aoi in self.aois]

        fig, ax = plt.subplots()
        ax.bar(labels, counts, color='darkred')
        ax.set_ylabel('Count Above Threshold')
        ax.set_title(f'Frequency of {self.get_title(self.variable_name)} > {self.threshold} {self.get_units(self.variable_name)}')

    def run(self):
        """Display the appropriate chart based on the number of AOIs."""
        if len(self.aois) == 1:
            self.pie_chart()
        elif len(self.aois) > 1:
            self.bar_plot()
        plt.show()

    def export(self):
        """Save the appropriate chart to the output folder."""
        if not self.output_folder:
            raise ValueError("Output folder is not set.")

        if len(self.aois) == 1:
            self.pie_chart()
        elif len(self.aois) > 1:
            self.bar_plot()
        plt.savefig(f'{self.output_folder}/chart.png')


class ComparisonMap(SurfacePoints, AirPoints, VariableChars, SurfaceMesh):

    def __init__(self, gdf : gpd.GeoDataFrame, df : pd.DataFrame):
        super().__init__(gdf, df)

        VariableChars.__init__(self)

        self.gdf = gdf
        self.simulations = []
        self.slice = slice
        self.variable_name = "Tair"  # variable name for plotting, default Tair but changable with set_variable()

        self.resolution = 10
        self.buffer = 1

        self.output_folder = ""  # output folder for export, changable with set_output_folder()

        self.simulations.append(df)  # append first simulation, add more with add_simulation(), max number of simulations is 6

        self.time = 1

        self.walls, self.rooftops = self._walls_rooftops()

        # plt specification
        self.cmap = ""
        self.min_value = 0
        self.max_value = 56

        self.ax_list = []

        base_date="30.7.2018"

    def set_cmap(self, cmap):
        self.cmap = cmap

    def set_min_value(self, all_values):
        self.min_value = 10 * (min(all_values) // 10)

    def set_max_value(self, all_values):
        self.max_value = 10 * (max(all_values) // 10)

    def set_variable(self, variable_name):
        # set variable (default "Tair")
        self.variable_name = variable_name

    def set_ax_list(self):
        self.ax_list = [i for ax in self.axs for i in ax]

    def set_time(self, time):
        if time not in self.get_timesteps():
            raise ValueError(f"Selected time not in timesteps!! You selected {time} but timesteps are: {self.get_timesteps()}")
        else:
            self.time = time

    def add_simulation(self, simulation : pd.DataFrame):
        # add another simulation 
        if len(self.simulations) > 6:
            raise ValueError("Maximum of 6 simulations for comparison is allowed, otherwise you have to add more if statements to 'create_plot()'")
        else:
            self.simulations.append(simulation)

    def remove_simulation(self, idx):
        # remove simulation based on id (position in list)
        self.simulations.remove(self.simulations[idx])

    def set_output_folder(self, output_folder):
        # set output folder - has to be done for export
        self.output_folder = output_folder

    def set_title(self):
        plt.suptitle(f"Time: {self.time}")

    def _create_plot_layout(self):
        l = len(self.simulations)

        # create figure with subplots based on number of simulations
        if l == 0:
            pass
        elif l == 1:
            n, m = 1, 1
        elif l == 2:
            n, m = 2, 1
        elif l == 3:
            n, m = 3, 1
        elif l == 4:
            n, m = 2, 2
        elif l == 5:
            n, m = 3, 2
        elif l == 6:
            n, m = 3, 2

        self.fig, self.axs = plt.subplots(n, m)
        self.set_ax_list()  # convert the ndarray of axes to a list

    def add_cbar(self):
        # add custom colorbar based on input data
        cbar = self.fig.colorbar(self.contour, ax=self.axs, orientation='vertical', shrink=0.8, aspect=30, ticks=self.ticks)  # add and position cbar
        cbar.ax.tick_params(labelsize=8)  # tick parameters (font size)
        cbar.ax.set_ylabel(self.get_title(self.variable_name), fontsize=8) #rotation=-90, labelpad=9)   # optional turn of label

        cbar.outline.set_visible(False)  # turn off black background of cbar
        
        return

    def _create_plot(self):
        """
        Create plot 
        """

        # initiate plot layout
        self._create_plot_layout()

        # set colormap for the whole thing
        cmap = self.get_cmap(self.variable_name)

        # set mins aand maxs for the whole thing
        all_values = pd.concat([d[self.variable_name] for d in self.simulations])
        #min_value = 10 * (min(all_values) // 10)
        #max_value = 10 * (max(all_values) // 10)

        self.set_min_value(all_values)
        self.set_max_value(all_values)
        self.set_cmap(cmap)

        # loop through the uploaded simulations
        for i in range(len(self.simulations)):
            ax = self.ax_list[i]  # take according axis from the list
            
            # plot walls and rooftops
            self.walls.plot(ax=ax, edgecolor='black', linewidth=0.5, zorder=2)  # zorder puts this above the variable
            self.rooftops.plot(ax=ax, edgecolor='black', linewidth=0.5, color='white', zorder=3)  # zorder puts this above the variable and the walls

            # set title of plot
            self.set_title()

            # fill the plot with data (based on variable)
            self.update_plot()

            # Remove the axes
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_frame_on(False)

        # add cbar
        self.add_cbar()

    def update_plot(self):
        """
        Update existing plot by adding the data based on the selected variable. The plot should already be created in create_plot() together
        with plotting the buildings (walls and rooftops).
        """
        # loop through simulations
        for i, sim in enumerate(self.simulations):
            ax = self.ax_list[i]  # select axis from list of axes (generated in when creating plot layout)

            # merge the simulation with the geodataframe TODO could be a better way to do this?
            merged = gpd.GeoDataFrame(pd.merge(sim[["cell_ID", self.variable_name, "Time"]], self.gdf[["cell_ID", "geometry"]])).dropna()
            subset = merged[merged["Time"] == self.time]  # select subset for the selected timestep

            # plot the surface
            import matplotlib.tri as tri
            triang = tri.Triangulation(subset.geometry.x, subset.geometry.y)
            if self.variable_name == "UTCI":
                self.levels = [9, 26, 32, 38, 46, 50]  # levels same as ticks for utci
                self.ticks = self.levels
                norm = BoundaryNorm(self.levels, ncolors=self.cmap.N, clip=True)
                self.contour = ax.tricontourf(triang, subset[self.variable_name], levels=self.levels, cmap=self.cmap, norm=norm, zorder=1)
            else: 
                if self.variable_name == "Tair":
                    self.levels = np.arange(self.min_value, self.max_value + 1, 1)
                    self.ticks = np.arange(self.min_value, self.max_value + 1, 5)
                elif self.variable_name == "WindSpeed":
                    self.levels = np.arange(self.min_value, self.max_value + 1, 1)
                    self.ticks = np.arange(self.min_value, self.max_value + 1, 5)
                elif self.variable_name == "RelatHumid":
                    self.levels = np.arange(0, 1.1, 0.1)
                    self.ticks = np.arange(0, 1.1, 0.2)

                self.contour = ax.tricontourf(triang, subset[self.variable_name], levels=self.levels, cmap=self.cmap, zorder=1)
    
    def _walls_rooftops(self):
        """ 
        Check if walls and rooftop files exist. If not, create walls and rooftop files. 
        Uses the function _classify_surfaces() from SurfaceMesh.
        """

        walls, ground, rooftops = self._classify_surfaces()

        return walls, rooftops  # TODO make this more effective also together with timeseriesdemonstration

    def run(self):
        """ Create and show the plot. """
        self._create_plot()
        plt.show()

    def update(self):
        """ Update data in existing plot without loading walls and rooftops again. """
        self.update_plot()
        self.set_title()
        #plt.show()

    def export(self):
        """ Export plots for all existing timesteps. """

        # create directory if it doesn't exist yet
        dir = Path(f"{self.output_folder}/comparison_time_series/")
        if not dir.exists():
            os.mkdir(dir)

        # create and export the plots
        for time in self.get_timesteps():
            self.time = time
            self._create_plot()
            plt.savefig(dir / Path(f"comparisontimeseries_{self.time}.png"))
            plt.close()  # close so that the memory does not get overloaded

        











