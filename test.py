import geopandas as gpd
import matplotlib.pyplot as plt

gdf = gpd.read_file('data/MUNICIPIOS_5000_ETRS89.shp')

gdf.plot()
plt.show()