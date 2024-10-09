import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from shapely import Polygon, LineString, Point
import string


class GraphMaker:
    """
    A class to handle loading and visualization of variables in simulation data.
    """

    # Titles, units, and layout settings
    titles = {
        "Tair": "Air Temperature",
        "WindSpeed": "Wind Speed",
        "Tsurf": "Surface Temperature",
        "RelatHumid": "Relative Humidity",
        "ET": "ET",
        "UTCI": "Felt Temperature - UTCI"
    }
    units = {
        "Tair": "Degrees (°C)",
        "Tsurf": "Degrees (°C)",
        "RelatHumid": "Percentage (%) x 0.01",
        "UTCI": "Degrees (°C)"
    }
    plt_layouts = {
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

    def __init__(self, gdf, simulations, areas_of_interest):
        """
        gdf : geopandas.GeoDataFrame
            GeoDataFrame containing spatial points.
        simulations : list of pandas.DataFrame
            List of DataFrames representing simulation results.
        areas_of_interest : list of shapely.geometry.Polygon
            List of polygons representing the areas of interest (AOIs).
        """

        self.gdf = gdf 
        self.simulations = simulations 
        self.areas_of_interest = areas_of_interest 

    def plot_areas_of_interest(self, outdir, show=True):

        self.gdf.plot()
        for aoi in self.areas_of_interest:
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
        ax.set_ylim(self.plt_layouts["ylims"][variable_name])
        ax.set_yticks(self.plt_layouts["yticks"][variable_name])
        ax.set_xlabel("Time")
        ax.set_ylabel(self.units[variable_name])

        # Apply gridlines
        linestyle = '-'
        linewidth = 0.7
        ax.yaxis.set_major_locator(ticker.MultipleLocator(self.plt_layouts["majorticklocator"][variable_name]))
        ax.grid(True, axis='y', which='major', color='gray', alpha=0.3, linestyle=linestyle, linewidth=linewidth)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if variable_name == "UTCI":
            self._apply_utci_background(ax)
        else:
            ax.set_facecolor((0.99, 0.99, 0.99, 0.1))
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(self.plt_layouts["minorticklocator"][variable_name]))
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
                    f"The above graph shows the average {self.plt_layouts['note'][variable_name]} "
                    "for Area A, Area B, Area C, and Area D from the simulation results.",
                    wrap=True, horizontalalignment='center', fontsize=10, fontstyle='italic')  

        
    def _add_img(self, img_path):
        """ Add image to plot upper right corner (map of areas of interest). """

        # TODO (???)

        return  

    def plot_single_point(self, cell_ID, variable_name, outdir, show=True):

        x, y = self.gdf[gdf['cell_ID'] == cell_ID].geometry.x.tolist()[0], self.gdf[gdf['cell_ID'] == cell_ID].geometry.y.tolist()[0]

        for df in self.simulations:
            # extract data
            values = [x for x in df[df['cell_ID'] == cell_ID][[variable_name]].values]
            timesteps = [x for x in df[df['cell_ID'] == cell_ID][["Time"]].values]
            
            fig, ax = plt.subplots(figsize=(10, 6))

            # plot values
            plt.plot(timesteps, values, c="red")

            # apply layout
            self._apply_plot_layout(ax, variable_name)
            self._plot_legend(ax)
            self._plot_note_text(variable_name)

            plt.title(f"{self.titles[variable_name]} at ({x}, {y})", fontsize=18, fontweight='bold', y=1.05)
            plt.subplots_adjust(top=0.83, bottom=0.2)
            
            plt.savefig(outdir + f'/{cell_ID}_{variable_name}.png')
            if show:
                plt.show()

    def _build_plot(self, simulation, variable_name, colors=['blue', 'red', 'yellow', 'green'], show=False):
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
        for idx, aoi in enumerate(self.areas_of_interest):
            # subset
            cell_IDs = gdf[gdf.within(aoi, align=True)]["cell_ID"].values.tolist()
            subset = df[df['cell_ID'].isin(cell_IDs)].dropna()

            cell_IDs = np.unique(subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
            timesteps = np.unique(subset.Time.values).tolist()  # get time steps
            avg_values = np.mean([subset[subset['cell_ID'] == id][variable_name].values for id in cell_IDs], axis=0)
            plt.plot(timesteps, avg_values, color=colors[idx], label=f"Area {list(string.ascii_uppercase)[idx]}")

        return

    def plot_single_simulation(self, variable_name, outdir, colors=['blue', 'red', 'yellow', 'green'], show=False):
        """
        Generates and displays a plot for a single simulation variable over time for all AOIs.

        Parameters:
        ----------
        variable : str
            The variable to plot (e.g., "Tair", "Tsurf", "UTCI"). Defaults to "Tair".
        colors : list of str, optional
            A list of colors for the areas of interest (AOIs). Defaults to ['blue', 'red', 'yellow', 'green'].
        """

        # loop through simulations
        for i, simulation in enumerate(self.simulations):

            fig, ax = plt.subplots(figsize=(12, 6))

            # plot values
            self._build_plot(simulation, variable_name, colors=colors)

            # apply layouts
            self._apply_plot_layout(ax, variable_name)
            self._plot_legend(ax)
            self._plot_note_text(variable_name)
            plt.title(self.titles[variable_name], fontsize=18, fontweight='bold', y=1.1)
            plt.subplots_adjust(top=0.85, bottom=0.2)

            plt.savefig(f'{outdir}/' + f'{variable_name}_sim{i+1}.png')

            if show:
                plt.show()

    def plot_simulation_comparison(self, variable_name, outdir, layout="vertical", colors=['blue', 'red', 'yellow', 'green'], show=False):
        """
        Generates and displays a plot with subplots for 2 simulations for a variable over time for all AOIs.

        Parameters:
        ----------
        variable_name : str
            The variable to plot (e.g., "Tair", "Tsurf", "UTCI"). Defaults to "Tair".
        layout : str "vertical" | "horizontal"
            "vertical" for subplots above each other, "horizontal" for subplots next to each other. Defaults to "vertical".
        colors : list of str, optional
            A list of colors for the areas of interest (AOIs). Defaults to ['blue', 'red', 'yellow', 'green'].
        """

        fig, axs = plt.subplots(2 if layout == "vertical" else 1, 1 if layout == "vertical" else 2, 
                                figsize=(10 if layout == "vertical" else 15, 8 if layout == "vertical" else 5))

        for i, ax in enumerate(axs):
            plt.sca(ax)
            self._build_plot(self.simulations[i], variable_name, colors)
            ax.set_title(f"Simulation {i+1}", fontsize=9)
            self._apply_plot_layout(ax, variable_name)

        # Collect handles and labels for the legend
        handles, labels = axs[0].get_legend_handles_labels()
 
        # Add the legend
        fig.legend(handles=handles, labels=labels, loc='center', bbox_to_anchor=(0.5, 0.88 if layout == "horizontal" else 0.92), ncol=4, fontsize=8, frameon=False)

        # other stuff around the plot
        plt.suptitle(self.titles[variable_name], fontsize=18, fontweight='bold', family='Verdana')  # title

        # Add note text in the bottom center
        plt.figtext(0.5, 0.05, 
                    r"$\mathbfit{" + "Note:" + "}$" +  f"The above graph shows the average {self.plt_layouts["note"][variable_name]} for Area A, Area B, Area C and \n Area D obtained from the simulation results for each hour of the simulation period.", 
                    wrap=True, horizontalalignment='center', fontsize=10, fontstyle='italic', family='Verdana')
        
        plt.subplots_adjust(top=0.78 if layout == "horizontal" else 0.86, bottom=0.26 if layout == "horizontal" else 0.15, hspace=0.28 if layout=="vertical" else 0)
        
        plt.savefig(f'{outdir}/' + f'{variable_name}_comparison.png')

        if show:
            plt.show()

        return
    
    def plot_variable_comparison(self, variable_name, aoi, colors=None, show=True):

        colors = ['red', 'blue']
        fig, ax = plt.subplots(figsize=(12, 6))

        # loop through simulations
        for i, simulation in enumerate(self.simulations):

            # plot values
            cell_IDs = gdf[gdf.within(aoi, align=True)]["cell_ID"].values.tolist()
            subset = simulation[simulation['cell_ID'].isin(cell_IDs)].dropna()

            cell_IDs = np.unique(subset['cell_ID'].values).tolist()  # reinitiate cell_IDs without nans
            timesteps = np.unique(subset.Time.values).tolist()  # get time steps
            avg_values = np.mean([subset[subset['cell_ID'] == id][variable_name].values for id in cell_IDs], axis=0)
            
            plt.plot(timesteps, avg_values, c=colors[i])

        # apply layouts
        self._apply_plot_layout(ax, variable_name)
        self._plot_legend(ax)
        if variable_name == "UTCI":
            self._apply_utci_background(ax)
        #self._plot_note_text(variable_name)
        plt.title(self.titles[variable_name], fontsize=18, fontweight='bold', y=1.1)
        plt.subplots_adjust(top=0.85, bottom=0.2)

        if show:
            plt.show()

            return
        

gdf = gpd.read_file('voxels/shp/surface_point_SHP.shp')
df = pd.read_csv('voxels/shp/surface_data_2021_07_15.csv')

#gdf = gpd.read_file('voxels/shp/air_point_SHP.shp')
#df = pd.read_csv('voxels/shp/air_data_2021_07_15.csv')

df2 = df.copy()
df2["Tair"] = [x + 2 for x in df["Tair"].values]
df2["UTCI"] = [x + 2 for x in df["UTCI"].values]

aoi1 = Polygon(((25496100, 6672050), (25496115, 6672000), (25496215, 6672070), (25496190, 6672100), (25496100, 6672050)))
aoi2 = Polygon(((25496200, 6672050), (25496215, 6672000), (25496315, 6672070), (25496290, 6672100), (25496200, 6672050)))
aoi3 = Polygon(((25496100, 6671900), (25496170, 6671800), (25496200, 6671820), (25496160, 6671900), (25496100, 6671900)))
aoi4 = Polygon(((25496200, 6671950), (25496220, 6671850), (25496300, 6671820), (25496260, 6671950), (25496200, 6671950)))

areas_of_interest = [aoi1, aoi2, aoi3, aoi4]
simulations = [df, df2]

graphmaker = GraphMaker(gdf, simulations, areas_of_interest)

graphmaker.plot_variable_comparison("UTCI", aoi1)

#graphmaker.plot_single_point(1, "Tair", outdir="voxels/figs")
#graphmaker.plot_single_simulation("UTCI", outdir="voxels/figs", show=True)
#graphmaker.plot_simulation_comparison("UTCI", outdir="voxels/figs", layout="horizontal", show=True)
#graphmaker.plot_areas_of_interest(outdir="voxels/figs", show=True)


surfacepoints = SurfacePoints(gpd.read_file('voxels/shp/surface_point_SHP.shp'), [pd.read_csv('voxels/shp/surface_data_2021_07_15.csv')])
airpoints = AirPoints(gpd.read_file('voxels/shp/air_point_SHP.shp'), [pd.read_csv('voxels/shp/surface_data_2021_07_15.csv')])


linegeometry = LineString([(25496120, 6672150), (25496315, 6671800)])
time = 1
#surfacepoints.plot_slice_on_map(linegeometry)
#airpoints.plot_slice_on_map(linegeometry)

#surfacepoints.plot_slice_points(linegeometry, "Tair", time=1)
#surfacepoints.plot_slice_lines(linegeometry, "UTCI", time=1)
#airpoints.plot_slice_fishnet(linegeometry, "Tair", resolution=10)




