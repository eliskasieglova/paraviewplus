# import matplotlib.pyplot as plt
# import numpy as np

# # Example data
# x = np.linspace(0, 10, 100)
# y = np.sin(x)

# # Create a plot
# fig, ax = plt.subplots()
# ax.plot(x, y, label='sin(x)')
# ax.set_title("Transparent Outside, White Inside")
# ax.set_xlabel("x-axis")
# ax.set_ylabel("y-axis")
# ax.legend()

# # Set the axes (plot) background to white
# fig.savefig("fname", facecolor=(1,1,1,0))

# # Save the figure with transparent background outside the plot area
# fig.savefig("transparent_outside_plot.png", transparent=True, dpi=300)

# # Show the plot
# plt.show()

from custom_widgets import CTkRangeSlider
import customtkinter

def show_value(value):
    print(value)
    
root = customtkinter.CTk()

range_slider = CTkRangeSlider(root, command=show_value)
range_slider.pack(padx=30, pady=30, fill="both")

root.mainloop()