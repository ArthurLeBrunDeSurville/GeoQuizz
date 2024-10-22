import tkinter as tk
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

class MapApp:
    def __init__(self, master):
        self.master = master
        master.title("Map Application")

        # Create a canvas widget
        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack()

        # Create a basemap object
        #self.map = Basemap(llcrnrlon=-180, llcrnrlat=-60, urcrnrlon=180, urcrnrlat=85, resolution='c', projection='merc')

        self.map = Basemap(llcrnrlon=-25, llcrnrlat=30, urcrnrlon=45, urcrnrlat=70, resolution='c', projection='merc')
        
        # Draw map features
        self.map.drawcoastlines()
        self.map.drawmapboundary(fill_color='aqua')
        self.map.fillcontinents(color='#ddaa66', lake_color='aqua')

        # Bind click event to canvas
        self.canvas.bind("<Button-1>", self.on_click)

        xmap, ymap = self.map(2.3333, 48.866666) # Conversion Lat,Long vers Coordonée Plot
        print(xmap, ymap)
        self.map.plot(xmap, ymap, 'ro', markersize=5)

    def on_click(self, event):
        x, y = event.x, event.y
        lon, lat = self.map(x, y, inverse=True)
        # Apply proportional factor for longitude
        lon = (lon / self.map.aspect) if self.map.aspect < 1 else lon
        print(f"Longitude: {lon}, Latitude: {lat}")

    def show_map(self):

        plt.tight_layout()
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        fig = plt.gcf()
        fig.patch.set_facecolor('#557171')
        plt.show()


root = tk.Tk()
app = MapApp(root)
app.show_map()
root.mainloop()