import geopandas as gpd
import pandas as pd
from shapely import LineString, Polygon
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.family': 'DejaVu Sans'})

from graphmaker import SimulationResults, TimeSeriesDemonstration, UTCICategory, SimulationComparison, AOIsOnMap, Windrose, Slice
from inputs import VariableChars


def main():

    output_folder = "paraviewplus/figs"

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

    # PLOT AREAS OF INTEREST ABOVE MAP
    aoimap = AOIsOnMap(surfpoints, surfdata, surfmesh)

    # add aois
    aoimap.add_area_of_interest(aoi1)
    aoimap.add_area_of_interest(aoi2)
    aoimap.add_area_of_interest(aoi3)
    aoimap.add_area_of_interest(aoi4)

    aoimap.set_output_folder(output_folder)
    # run with point map underneath
    #aoimap.plot()

    # run with mesh underneath
    aoimap.set_plot_type("mesh")
    #aoimap.run()

    # Variable characteristics
    varchars = VariableChars()
    varchars.add_variable("ET")

    # SLICE
    slice = LineString([[25496100, 6672050], [25496115, 6672000]])
    sl = Slice(airpoints, airdata, slice)
    sl.add_variable("Tair")
    sl.set_type("matrix")
    #sl.run()


    # WINDROSE
    wr = Windrose(airpoints, airdata)

    wr.set_output_folder(output_folder)
    #wr.run()

    # SIMULATION RESULTS
    sr = SimulationResults(surfpoints, surfdata)
    sr.add_area_of_interest(aoi1)
    sr.add_area_of_interest(aoi2)
    sr.add_area_of_interest(aoi3)
    sr.add_variable("Tair")
    sr.add_variable("UTCI")
    sr.set_output_folder("paraviewplus/figs")
    sr.set_show(True)

    sr.run()  

    # TIME SERIES DEMONSTRATION
    tsd = TimeSeriesDemonstration(
        surfpoints=surfpoints,
        airpoints=airpoints,
        surfmesh=surfmesh,
        surfdata=surfdata,
        airdata=airdata,
    )

    tsd.add_variable("WindDirection") # TODO fix wind direction

    #tsd.plot()

    #tsd.set_output_folder(output_folder)
    #tsd.export()

    # UTCI
    utci = UTCICategory(surfpoints, surfdata, surfmesh)
    utci.add_category('moderate')

    #utci.run()

    # SIMULATION COMPARISON
    sc = SimulationComparison(surfpoints, surfdata)
    sc.add_aoi(aoi1)
    sc.add_aoi(aoi2)
    sc.add_variable("Tair")
    sc.add_variable("UTCI")
    sc.add_simulation(surfdata2)

    sc.show()


if __name__ == "__main__":
    main()