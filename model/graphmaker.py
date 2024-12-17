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
from model.inputs import SurfaceMesh, AirPoints, SurfacePoints, VariableChars


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

    def __init__(self, surfpoints : gpd.GeoDataFrame, surfdata : pd.DataFrame, airpoints : gpd.GeoDataFrame, airdata : pd.DataFrame, surfmesh : gpd.GeoDataFrame) -> None:

        self.surfpoints = surfpoints
        self.surfdata = surfdata
        self.airpoints = airpoints
        self.airdata = airdata
        self.surfmesh = surfmesh

        SurfacePoints.__init__(self, self.surfpoints, self.surfdata)
        AirPoints.__init__(self, self.airpoints, self.airdata)
        SurfaceMesh.__init__(self, self.surfmesh, surfdata)
        VariableChars.__init__(self)

        # creates walls and rooftops dataframes for plotting
        self.walls, self.rooftops = self._walls_rooftops()

        self.output_folder = None
        self.vars = []

    def add_variable(self, variable_name):
        self.vars.append(variable_name)

    def set_output_folder(self, output_folder):
        self.output_folder = output_folder
    
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
        cax = self.ax.inset_axes([0.65, -0.05, 0.4, 0.02]) 
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
    
    def _plot_time_series_sim(self, fig, ax, variable_name, cmap, time):
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
            subset = merged[merged["Time"] == time]
        else:
            merged = gpd.GeoDataFrame(pd.merge(self.airdata, self.airpoints[["cell_ID", "geometry"]])).dropna()
            subset = merged[merged["Time"] == time]

        # plot the surface
        import matplotlib.tri as tri
        triang = tri.Triangulation(subset.geometry.x, subset.geometry.y)
        if variable_name == "UTCI":
            levels = [9, 26, 32, 38, 46, 50]  # levels same as ticks for utci
            ticks = levels
            norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
            contour = ax.tricontourf(triang, subset[variable_name], levels=levels, cmap=cmap, norm=norm)
        elif variable_name == "WindDirection":
            self.plot_windflow(time)
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
            self._layout_time_series_sim(fig, self.ax, contour, levels, ticks, variable_name)

        return
    
    def _create_plot(self,master, time):
        """
        Runs the visualization for each timestep in the surface data, plotting
        multiple variables in a 2x2 subplot layout.
        TODO redo this to being adjustable (vars, subplots etc)
        """
        self.figsize = (9, 9)
        
        self.master_frame = master

        plot_frame = ctk.CTkFrame(master)

        if len(self.vars) == 1:
            # setup
            
            self.fig, self.ax = plt.subplots(figsize=self.figsize)
            name = self.vars[0]
            cmap = self.get_cmap(self.vars[0])
            #cmap = self.cmaps[0]
            # run
            self._plot_time_series_sim(self.fig, self.ax, name, cmap, time)

        else: 
            if len(self.vars) == 2:
                # setup
                n, m = (1, 2)
                self.fig, axs = plt.subplots(n, m, figsize=self.figsize, facecolor='#F2F2F2')
                ax_list = [axs[0], axs[1]]

            elif len(self.vars) == 3:
                n, m  = (1, 3)
                self.fig, axs = plt.subplots(n, m, figsize=self.figsize, facecolor='#F2F2F2')
                ax_list = [axs[0], axs[1], axs[2]]

            elif len(self.vars) == 4:
                n, m = (2, 2)
                self.fig, axs = plt.subplots(n, m, figsize=self.figsize, facecolor='#F2F2F2')
                ax_list = [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]

            # plot selected variables
            for i in range(len(self.vars)):
                name = self.vars[i]
                cmap = self.get_cmap(self.vars[i])
                self.ax = ax_list[i]
                # plot
                plt.subplot(n, m, i+1) 
                self._plot_time_series_sim(self.fig, self.ax, name, cmap, time)

        self.title_content = f"Time: {time}"
        self.plot_title = self.fig.suptitle(self.title_content, fontsize = 16)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        return plot_frame

    def plot(self, time=7):
        """ Show the plot. """
        self._create_plot(time)
        plt.show()

    def export(self):
        """ Save the plot as figure in output folder. """
        for time in self.get_timesteps():
            self._create_plot(time)
            plt.savefig(f"{self.output_folder}/timeseries_{time}.png")
            plt.close()
   
    def remove_title(self):
        self.plot_title = self.fig.suptitle(" ")
        self.canvas.draw()
        
    def set_plot_title(self, text):
        self.title_content = text
        self.plot_title = self.fig.suptitle(self.title_content)
        self.canvas.draw()
        
    def update_plot_time(self, time):
        if len(self.vars) == 1:
            # setup
            self.fig, self.ax = plt.subplots(figsize=self.figsize)
            name = self.vars[0]
            cmap = self.get_cmap(self.vars[0])
            # run
            self._plot_time_series_sim(self.fig, self.ax, name, cmap, time)

        else: 
            if len(self.vars) == 2:
                # setup
                n, m = (1, 2)
                self.fig, axs = plt.subplots(n, m, figsize=self.figsize, facecolor='#F2F2F2')
                ax_list = [axs[0], axs[1]]

            elif len(self.vars) == 3:
                n, m  = (1, 3)
                self.fig, axs = plt.subplots(n, m, figsize=self.figsize, facecolor='#F2F2F2')
                ax_list = [axs[0], axs[1], axs[2]]

            elif len(self.vars) == 4:
                n, m = (2, 2)
                self.fig, axs = plt.subplots(n, m, figsize=self.figsize, facecolor='#F2F2F2')
                ax_list = [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]

            # plot selected variables
            for i in range(len(self.vars)):
                name = self.vars[i]
                cmap = self.get_cmap(self.vars[i])
                self.ax = ax_list[i]
                # plot
                plt.subplot(n, m, i+1) 
                self._plot_time_series_sim(self.fig, self.ax, name, cmap, time)

        self.plot_title = self.fig.suptitle(" ")
        self.title_content = f"Time: {time}"
        self.plot_title = self.fig.suptitle(self.title_content, fontsize = 38)
        
        self.canvas.draw()

    def update_font_size(self, value):
        self.plot_title = self.fig.suptitle(self.title_content, fontsize=value)
        self.canvas.draw()        

        
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

    def get_colors(self,length_of_aois):
        return ['blue', 'red', 'yellow', 'green', 'brown', 'pink'][:length_of_aois]

    def get_variables(self):
        available_var_list = ['Tair', 'ET', 'UTCI','Tsurf', 'RelatHumid']
        return available_var_list

    def create_plot(self, master):
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

        self.colors = self.get_colors(len(self.areas_of_interest))

        # plot values
        self._build_plot(self.surfdata, self.areas_of_interest, self.variable_name, colors=self.colors)

        # apply layouts
        self._apply_plot_layout(self.ax, self.variable_name)
        self.legend = self._plot_legend(self.ax)
        self.note = self._plot_note_text(self.variable_name)
        self.plot_title = self.ax.set_title(self.title, fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        #self.root.update()

        return plot_frame

    def update_plot(self, variable):
        self.variable_name = variable
        
        self.ax.clear()
        self.note.remove()
        self.title = self.get_title(self.variable_name)
        # plot values
        self._build_plot(self.surfdata, self.areas_of_interest, self.variable_name, colors=self.colors)

        # apply layouts
        self._apply_plot_layout(self.ax, self.variable_name)
        self.legend = self._plot_legend(self.ax)
        self.note = self._plot_note_text(self.variable_name)
        self.plot_title = self.ax.set_title(self.title, fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)
        
        self.canvas.draw()
        
    def remove_legend(self):
        self.legend.remove()
        self.canvas.draw()
        
    def set_legend(self):
        self.legend = self._plot_legend(self.ax) 
        self.canvas.draw()
        
    def remove_title(self):
        self.plot_title = self.ax.set_title("")
        self.canvas.draw()
        
    def set_plot_title(self):
        self.plot_title = self.ax.set_title(self.title, fontsize=18, fontweight='bold', y=1.1)
        self.canvas.draw()
        
    def remove_note(self):
        if self.note is not None:  # Check if a note exists
            self.note.remove()     # Remove the old note
            self.note = None       # Reset the reference
            self.canvas.draw()
        
    def set_plot_note(self, text):
        if self.note is not None:  # Check if a note exists
            self.note.remove()     # Remove the old note

        # Add the new note to the plot
        self.note = self.fig.text(
            0.5, 0.05,
            r"$\mathbfit{" + "Note:" + "}$ " + text,
            wrap=True,
            horizontalalignment='center',
            fontsize=10,
            fontstyle='italic'
        )
        self.canvas.draw()  # Redraw the canvas
        
    def hide_axis_label(self):
        self.ax.xaxis.label.set_visible(False)  # Hides the X-axis label
        self.ax.yaxis.label.set_visible(False)  # Hides the Y-axis label
        self.canvas.draw()
        
    def show_axis_label(self):
        self.ax.xaxis.label.set_visible(True)  # Hides the X-axis label
        self.ax.yaxis.label.set_visible(True)  # Hides the Y-axis label
        self.canvas.draw()        
       
    def set_max_ylims(self,number):
        #check number validity
        if number <= self.ylims[0]:
            raise Exception("Sorry, no numbers below zero") 
        
        # set the new limits
        self.ylims = (self.ylims[0], number)
        self.ax.set_ylim(self.ylims)
        
        # Change ticks depending on the visible degrees
        if (self.ylims[1] - self.ylims[0]) < 25:
            self.yticks = (np.arange(self.ylims[0], number, step=5))
        else:
            self.yticks = (np.arange(self.ylims[0], number, step=10))
        self.ax.set_yticks(self.yticks)  
        self.canvas.draw() 
        
    def set_min_ylims(self,number):
        #check number validity
        if number >= self.ylims[1]:
            raise Exception("Sorry, no numbers below zero")
        
        # set the new limits
        self.ylims = (number, self.ylims[1])
        self.ax.set_ylim(self.ylims)
        
        # Change ticks depending on the visible degrees
        if (self.ylims[1] - self.ylims[0]) < 25:
            self.yticks = (np.arange(number, self.ylims[1], step=5))
        else:
            self.yticks = (np.arange(number, self.ylims[1], step=10))      
        
        self.yticks = (np.arange(number, self.ylims[1], step=10))
        self.ax.set_yticks(self.yticks)  
        self.canvas.draw() 
        
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

        self.categories = ['extreme', 'very_strong', 'strong', 'moderate', 'no']
    
        # creates walls and rooftops dataframes for plotting
        self.walls, self.rooftops = self._walls_rooftops()

        self.output_folder = None
        
        self.cat = self.categories[-1]
        self.time = 12
        self.show_title = True
        self.title_content = ''

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

    def _create_plot(self,master):



        # Define UTCI categories and plotting colors
        self.utci = {
            'extreme': {'bounds': (46, 50), 'color': 'darkred'},
            'very_strong': {'bounds': (38, 46), 'color': 'red'},
            'strong': {'bounds': (32, 38), 'color': 'orangered'},
            'moderate': {'bounds': (26, 32), 'color': 'orange'},
            'no': {'bounds': (9, 26), 'color': 'lightgreen'}
        }

        plot_frame = ctk.CTkFrame(master)

        self.fig, self.ax = plt.subplots(dpi=100, facecolor='#F2F2F2')
        #self.fig.subplots_adjust(left=0.15, bottom=0.05, right=0.6, top=0.92, wspace=0.2, hspace=0.2)

        # extract area with UTCI according to selected temperature
        self.temps = self.surfdata[["cell_ID", "UTCI", "Time"]].dropna()
        self.temps2 = self.temps.where(self.temps["Time"] == self.time).dropna()

        # merge csv with gpd
        self.subset = gpd.GeoDataFrame(pd.merge(self.temps2, self.surfpoints[["cell_ID", "geometry"]]))

        # plot the UTCI category
        self.contour = self.ax.tricontourf(self.subset.geometry.x, self.subset.geometry.y, self.subset.UTCI, levels=self.utci[self.cat]['bounds'], colors=self.utci[self.cat]["color"],zorder=1)

        # plot the surface (walls)
        self.walls.plot(ax=self.ax, edgecolor='black', linewidth=0.5,zorder=2)
        self.rooftops.plot(ax=self.ax, edgecolor='black', linewidth=0.5, color='#F2F2F2',zorder=2)
        self.ax.axis('off')
        self.title_content = f'UTCI: {self.cat} (hour {self.time})'
        self.plot_title = self.ax.set_title(self.title_content)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both',expand=True)
        
        return plot_frame

    def update_plot_time(self, hour):
        
        self.time = hour
        
        for coll in self.contour.collections:
            coll.remove()
            
        self.temps2 = self.temps.where(self.temps["Time"] == self.time).dropna()

        # merge csv with gpd
        new_subset = gpd.GeoDataFrame(pd.merge(self.temps2, self.surfpoints[["cell_ID", "geometry"]]))
        
        # Create a new contour plot with updated data 
        self.contour = self.ax.tricontourf(new_subset.geometry.x, new_subset.geometry.y, new_subset.UTCI, levels=self.utci[self.cat]['bounds'], colors=self.utci[self.cat]["color"],zorder=1)
        if self.show_title:
            self.title_content = f'UTCI: {self.cat} (hour {self.time})'
            self.plot_title = self.ax.set_title(self.title_content)
        self.canvas.draw()
        
    def update_plot_category(self, cat):
        
        self.cat = cat

        for coll in self.contour.collections:
            coll.remove()
        
        self.contour = self.ax.tricontourf(self.subset.geometry.x, self.subset.geometry.y, self.subset.UTCI, levels=self.utci[self.cat]['bounds'], colors=self.utci[self.cat]["color"],zorder=1)
        if self.show_title:
            self.title_content = f'UTCI: {self.cat} (hour {self.time})'
            self.plot_title = self.ax.set_title(self.title_content)
        self.canvas.draw()

    def remove_title(self):
        self.show_title = False
        self.plot_title = self.ax.set_title("")
        self.canvas.draw()
        
    def set_title(self,value):
        self.show_title = True
        self.title_content = value
        self.plot_title = self.ax.set_title(self.title_content)
        self.canvas.draw()    

    def update_font_size(self, value):
        self.plot_title = self.ax.set_title(self.title_content, fontsize= value)
        self.canvas.draw()
        
                  
    # def export(self):
    #     for cat in self.categories:
    #         for time in self.get_timesteps():
    #             self._create_plot(cat, time)
    #             plt.savefig(self.output_folder + f"/utci/utci_{cat}_{time}.png")
    #             plt.close()


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
        
        self.colors = ['red', 'blue', 'green', 'yellow']
        self.simulation_names = []
        
        self.sims_lines = {}

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
        
    def _create_plot(self, master, variable_name, selected_area):
        
        
        
        plot_frame = ctk.CTkFrame(master)
        
        self.fig, self.ax = plt.subplots(figsize=(12, 6), facecolor='#F2F2F2')
        
        
        for i, simulation in enumerate(self.simulations):
            # plot values
            self.cell_IDs = self.surfpoints[self.surfpoints.within(self.aois[selected_area], align=True)]["cell_ID"].values.tolist()
            self.subset = simulation[simulation['cell_ID'].isin(self.cell_IDs)].dropna()

            self.cell_IDs = np.unique(self.subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
            self.timesteps = np.unique(self.subset.Time.values).tolist()  # get time steps
            avg_values = np.mean([self.subset[self.subset['cell_ID'] == id][variable_name].values for id in self.cell_IDs], axis=0)
            
            line, = plt.plot(self.timesteps, avg_values, c=self.colors[i], label=f"Simulation {i+1}" if len(self.simulation_names) < len(self.simulations) else self.simulation_names[i])
            self.sims_lines[i] = line


        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # apply layouts
        self._apply_plot_layout(self.ax, variable_name)
        self.plot_legend = self._plot_legend(self.ax)
        if variable_name == "UTCI":
            self._apply_utci_background(self.ax)
        #self._plot_note_text(variable_name)

        self.plot_title = self.ax.set_title(f"{self.get_title(variable_name)} (Area {chr(65+selected_area)}): Existing vs. New Design{'s' if len(self.simulations) > 2 else ''}",
                fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)
        
        return plot_frame
    
    def update_plot(self, variable_name, selected_area):
        
        self.ax.clear()

        for i, simulation in enumerate(self.simulations):
            # plot values
            self.cell_IDs = self.surfpoints[self.surfpoints.within(self.aois[selected_area], align=True)]["cell_ID"].values.tolist()
            self.subset = simulation[simulation['cell_ID'].isin(self.cell_IDs)].dropna()

            self.cell_IDs = np.unique(self.subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
            self.timesteps = np.unique(self.subset.Time.values).tolist()  # get time steps
            avg_values = np.mean([self.subset[self.subset['cell_ID'] == id][variable_name].values for id in self.cell_IDs], axis=0)
            
            line, = plt.plot(self.timesteps, avg_values, c=self.colors[i], label=f"Simulation {i+1}" if len(self.simulation_names) < len(self.simulations) else self.simulation_names[i])
            self.sims_lines[i] = line


        # apply layouts
        self._apply_plot_layout(self.ax, variable_name)
        self.plot_legend = self._plot_legend(self.ax)
        if variable_name == "UTCI":
            self._apply_utci_background(self.ax)
        #self._plot_note_text(variable_name)

        self.plot_title = self.ax.set_title(f"{self.get_title(variable_name)} (Area {chr(65+selected_area)}): Existing vs. New Design{'s' if len(self.simulations) > 2 else ''}",
                fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2) 
        
        self.canvas.draw()       
       
    
    def remove_legend(self):
        self.plot_legend.remove()
        self.canvas.draw()
        
    def set_legend(self):
        self.plot_legend = self._plot_legend(self.ax) 
        self.canvas.draw()

    def hide_axis_label(self):
        self.ax.xaxis.label.set_visible(False)  # Hides the X-axis label
        self.ax.yaxis.label.set_visible(False)  # Hides the Y-axis label
        self.canvas.draw()
        
    def show_axis_label(self):
        self.ax.xaxis.label.set_visible(True)  # Hides the X-axis label
        self.ax.yaxis.label.set_visible(True)  # Hides the Y-axis label
        self.canvas.draw()        
   

    def remove_title(self):
        self.plot_title = self.ax.set_title("")
        self.canvas.draw()
        
    def set_new_title(self, new_title):
        self.plot_title = self.ax.set_title( new_title, fontsize=18, fontweight='bold', y=1.1)
        self.canvas.draw()
        
    def set_max_ylims(self,number):
        #check number validity
        if number <= self.ylims[0]:
            raise Exception("Sorry, no numbers below zero") 
        
        # set the new limits
        self.ylims = (self.ylims[0], number)
        self.ax.set_ylim(self.ylims)
        
        # Change ticks depending on the visible degrees
        if (self.ylims[1] - self.ylims[0]) < 25:
            self.yticks = (np.arange(self.ylims[0], number, step=5))
        else:
            self.yticks = (np.arange(self.ylims[0], number, step=10))
        self.ax.set_yticks(self.yticks)  
        self.canvas.draw() 
        
    def set_min_ylims(self,number):
        #check number validity
        if number >= self.ylims[1]:
            raise Exception("Sorry, no numbers below zero")
        
        # set the new limits
        self.ylims = (number, self.ylims[1])
        self.ax.set_ylim(self.ylims)
        
        # Change ticks depending on the visible degrees
        if (self.ylims[1] - self.ylims[0]) < 25:
            self.yticks = (np.arange(number, self.ylims[1], step=5))
        else:
            self.yticks = (np.arange(number, self.ylims[1], step=10))      
        
        self.yticks = (np.arange(number, self.ylims[1], step=10))
        self.ax.set_yticks(self.yticks)  
        self.canvas.draw() 
         

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
        
    def _create_plot(self, master):
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
            
        # Create a frame for the windrose plot
        plot_frame = tk.Frame(master)
        plot_frame.pack(fill="both", expand=True)

        self.fig = plt.Figure(figsize=(5, 5),facecolor='#F2F2F2')
        self.ax = WindroseAxes.from_ax(fig=self.fig)
        
        # Plot filled contours with specified color map and levels
        self.ax.contourf(wd, ws, bins=self.levels, cmap=self.cmap, edgecolor="black")

        # Add legend
        self.legends = self.ax.set_legend(title="Wind Speed (m/s)", loc=self.legend_loc)
        
        self.title_content = ''
        self.plot_title = self.fig.suptitle(self.title_content, fontsize=18)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        return plot_frame


    def remove_title(self):
        self.plot_title = self.fig.suptitle("", fontsize=18)
        self.canvas.draw()
        
    def set_plot_title(self, text):
        self.title_content = text
        self.plot_title = self.fig.suptitle(self.title_content, fontsize=16)
        self.canvas.draw()

    def remove_legends(self):
        self.ax.clear()
        self.ax.contourf(self.airdata.WindDirection.values, self.airdata.WindSpeed.values, bins=self.levels, cmap=self.cmap, edgecolor="black")
        self.canvas.draw()
        
    def set_legends(self):
        self.legends = self.ax.set_legend(title="Wind Speed (m/s)", loc=self.legend_loc)
        
        self.canvas.draw()
    
    def color_change(self, cmap_name): 
        self.ax.clear()
        cmap = plt.cm.get_cmap(cmap_name)
        self.ax.contourf(self.airdata.WindDirection.values, self.airdata.WindSpeed.values, bins=self.levels, cmap=cmap, edgecolor="black")
        self.canvas.draw()

    def update_font_size(self, count):
        self.plot_title = self.fig.suptitle(self.title_content, fontsize=count)     
        self.canvas.draw()
  
       
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
        self.time = 12

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

    def _create_plot_data(self):
        
        # Create slice and extract relevant points along the line
        points_along_line = self._slice()

        # Merge gdf with df
        points_along_line = points_along_line[["cell_ID", "geometry", "dist_from_origin"]]
        merged = pd.merge(points_along_line, self.df, how="left", on="cell_ID")

        # Filter data for the selected time 
        subset = merged[merged["Time"] == self.time].sort_values("dist_from_origin").copy()

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

        self.fishnet_gdf = gpd.GeoDataFrame(geometry=fishnet, crs=points_along_line.crs)
        # Create a GeoDataFrame where geometry is based on dist_from_origin and geometry.z
        points_gdf = gpd.GeoDataFrame(
            subset,
            geometry=[Point(x, z) for x, z in zip(subset["dist_from_origin"], subset.geometry.z)],
            crs=points_along_line.crs
        )

        # Spatial join to match points to fishnet cells
        joined = gpd.sjoin(points_gdf, self.fishnet_gdf, how='left', predicate='within')

        # Check if any points were joined
        print(joined['index_right'].isna().sum(), "points did not match any fishnet cell")

        # Calculate average height values (geometry.z) within each cell of the fishnet
        fishnet_avg = joined.groupby('index_right').agg({
            self.variable_name: lambda vals: np.nanmean([v for v in vals])  # Calculate mean z values
        }).reset_index()

        fishnet_avg['index_right'] = [int(x) for x in fishnet_avg['index_right']]

        # Merge back the average heights with the fishnet
        self.fishnet_gdf = pd.merge(self.fishnet_gdf, fishnet_avg, left_index=True, right_on='index_right', how='right')

        # colormap
        self.cmap = plt.get_cmap(self.get_cmap(self.variable_name))

        # Normalize the variable values for color mapping
        self.min_value = self.fishnet_gdf[self.variable_name].min()
        self.max_value = self.fishnet_gdf[self.variable_name].max()
        self.norm = plt.Normalize(vmin=self.min_value, vmax=self.max_value)

        # Assign colors based on variable_name using vmin and vmax for normalization
        self.fishnet_gdf["color"] = [self.cmap((value - self.min_value) / (self.max_value - self.min_value)) for value in self.fishnet_gdf[self.variable_name].values]

        return self.fishnet_gdf["color"]

    def _create_plot(self, master):
        
        data = self._create_plot_data()

        plot_frame = ctk.CTkFrame(master)

        # Plot the fishnet grid colored by the average heights
        self.fig, self.ax = plt.subplots(facecolor='#F2F2F2')
        self.fishnet_gdf = self.fishnet_gdf.set_geometry('geometry')
        self.fishnet_gdf.plot(ax=self.ax, color=data, legend=True)

        # Add a colorbar to the plot
        self.sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=self.norm)
        self.sm.set_array([])  # We don't need to set actual data here
        self.cbar = self.fig.colorbar(self.sm, ax=self.ax, shrink=0.5)

        # Add plot labels and title
        self.xaxis = plt.xlabel('Distance from Origin')
        self.yaxis = plt.ylabel('Height')
        
        self.title_content = f'Plot of {self.variable_name} using Fishnet Grid'
        self.title = self.ax.set_title(self.title_content)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        return plot_frame
    
    def update_plot(self):
        # Recreate the plot data
        data = self._create_plot_data()

        # Clear the existing plot from the axis
        self.ax.clear()

        # Replot the fishnet grid with updated data
        self.fishnet_gdf = self.fishnet_gdf.set_geometry('geometry')
        self.fishnet_gdf.plot(ax=self.ax, color=data, legend=True)

        # Add the colorbar to the plot
        if hasattr(self, 'cbar'):
            self.cbar.remove()  # Remove the previous colorbar
        self.sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=self.norm)
        self.sm.set_array([])  # No actual data is needed here
        self.cbar = self.fig.colorbar(self.sm, ax=self.ax, shrink=0.5)

        # Add plot labels and title again
        self.ax.set_xlabel('Distance from Origin')
        self.ax.set_ylabel('Height')
        self.ax.set_title(self.title_content)

        self.fig.tight_layout(rect=[0, 0, 1, 0.95])  # Optional: adjust the rect to fit colorbar and title

        # Redraw the canvas to reflect changes
        self.canvas.draw() 
   
    def set_new_title(self, text):
        self.title_content = text
        self.ax.set_title(self.title_content)   
        self.canvas.draw() 
        
    def remove_title(self):
        self.title = self.ax.set_title("")  
        self.canvas.draw() 
        
    def remove_colorbar(self):
        self.cbar.remove()  # Remove the colorbar from the figure
        self.cbar = None  # Reset the reference
        self.canvas.draw()
        
    def set_new_colorbar(self):
        self.cbar = self.fig.colorbar(self.sm, ax=self.ax)
        self.canvas.draw()
        
    def set_new_cmap(self, cmap):
        
        self.ax.clear()
        
        cmap = plt.cm.get_cmap(cmap)
        self.fishnet_gdf["color"] = [cmap((value - self.min_value) / (self.max_value - self.min_value)) for value in self.fishnet_gdf[self.variable_name].values]
        self.fishnet_gdf.plot(ax=self.ax, color=self.fishnet_gdf['color'], legend=True)
    
        self.cbar.remove()  # Remove the colorbar from the figure
        self.cbar = None  # Reset the reference
        self.sm = plt.cm.ScalarMappable(cmap=cmap, norm=self.norm)    
        self.sm.set_array([])  # We don't need to set actual data here
        self.cbar = self.fig.colorbar(self.sm, ax=self.ax)
        
        self.canvas.draw()
    
    def remove_axis(self):
        self.ax.xaxis.label.set_visible(False)  # Hides the X-axis label
        self.ax.yaxis.label.set_visible(False)  # Hides the Y-axis label
        self.canvas.draw()
        
    def set_axis(self):
        self.ax.xaxis.label.set_visible(True)  # Hides the X-axis label
        self.ax.yaxis.label.set_visible(True)  # Hides the Y-axis label
        self.canvas.draw()
        
         
    # def export(self):
    #     self._create_plot()
    #     plt.savefig(self.output_folder + f"/slice_{self.variable_name}.png")
    #     plt.close()

    # def show(self):
    #     self._create_plot()
    #     plt.show()            