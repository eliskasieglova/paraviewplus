import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.axes as axes
import matplotlib.patches as mpatches
from PIL import Image

class SizedScrollableFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, *args, **kwargs):
        super().__init__(master, fg_color='transparent', *args, **kwargs)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.place(x=0, y=0, anchor="nw", relwidth=1, relheight=1)



# class for Fancy looking graphs and rounded edges graph
class StaticColorAxisBBox(mpatches.FancyBboxPatch):
    def set_edgecolor(self, color):
        if hasattr(self, "_original_edgecolor"):
            return
        self._original_edgecolor = color
        self._set_edgecolor(color)

    def set_linewidth(self, w):
        super().set_linewidth(1.5)

class FancyAxes(axes.Axes):
    name = "fancy_box_axes"
    _edgecolor: str

    def __init__(self, *args, **kwargs):
        self._edgecolor = kwargs.pop("edgecolor", None)
        super().__init__(*args, **kwargs)

    def _gen_axes_patch(self):
        return StaticColorAxisBBox(
            (0, 0),
            1.0,
            1.0,
            boxstyle="round, rounding_size=0.02, pad=0",
            edgecolor=self._edgecolor,
            linewidth=5,
        )

class Slice(ctk.CTkFrame):
    def __init__(self, master,master_class, number):
        super().__init__(master, fg_color='grey80')   
        self.pack(side="top", fill="x", padx=4, pady=2)
        
        self.frame_key = number
        self.parent = master_class
                
        slices_result_label = ctk.CTkLabel(self, text=f'Slice {self.frame_key}')
        slices_result_label.pack(side='left', padx=8, pady=2)
        
        self.slices_result_entry = ctk.CTkEntry(self, width=280, border_width=0)
        self.slices_result_entry.pack(side='left', fill='x', padx=8, pady=2)
        
        slices_result_delete_button = ctk.CTkButton(self, text='delete', width=80, command=self.on_delete)
        slices_result_delete_button.pack(side='right', padx=4, pady=2)

    def insert_data(self,data):
        self.slices_result_entry.insert(0,data)
        
    def on_delete(self):
        print(len(self.parent.slices_frames))
        print(self.frame_key)
        if self.frame_key in self.parent.slices_frames:
            del self.parent.slices_frames[self.frame_key]
            
        print(self.slices_result_entry.get())
        test = self.parent.all_polygons[-1]
        print(str(test["points"]))    
        for polygon in self.parent.all_polygons:
            if f"[{self.slices_result_entry.get()}]" == str(polygon["points"]):
                print("works")
                for line_plot in polygon["lines"]:
                    line_plot.remove()

                # Remove the dots associated with this polygon
                for dot in polygon["dots"]:
                    dot.remove()
                self.parent.all_polygons.remove(polygon)
        self.parent.canvas.draw() 
        self.destroy()

class Slicer(ctk.CTkFrame):
    def __init__(self, master, shp_path):
        super().__init__(master, fg_color='transparent')

        gdf = shp_path
        
        self.parent = master
        # Set the protocol to handle window close event
        #self.protocol("WM_DELETE_WINDOW", self.on_closing) 

        # Create new height column
        gdf['height'] = gdf.geometry.apply(lambda geom: np.mean([coord[2] for coord in geom.exterior.coords if len(coord) == 3]))
        

        self.fig = plt.figure(figsize=(5, 5), facecolor='#D9D9D9')
        self.ax = self.fig.add_subplot(111, axes_class=FancyAxes, facecolor='#E5E5E5', edgecolor='#F2F2F2')
        self.ax.set_box_aspect(1)

        for spine in self.ax.spines.values():
            spine.set_visible(False)

        # Plot the surface mesh
        gdf.plot(column="height", cmap="Spectral_r", legend=True, markersize=1, ax=self.ax)

        # Style plot
        self.ax.set_aspect('equal', 'box')
        self.ax.set_xlabel("longitude")
        self.ax.set_ylabel("latitude")
        
        self.slices_counts = 0
        self.slices_frames = {}
        self.slices_list = [] 
        
        self.drawn_lines = []

        self.redo_stack = []  # Stack for redo functionality

        self.zoom_pressed = False
        self.pan_pressed = False
        self.draw_pressed = False
        
        self.is_drawing_enabled = False  # Initially disable drawing
        
        self.first_line = True
        
        # Connect the click event once
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
##################################################################################################################################
        
        main_frame = self
        main_frame.pack(side='top', fill='both', expand=True)
        
        extended_plot_frame = ctk.CTkFrame(main_frame)
        extended_plot_frame.pack(side='top', fill='both', expand= True,pady=(4,0), padx=4)
        
        draw_tool_frame = ctk.CTkFrame(extended_plot_frame, fg_color='#E5E5E5')
        draw_tool_frame.pack(side='top', fill='x', pady=(2,0), padx=4)
        
        # Create CustomTkinter buttons for Draw, Undo, and Redo
        pencil_image = ctk.CTkImage(Image.open('icons/pencil_icon.png'), size=(20, 20))
        self.draw_button = ctk.CTkButton(draw_tool_frame,text='', image=pencil_image, corner_radius=6, fg_color='#E5E5E5', width=20, command=self.start_drawing)
        self.draw_button.pack(side='left', pady=2, padx=(2,0))

        erase_image = ctk.CTkImage(Image.open('icons/eraser_icon.png'), size=(20, 20))
        self.delete_button = ctk.CTkButton(draw_tool_frame,text='', image=erase_image, corner_radius=6, fg_color='#E5E5E5', width=20, command=self.start_deleting)
        self.delete_button.pack(side='left', pady=2, )        
                
        spacer_label = ctk.CTkLabel(draw_tool_frame, text= "|")
        spacer_label.pack(side='left', padx=(0,2))
        
        undo_image = ctk.CTkImage(Image.open('icons/undo_icon.png'), size=(20, 20))
        self.undo_button = ctk.CTkButton(draw_tool_frame,text='', image=undo_image, corner_radius=6, fg_color='#E5E5E5', width=20, state='disabled', command=self.undo_line)
        self.undo_button.pack(side='left', pady=2)

        redo_image = ctk.CTkImage(Image.open('icons/redo_icon.png'), size=(20, 20))
        self.redo_button = ctk.CTkButton(draw_tool_frame,text='', image=redo_image, corner_radius=6, fg_color='#E5E5E5', width=20, state='disabled', command=self.redo_line)
        self.redo_button.pack(side='left', pady=2)
        
        title_label = ctk.CTkLabel(draw_tool_frame, text='Slices', font=('Futura', 14,'bold'))
        title_label.pack(side='left', pady=2, fill='x', expand=True)
        
        
        plot_frame = ctk.CTkFrame(extended_plot_frame, fg_color='transparent')
        plot_frame.pack(side='top', fill='both',pady=(0,2), padx=4, expand= True)
        
        # Embed plot in CustomTkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both',pady=8,padx=8, expand= True)

        # Add toolbar
        ghost_frame = ctk.CTkFrame(plot_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, ghost_frame)
        self.toolbar.update()
        
        # Function to bind zoom button
        def zoom():
            if not self.zoom_pressed:
                self.zoom_graph_button.configure(fg_color='#96C11F') 
                self.zoom_pressed = True
                if self.pan_pressed:
                    self.pan_graph_button.configure(fg_color='#E5E5E5')
                    self.pan_pressed = False                    
            else:
                self.zoom_graph_button.configure(fg_color='#E5E5E5')
                self.zoom_pressed = False 
            self.toolbar.zoom()  # Equivalent to clicking the zoom button on the toolbar

        # Function to bind pan button
        def pan():
            if not self.pan_pressed:
                self.pan_graph_button.configure(fg_color='#96C11F') 
                self.pan_pressed = True
                if self.zoom_pressed:
                    self.zoom_graph_button.configure(fg_color='#E5E5E5')
                    self.zoom_pressed = False                     
            else:
                self.pan_graph_button.configure(fg_color='#E5E5E5')
                self.pan_pressed = False
            self.toolbar.pan()  # Equivalent to clicking the pan button on the toolbar

        # Function to reset the view
        def reset_view():
            self.toolbar.home()  # Resets the view to the default


        reset_image = ctk.CTkImage(Image.open('icons/reset_icon.png'), size=(20, 20))
        self.reset_graph_button = ctk.CTkButton(draw_tool_frame, text='',image=reset_image, corner_radius=6, fg_color='#E5E5E5', width=20, command=reset_view)
        self.reset_graph_button.pack(side='right', pady=4)
        
        zoom_image = ctk.CTkImage(Image.open('icons/zoom_icon.png'), size=(20, 20))
        self.zoom_graph_button = ctk.CTkButton(draw_tool_frame, text="", image=zoom_image, corner_radius=6, fg_color='#E5E5E5', width=20, command=zoom)
        self.zoom_graph_button.pack(side='right', padx=(0,4), pady=4)
        
        pan_image = ctk.CTkImage(Image.open('icons/pan_icon.png'), size=(20, 20))
        self.pan_graph_button = ctk.CTkButton(draw_tool_frame, text='',image=pan_image, width=20, corner_radius=6, fg_color='#E5E5E5', command=pan)
        self.pan_graph_button.pack(side='right', padx=(0,4), pady=4)
        
        self.result_frame = SizedScrollableFrame(main_frame, height=86)
        self.result_frame.pack(side="top", fill="x", padx=4, pady=4)

        slices_title_frame = ctk.CTkFrame(self.result_frame.scrollable_frame, fg_color='grey80')
        slices_title_frame.pack(side="top", fill="x", padx=4, pady=2)
                
        slices_title_label = ctk.CTkLabel(slices_title_frame, text='Slices:')
        slices_title_label.pack(side='left', padx=8, pady=2)
        
        slices_title_add_label = ctk.CTkButton(slices_title_frame, text='Add', command=self.create_slices_gui, width=80)
        slices_title_add_label.pack(side='right', padx=4, pady=2)
        
        
        
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(side='top', fill='x', pady=4, padx=4)
        
        self.next_button = ctk.CTkButton(bottom_frame, text= 'Next', width=80)
        self.next_button.pack(side='right', pady=4, padx=4)
        
    def create_slices_gui(self): 
        self.slices_counts +=1
        
        slices_frame = Slice(self.result_frame.scrollable_frame,self, self.slices_counts)
            
        # Check if `drawn_lines` exists, contains "points", and has valid data
        if self.drawn_lines:
            last = self.drawn_lines[-1]["points"]  # Get the latest tuple of points
            last2 = ', '.join(map(str,last)) 
            print('test', last2)
            slices_frame.insert_data(last2)  # Insert data into the slice frame
            #self.parent.slices_list.append(last)
            self.slices_list.append(last2)     
        
        self.slices_frames[self.slices_counts] = slices_frame

    def get_slices_list(self):
        return self.slices_list

    
    # Function to start drawing mode with the button
    def start_drawing(self):
        if not self.draw_pressed:
            self.draw_button.configure(fg_color='#96C11F')
            self.is_drawing_enabled = True
            self.draw_pressed = True
            print("Drawing mode enabled.")
                
        else:
            self.draw_button.configure(fg_color='#E5E5E5')
            self.is_drawing_enabled = False
            self.draw_pressed = False
            print("Drawing mode disabled")
        
        
    def start_deleting(self):
        # Store the closed polygon in all_polygons
        """Remove all drawn lines."""
        if hasattr(self, 'drawn_lines'):
            for line_entry in self.drawn_lines:
                line_entry["line"].remove()  # Remove each line from the plot
            self.drawn_lines = []  # Clear the list of lines

            # Update the canvas
            self.fig.canvas.draw()
            print("All lines cleared.")


    # Function to handle mouse clicks
    def on_click(self, event):
        if self.is_drawing_enabled:
            self.on_click_draw(event)

            
    def on_click_draw(self, event):
        """Handle click events to draw a line for every two points."""
        if event.inaxes == self.ax:  # Ensure the click is inside the plot area
            x, y = event.xdata, event.ydata
            new_point = (x, y)

            # Initialize a list to store current line's points
            if not hasattr(self, 'current_line_points'):
                self.current_line_points = []

            # Add the new point to the current line's points
            self.current_line_points.append(new_point)

            # Check if two points have been clicked
            if len(self.current_line_points) == 2:
                # Draw the line
                x_vals = [p[0] for p in self.current_line_points]
                y_vals = [p[1] for p in self.current_line_points]
                
                line, = self.ax.plot(x_vals, y_vals, color="black", linewidth=1.5, alpha=0.8)
                
                # Initialize a list to store all drawn lines
                if not hasattr(self, 'drawn_lines'):
                    self.drawn_lines = []

                # Append the new line to the list of drawn lines
                self.drawn_lines.append({
                    "line": line,  # The Matplotlib line object
                    "points": self.current_line_points[:]  # A copy of the points
                })
                self.create_slices_gui()

                self.check_undo_redo_viability()
                
                print(f"Line drawn between {self.current_line_points[0]} and {self.current_line_points[1]}.")
                
                # Reset the current line's points
                self.current_line_points = []

            # Update the canvas
            self.fig.canvas.draw()




            

    # Helper function for distance calculation
    def _distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    
    
    def check_undo_redo_viability(self):
        current_undo_state = self.undo_button.cget("state")
        current_redo_state = self.redo_button.cget("state")
        
        # Enable/disable the undo button based on `drawn_lines`
        if self.drawn_lines and current_undo_state == "disabled":
            self.undo_button.configure(state="normal")
        elif not self.drawn_lines and current_undo_state == "normal":
            self.undo_button.configure(state="disabled")

        # Enable/disable the redo button based on `redo_stack`
        if self.redo_stack and current_redo_state == "disabled":
            self.redo_button.configure(state="normal")
        elif not self.redo_stack and current_redo_state == "normal":
            self.redo_button.configure(state='disabled')
       
       
    def undo_line(self):
        """Remove the last drawn line."""
        if hasattr(self, 'drawn_lines') and self.drawn_lines:
            last_line = self.drawn_lines.pop()  # Remove the last line entry
            self.redo_stack.append(last_line)
            last_line["line"].remove()  # Remove the line from the plot
            
            # Update the canvas
            self.fig.canvas.draw()
            print("Last line undone.")
            self.check_undo_redo_viability()
        else:
            print("No lines to undo.")
        

    def redo_line(self):
        self.check_undo_redo_viability()
        line_segment = self.redo_stack.pop()
        if isinstance(line_segment, dict) and "points" in line_segment:
            points = line_segment["points"]
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            line, = self.ax.plot(x_vals, y_vals, color="black", linewidth=1.5, alpha=0.8)
            if not hasattr(self, 'drawn_lines'):
                self.drawn_lines = []
            self.drawn_lines.append({"line": line, "points": points})
            self.fig.canvas.draw()
            print(f"Redo line between {points[0]} and {points[1]}.")
        else:
            print("Invalid line segment in redo stack.")    
                    


# class App(ctk.CTk):
#     def __init__(self):
#         super().__init__(fg_color = "gray95")
        
#         self.slicer = Slicer(self,"data\surface_triangle_SHP.shp")
        
#         self.title('Solene Pre-Proccesing')
#         self.geometry('600x600')
#         self.minsize(600,600)
        
#     def on_closing(self):
#         # Close all matplotlib figures
#         plt.close('all')
#         # Quit and destroy the Tkinter application
#         self.quit()
#         self.destroy()
 
 
#     def mainloop(self):
#         super().mainloop()


# if __name__ == "__main__":
#     app = App() 
#     app.mainloop()  
#     # Instantiate