from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

coordinates = [
    (41.3888, 2.1590),
    (39.4739, -0.3797),
    (40.4165, -3.7026),
    (43.2627, -2.9253),
    (39.0437, -77.4875),
    (33.7490, -84.3880),
    (29.7633, -95.3633),
    (31.7587, -106.4869),
    (33.4484, -112.0740),
    (34.0522, -118.2437),
    (34.0522, -118.2437)
    ]

m = Basemap(projection='mill', resolution='l')

m.drawcoastlines()
m.drawcountries()
m.drawmapboundary(fill_color='aqua')
m.fillcontinents(color='lightgreen', lake_color='aqua')

lats, lons = zip(*coordinates)
x, y = m(lons, lats)

m.scatter(x[0], y[0], marker='o', color='green', label='Start', zorder=5)
m.scatter(x[1:-2], y[1:-2], marker='o', color='red', label='Nodes', zorder=5)
m.scatter(x[-1], y[-1], marker='o', color='blue', label='End', zorder=5)

for i in range(len(coordinates) - 1):
    x1, y1 = m(coordinates[i][1], coordinates[i][0]) 
    x2, y2 = m(coordinates[i+1][1], coordinates[i+1][0])
    plt.plot([x1, x2], [y1, y2], color='black', linewidth=2, zorder=3)

plt.legend()
plt.show()
plt.savefig('world_map.png', bbox_inches='tight')
