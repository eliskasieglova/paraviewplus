import geopandas as gpd
import pandas as pd
from shapely import LineString, Polygon
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.family': 'DejaVu Sans'})

from graphmaker import SimulationResults, TimeSeriesDemonstration

def main():

    surfpoints = gpd.read_file("paraviewplus/shp/surface_point_SHP.shp")
    airpoints = gpd.read_file("paraviewplus/shp/air_point_SHP.shp")
    surfmesh = gpd.read_file("paraviewplus/shp/surface_triangle_SHP.shp")
    surfdata = pd.read_csv("paraviewplus/shp/surface_data_2021_07_15.csv")
    airdata = pd.read_csv("paraviewplus/shp/air_data_2021_07_15.csv")

    surfdata2 = surfdata.copy()
    surfdata2["Tair"] = [x + 2 for x in surfdata["Tair"].values]
    surfdata2["UTCI"] = [x + 2 for x in surfdata["UTCI"].values]

    aoi1 = Polygon(((25496100, 6672050), (25496115, 6672000), (25496215, 6672070), (25496190, 6672100), (25496100, 6672050)))
    aoi2 = Polygon(((25496200, 6672050), (25496215, 6672000), (25496315, 6672070), (25496290, 6672100), (25496200, 6672050)))
    aoi3 = Polygon(((25496100, 6671900), (25496170, 6671800), (25496200, 6671820), (25496160, 6671900), (25496100, 6671900)))
    aoi4 = Polygon(((25496200, 6671950), (25496220, 6671850), (25496300, 6671820), (25496260, 6671950), (25496200, 6671950)))

    aois = [aoi1, aoi2, aoi3, aoi4]


    sr = SimulationResults(surfpoints, surfdata)
    sr.set_areas_of_interest(aois)
    sr.set_variable_names("all")
    sr.set_output_folder("paraviewplus/figs")
    sr.set_show(True)

    #sr.run()  # TODO manual adding of variable and plot layout information - later

    tsd = TimeSeriesDemonstration(
        surfpoints=surfpoints,
        airpoints=airpoints,
        surfmesh=surfmesh,
        surfdata=surfdata,
        airdata=airdata,
    )

    #tsd.run()




    


    #graphmaker = DataPoints(gdf, df)

    #graphmaker.plot_single_point("Tair", outdir="paraviewplus/figs", show=True, cell_ID=1)

    #graphmaker.plot_variable_comparison(df2, "UTCI", areas_of_interest)

    #graphmaker.plot_single_simulation("UTCI", areas_of_interest, outdir="paraviewplus/figs", show=True)
    #graphmaker.plot_areas_of_interest(aois=areas_of_interest, outdir="paraviewplus/figs", show=True)

    surfacepoints = SurfacePoints(gdf=gdf, df=df, aois=[aoi1, aoi2], output_folder="paraviewplus/figs")
    #surfacepoints.compare_simulations(df2=df2, df3=df2, variable_names=["Tair", "UTCI"])
 
    walls = gpd.read_file('paraviewplus/cache/walls.shp')
    rooftops=gpd.read_file('paraviewplus/cache/rooftops.shp')
    airpoints=gpd.read_file("paraviewplus/shp/air_point_shp.shp")
    airdata=pd.read_csv("paraviewplus/shp/air_data_2021_07_15.csv")
    #surfacepoints.timeSeriesSimulation(16, walls, rooftops, airpoints, airdata)

    #surfacepoints.plot_simulation_timeseries(walls, rooftops, airpoints, airdata)
    surfacepoints.plot_UTCI_category(walls, rooftops, 'moderate')

    #surfacepoints.plotSimulationResults("UTCI", [aoi1, aoi2, aoi3, aoi4], "paraviewplus/figs", show=True)

    #airpoints = AirPoints(airpoints, airdata, "paraviewplus/figs")
    #airpoints.plot_windrose()

    #linegeometry = LineString([(25496120, 6672150), (25496315, 6671800)])
    #time = 1
    #surfacepoints.plot_slice_on_map(linegeometry)
    #airpoints.plot_slice_on_map(linegeometry)
    #surfacepoints.plot_points_3d(colorby="Tair")
    #surfacepoints.plot_slice_3d(linegeometry)

    #airpoints.plot_streamplot(1, gpd.read_file("paraviewplus/shp/surface_triangle_SHP.shp"), dims=2)
    
    #airpoints.plot_flow(1, gpd.read_file("paraviewplus/shp/surface_triangle_SHP.shp"))
    #airpoints._remove_buildings(gpd.read_file("paraviewplus/shp/surface_point_SHP.shp"))

    #surfacepoints.plot_slice_points(linegeometry, "Tair", time=1)
    #surfacepoints.plot_slice_lines(linegeometry, "UTCI", time=1)
    #airpoints.plot_slice_fishnet(linegeometry, "WindSpeed", resolution=5)

    #airpoints.plot_matrix(linegeometry, "WindSpeed", resolution=5)

if __name__ == "__main__":
    main()
