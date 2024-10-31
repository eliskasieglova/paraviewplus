import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

from inputs import SurfaceMesh
from inputs import DataPoints
from inputs import AirPoints
from inputs import SurfacePoints


class TimeSeriesDemonstration(SurfaceMesh, DataPoints):
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

    def __init__(self, surfpoints, surfdata, airpoints, airdata, surfmesh) -> None:

        self.surfpoints = surfpoints
        self.surfdata = surfdata
        self.airpoints = airpoints
        self.airdata = airdata
        self.surfmesh = surfmesh

        # creates walls and rooftops dataframes for plotting
        self.walls, self.rooftops = self._walls_rooftops()

    
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

        self._layout_time_series_sim(fig, ax, contour, levels, ticks, variable_name)

        return

    def run(self, var1=("Tair", "coolwarm"), var2=("RelatHumid", "Purples"), var3=("WindSpeed", "Blues"), var4=("UTCI", ListedColormap(['green', 'orange', 'orangered', 'red', 'darkred']))):
        """
        Runs the visualization for each timestep in the surface data, plotting
        multiple variables in a 2x2 subplot layout.

        Parameters
        ----------
        var1, var2, var3, var4 : tuple
            Each variable tuple contains the variable name and colormap to use for plotting.
        """
        # get the timesteps in the data
        for time in self.get_timesteps(df=self.surfdata):

            # create figure layout
            fig, axs = plt.subplots(2, 2, figsize=(9, 9))

            # plot selected variables
            for i, v in enumerate([var1, var2, var3, var4]):
                name = v[0]
                cmap = v[1]
                ax = [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]][i]
                # plot
                plt.subplot(2, 2, i+1) 
                self._plot_time_series_sim(fig, ax, name, cmap, time)

            plt.suptitle(f"Time: {time}", fontsize = 40)

            plt.show()

        return

class SimulationResults(SurfacePoints):
    """ Plots the simulation results for the chosen areas of interest in one plot for each selected variable. """

    def __init__(self, gdf, df) -> None:
        super().__init__(gdf, df)

        self.gdf = gdf
        self.df = df

        self.output_folder = None
        self.areas_of_interest = None
        self.variable_names = None

        self.export = False
        self.show = False

    def set_variable_names(self, variable_names: list | str):
        """
        Set the variables to be plotted. If 'all', all variables in df will be used.

        Parameters
        ----------
        variable_names : list or str
            List of variable names to plot, or 'all' to plot all available variables.
        """
        # if all vars selected, get all vars from csv file
        if variable_names == "all":
            variable_names = [x for x in self.df.columns[1:-1]]

        if not variable_names:
            raise ValueError("Come on, you have to select at least one variable.")
        
        for variable_name in variable_names:
            try: 
                self.get_title(variable_name)
            except: 
                print(f"{variable_name} is not supported and was removed from the variable list. If you want to add it to the supported variables list, fill in the info.")  # TODO
                variable_names.remove(variable_name)

        # set the variable names
        self.variable_names = variable_names

    def set_areas_of_interest(self, aois):
        """
        Set the areas of interest (AOIs) to be plotted.

        Parameters
        ----------
        aois : list
            List of areas of interest to plot.
        """
        if not aois:
            raise ValueError("Oh come on, areas of interest cannot be empty.")
        
        self.areas_of_interest = aois

    def set_output_folder(self, output_folder):
        """ Save the output folder as class variable. """
        self.output_folder = output_folder

    def set_export(self, selection : bool):
        self.export = selection

    def set_show(self, selection : bool):
        self.show = selection
    
    def plot(self, variable_name, colors=['blue', 'red', 'yellow', 'green']):
        """
        Generates and displays a plot for a single simulation variable over time for all AOIs.

        Parameters:
        ----------
        variable_names : list of strings
            The variables to plot (e.g., []"Tair", "Tsurf", "UTCI"]). If no variable is chosen it defaults to all the variables
        colors : list of str, optional
            A list of colors for the areas of interest (AOIs). Defaults to ['blue', 'red', 'yellow', 'green'].
        """

        # initiate figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # plot values
        self._build_plot(self.df, self.areas_of_interest, variable_name, colors=colors)

        # apply layouts
        self._apply_plot_layout(ax, variable_name)
        self._plot_legend(ax)
        self._plot_note_text(variable_name)
        plt.title(self.get_title(variable_name), fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)

    def run(self):
        """ Run the graphmaking. Export or show based on user selection. """
        for variable_name in self.variable_names:
            self.plot(variable_name)

            if self.export:
                plt.savefig(f'{self.output_folder}/' + f'{variable_name}.png')   

            if self.show:
                plt.show()



class SimulationComparison(SurfacePoints):

    def __init__(self, gdf, df) -> None:
        super().__init__(gdf, df)

        self.gdf = gdf
        self.df = df

        self.output_folder = None
        self.areas_of_interest = None
        self.variable_names = None

        self.export = False
        self.show = False




if __name__ == "__main__":

    pass




        
        
        






