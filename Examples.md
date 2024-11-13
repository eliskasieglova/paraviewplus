# Examples

### Plot Surface Points

```
import matplotlib.pyplot as plt
import geopandas as gpd

# load shapefile
gdf = gpd.read_file("surface_point_SHP.shp")  # path to shapefile surface points

# create scatterplot
sc = plt.scatter(gdf.geometry.x, gdf.geometry.y, c=gdf.geometry.z, cmap="Spectral_r", s=1)

# add colorbar
cbar = plt.colorbar(sc)
cbar.set_label('Height (m)')

# style plot
plt.axis('equal')
plt.title("Scatterplot of surface points colored by height")
plt.xlabel("longitude")
plt.ylabel("latitude")

plt.show()
```

![image](https://github.com/user-attachments/assets/399e3c90-6344-46a8-afb2-8b4652ede2dd)

### Plot Surface Mesh

```
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np

# load shapefile
gdf = gpd.read_file("surface_triangle_SHP.shp")  # path to shapefile surface points

# create new height column
gdf['height'] = gdf.geometry.apply(
    lambda geom: np.mean([coord[2] for coord in geom.exterior.coords if len(coord) == 3])
)

# plot the surfacemesh and color it by height
gdf.plot(column='height', legend=True, legend_kwds={"label": "Height (m)"})

# style the plot
plt.axis('equal')
plt.title("Scatterplot of surface mesh colored by height")
plt.xlabel("longitude")
plt.ylabel("latitude")

plt.show()
```
![image](https://github.com/user-attachments/assets/e7557da4-518c-4c16-9ccf-a20da1ca956c)

### Plot Areas of Interest (above surface points)
```
import matplotlib.pyplot as plt
import geopandas as gpd

# load shapefile
gdf = gpd.read_file("surface_point_SHP.shp")  # path to shapefile surface points

# create areas of interest
aoi1 = Polygon(((25496100, 6672050), (25496115, 6672000), (25496215, 6672070), (25496190, 6672100), (25496100, 6672050)))
aoi2 = Polygon(((25496200, 6672050), (25496215, 6672000), (25496315, 6672070), (25496290, 6672100), (25496200, 6672050)))
aoi3 = Polygon(((25496100, 6671900), (25496170, 6671800), (25496200, 6671820), (25496160, 6671900), (25496100, 6671900)))
aoi4 = Polygon(((25496200, 6671950), (25496220, 6671850), (25496300, 6671820), (25496260, 6671950), (25496200, 6671950)))

# assign height column to the geodataframe
gdf["height"] = gdf.geometry.z.values

# plot the points (and color by height)
ax = gdf.plot(column="height", cmap="Spectral_r", legend=True, markersize=1)

for aoi in [aoi1, aoi2, aoi3, aoi4]:
    aoi = gpd.GeoSeries(aoi)
    aoi.plot(ax=ax, color='lightgrey', alpha=0.8, edgecolor='black', linewidth=2)

# style plot
plt.axis('equal')
plt.title("Scatterplot of surface points colored by height (with areas of interest)")
plt.xlabel("longitude")
plt.ylabel("latitude")

plt.show()
```
![image](https://github.com/user-attachments/assets/4eb19026-87a3-41de-9e9c-82f6f20363df)

### Plot Areas of Interest (above surface mesh)
```
import matplotlib.pyplot as plt
import geopandas as gpd

# load shapefile
gdf = gpd.read_file("surface_triangle_SHP.shp")  # path to shapefile surface points

# create areas of interest
aoi1 = Polygon(((25496100, 6672050), (25496115, 6672000), (25496215, 6672070), (25496190, 6672100), (25496100, 6672050)))
aoi2 = Polygon(((25496200, 6672050), (25496215, 6672000), (25496315, 6672070), (25496290, 6672100), (25496200, 6672050)))
aoi3 = Polygon(((25496100, 6671900), (25496170, 6671800), (25496200, 6671820), (25496160, 6671900), (25496100, 6671900)))
aoi4 = Polygon(((25496200, 6671950), (25496220, 6671850), (25496300, 6671820), (25496260, 6671950), (25496200, 6671950)))

# create new height column
gdf['height'] = gdf.geometry.apply(
    lambda geom: np.mean([coord[2] for coord in geom.exterior.coords if len(coord) == 3])
)

# plot the surface mesh
ax = gdf.plot(column="height", cmap="Spectral_r", legend=True, markersize=1)

# plot the areas of interest
for aoi in [aoi1, aoi2, aoi3, aoi4]:
    aoi = gpd.GeoSeries(aoi)
    aoi.plot(ax=ax, color='lightgrey', alpha=0.8, edgecolor='black', linewidth=2)

# style plot
plt.axis('equal')
plt.title("Scatterplot of surface mesh colored by height (with areas of interest)")
plt.xlabel("longitude")
plt.ylabel("latitude")

plt.show()

```
![image](https://github.com/user-attachments/assets/874b0885-0316-42d2-99a5-698e7a1937ff)


### Plot LineString (Slice) on Map

```

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
```
