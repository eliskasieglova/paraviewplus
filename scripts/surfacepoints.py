import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
plt.rcParams.update({'font.family': 'DejaVu Sans'})

from datapoints import DataPoints

class SurfacePoints(DataPoints):
    def __init__(self, gdf, df, output_folder, aois=None):
        super().__init__(gdf, df, output_folder)

        self.aois = aois

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

    def plot_UTCI(self,  walls=gpd.read_file('paraviewplus/cache/walls.shp'), rooftops=gpd.read_file('paraviewplus/cache/rooftops.shp'), cat='moderate', time=1):

        utci = {
            'extreme': {
                'bounds': (46, 50),
                'color': 'darkred'
            },
            'very_strong': {
                'bounds': (38, 46),
                'color': 'red'
            },
            'strong': {
                'bounds': (32, 38),
                'color': 'orangered'
            },
            'moderate': {
                'bounds': (26, 32),
                'color': 'orange'
            },
            'no': {
                'bounds': (9, 26),
                'color': 'lightgreen'
            }
        }

        # plot the surface (walls)
        ax = walls.plot(edgecolor='black', linewidth=0.5)
        rooftops.plot(ax=ax, edgecolor='black', linewidth=0.5, color='white')

        # extract area with UTCI according to selected temperature
        for cat in utci:
            bounds = utci[cat]['bounds']
            color = utci[cat]['color']
            temps = self.df[["cell_ID", "UTCI", "Time"]].dropna()
            temps = temps.where(temps["Time"] == time).dropna()
            temps = temps.where((temps["UTCI"] > bounds[0]) & (temps["UTCI"] < bounds[1])).dropna()  # select the UTCI category

            # merge csv with gpd
            subset = gpd.GeoDataFrame(pd.merge(temps, self.gdf[["cell_ID", "geometry"]]))

            ax.scatter(subset.geometry.x, subset.geometry.y, c=color, s=1)
        plt.title(f'UTCI (hour {time})')
        plt.show()

        return

    def plot_UTCI_cat(self, walls=gpd.read_file('paraviewplus/cache/walls.shp'), rooftops=gpd.read_file('paraviewplus/cache/rooftops.shp'), cat='moderate', time=1):
        
        utci = {
            'extreme': {
                'bounds': (46, 50),
                'color': 'darkred'
            },
            'very_strong': {
                'bounds': (38, 46),
                'color': 'red'
            },
            'strong': {
                'bounds': (32, 38),
                'color': 'orangered'
            },
            'moderate': {
                'bounds': (26, 32),
                'color': 'orange'
            },
            'no': {
                'bounds': (9, 26),
                'color': 'lightgreen'
            }
        }

        # plot the surface (walls)
        ax = walls.plot(edgecolor='black', linewidth=0.5)
        rooftops.plot(ax=ax, edgecolor='black', linewidth=0.5, c='white')

        # extract area with UTCI according to selected temperature
        temps = self.df[["cell_ID", "UTCI", "Time"]].dropna()
        temps = temps.where(temps["Time"] == time).dropna()
        temps = temps.where((temps["UTCI"] > utci[cat]['bounds'][0]) & (temps["UTCI"] < utci[cat]['bounds'][1])).dropna()  # select the UTCI category

        # merge csv with gpd
        subset = gpd.GeoDataFrame(pd.merge(temps, self.gdf[["cell_ID", "geometry"]]))

        ax.scatter(subset.geometry.x, subset.geometry.y, c=utci[cat]['color'], s=1)
        plt.title(f'UTCI (hour {time})')
        plt.show()

        return
    
    def compare_simulations(self, df2, df3=None, df4=None, variable_names=[]):

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

