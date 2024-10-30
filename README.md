## Examples

### Plot surface

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






