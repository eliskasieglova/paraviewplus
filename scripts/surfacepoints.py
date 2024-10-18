import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'DejaVu Sans'})

from basepoints import BasePoints

class SurfacePoints:
    def __init__(self, gdf, df):
        super().__init__(gdf, df)

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

