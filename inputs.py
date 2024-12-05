import geopandas as gpd
import pandas as pd
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib import rcParams
rcParams['font.family'] = 'DejaVu Sans'


class VariableChars:

    def __init__(self) -> None:
        self.varchars = {
            "Tair": {
                "title": "Air Temperature",
                "units": "Degrees Celsius", 
                "note": "",
                "cmap": "coolwarm",  # cmap from matplotlib list
                "ylims": (9, 50),
                "yticks": (np.arange(10, 51, step=10)),
                "minorticklocator": 5,
                "majorticklocator": 10

            },
            "Tsurf": {
                "title": "Surface Temperature",
                "units": "Degrees Celsius",
                "note": "",
                "cmap": "coolwarm",
                "ylims": (9, 50),
                "yticks": (np.arange(10, 51, step=10)),
                "minorticklocator": 5,
                "majorticklocator": 10
            },
            "UTCI": {
                "title": "Felt Temperature",
                "units": "Degrees Celsius",
                "note": "",
                "cmap": ListedColormap(['green', 'orange', 'orangered', 'red', 'darkred']),
                "ylims": (9, 50),
                "yticks": (np.arange(10, 51, step=10)),
                "minorticklocator": 5,
                "majorticklocator": 10
            },
            "RelatHumid": {
                "title": "Relative Humidity",
                "units": "percent",
                "note": "",
                "cmap": "Purples",
                "ylims": (0, 1),
                "yticks": (np.arange(0, 1.1, step=0.1)),
                "minorticklocator": 0.05,
                "majorticklocator": 0.1
            },
            "WindSpeed": {
                "title": "Wind Speed",
                "units": "m/s",
                "note": "",
                "cmap": "Blues",
                "ylims": (0, 10),
                "yticks": (np.arange(0, 10, step=1)),
                "minorticklocator": None,
                "majorticklocator": None
            }
        }

    def get_title(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["title"]
    
    def get_units(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["units"]
    
    def get_note_text(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["note"]
    
    def get_ylims(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["ylims"]
    
    def get_yticks(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["yticks"]
    
    def get_cmap(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["cmap"]
    
    def get_minorticklocator(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["minorticklocator"]
    
    def get_majorticklocator(self, name):
        if not name in self.varchars.keys():
            return ""
        else:
            return self.varchars[name]["majorticklocator"]
        
    def add_variable(self, name):

        dict_keys = [k for k in self.varchars["Tair"].keys()]
        
        self.varchars[name] = {

        }

        for k in dict_keys:
            self.varchars[name][k] = ""
    
    def set_title(self, name, title):
        self.varchars[name]["title"] = title

    def set_units(self, name, units):
        self.varchars[name]["units"] = units

    def set_cmap(self, name, cmap):
        self.varchars[name]["cmap"] = cmap

    def set_ylimx(self, name, ylims):
        self.varchars[name]["ylims"] = ylims

    def set_yticks(self, name, yticks):
        self.varchars[name]["yticks"] = yticks

    def set_minorticklocator(self, name, minorticklocator):
        self.varchars[name]["minorticklocator"] = minorticklocator

    def set_majorticklocator(self, name, majorticklocator):
        self.varchars[name]["majorticklocator"] = majorticklocator


class DataPoints(VariableChars):
    def __init__(self, gdf, df):
        self.gdf = gdf
        self.df = df
        self.output_folder = "paraviewplus/figs"
    
    def get_timesteps(self):
        """ Return the time steps in the dataset """
        return [x for x in np.unique(self.df.Time)]
    
    def get_columns(self):
        """ Get the columns (variables) of chosen dataset"""
        return [x for x in self.df.columns]

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
    def __init__(self, gdf, df):
        super().__init__(gdf, df)

        self.gdf = gdf
        self.df = df

        self.output_folder = None

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

        timesteps = self.get_timesteps()
        
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
            x, y = self.surfpoints[self.surfpoints['cell_ID'] == cell_ID].geometry.x.tolist()[0], self.surfpoints[self.surfpoints['cell_ID'] == cell_ID].geometry.y.tolist()[0]
    
        # extract data
        values = [x for x in self.surfdata[self.surfdata['cell_ID'] == cell_ID][[variable_name]].values]
        timesteps = [x for x in self.surfdata[self.surfdata['cell_ID'] == cell_ID][["Time"]].values]
        
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

    def _build_plot(self, simulation, aois, variable_name, colors, show=False):
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


class AirPoints(DataPoints):
    def __init__(self, gdf, df):
        super().__init__(gdf, df)
        self.gdf = gdf
        self.df = df

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
        
class SurfaceMesh():
    def __init__(self, surfmesh : gpd.GeoDataFrame, surfdata : pd.DataFrame):
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
    

    


