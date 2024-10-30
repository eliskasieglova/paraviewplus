## Examples

### Plot Surface Points

```
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

# Plot Surface Mesh

```
import geopandas as gpd
import numpy as np

# load shapefile
gdf = gpd.read_file("surface_point_SHP.shp")  # path to shapefile surface points

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



# Plot Areas of Interest





