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

class AoI(ctk.CTkFrame):
    def __init__(self, master,master_class, number):
        super().__init__(master, fg_color='grey80')   
        self.pack(side="top", fill="x", padx=4, pady=2)
        
        self.frame_key = number
        self.parent = master_class
                
        aoi_result_label = ctk.CTkLabel(self, text=f'Area {self.frame_key}')
        aoi_result_label.pack(side='left', padx=8, pady=2)
        
        self.aoi_result_entry = ctk.CTkEntry(self, width=280, border_width=0)
        self.aoi_result_entry.pack(side='left', fill='x', padx=8, pady=2)
        
        aoi_result_delete_button = ctk.CTkButton(self, text='delete', width=80, command=self.on_delete)
        aoi_result_delete_button.pack(side='right', padx=4, pady=2)

    def insert_data(self,data):
        self.aoi_result_entry.insert(0,data)
        
    def on_delete(self):
        print(len(self.parent.aoi_frames))
        print(self.frame_key)
        if self.frame_key in self.parent.aoi_frames:
            del self.parent.aoi_frames[self.frame_key]
            
        print(self.aoi_result_entry.get())
        test = self.parent.all_polygons[-1]
        print(str(test["points"]))    
        for polygon in self.parent.all_polygons:
            if f"[{self.aoi_result_entry.get()}]" == str(polygon["points"]):
                print("works")
                for line_plot in polygon["lines"]:
                    line_plot.remove()

                # Remove the dots associated with this polygon
                for dot in polygon["dots"]:
                    dot.remove()
                self.parent.all_polygons.remove(polygon)
        self.parent.canvas.draw() 
        self.destroy()

class AreaOfIntrest(ctk.CTkFrame):
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
        
        self.aoi_counts = 0
        self.aoi_frames = {}
        self.aoi_list = [] # this is returnable to higher classes
        
        # Initialize variables for tracking polygon points and states
        self.dots = []
        self.drawing_lines = []
        self.polygon_lines = []  # List to store line objects representing drawn segments
        self.polygon_points = []
        self.all_polygons = []  # List to store completed polygons as lists of points
        self.redo_stack = []  # Stack for redo functionality
        self.closed_polygon_redo_stack = []  # Stack to redo closed polygons

        self.zoom_pressed = False
        self.pan_pressed = False
        self.draw_pressed = False
        self.delete_pressed = False
        
        self.is_polygon_closed = False
        self.is_drawing_enabled = False  # Initially disable drawing
        self.is_deleting_enabled = False
        
        self.distance_threshold = 50  # Set the distance threshold in plot units
        
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
        
        title_label = ctk.CTkLabel(draw_tool_frame, text='Areas Of Intrest', font=('bold', 16))
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

        aoi_title_frame = ctk.CTkFrame(self.result_frame.scrollable_frame, fg_color='grey80')
        aoi_title_frame.pack(side="top", fill="x", padx=4, pady=2)
                
        aoi_title_label = ctk.CTkLabel(aoi_title_frame, text='Areas of Intrest:')
        aoi_title_label.pack(side='left', padx=8, pady=2)
        
        aoi_title_add_label = ctk.CTkButton(aoi_title_frame, text='Add', command=self.create_aoi_gui, width=80)
        aoi_title_add_label.pack(side='right', padx=4, pady=2)
        
        
        
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(side='top', fill='x', pady=4, padx=4)
        
        self.next_button = ctk.CTkButton(bottom_frame, text= 'Next', width=80)
        self.next_button.pack(side='right', pady=4, padx=4)
        
    def create_aoi_gui(self): 
        self.aoi_counts +=1
        
        aoi_frame = AoI(self.result_frame.scrollable_frame,self, self.aoi_counts)
            
        if self.is_drawing_enabled:
            last = self.all_polygons[-1]
            last1 = next(iter(last.values()))
            last2 = ', '.join(map(str,last1)) 
            aoi_frame.insert_data(last2)
            self.aoi_list.append(last2) 
            self.parent.aoi_list.append(last2)     
        
        self.aoi_frames[self.aoi_counts] = aoi_frame

    def get_aoi_list(self):
        return self.aoi_list

    
    # Function to start drawing mode with the button
    def start_drawing(self):
        if not self.draw_pressed:
            self.draw_button.configure(fg_color='#96C11F')
            self.is_polygon_closed = True
            self.is_drawing_enabled = True
            self.draw_pressed = True
            print("Drawing mode enabled.")
            if self.delete_pressed:
                self.delete_button.configure(fg_color='#E5E5E5')
                self.is_deleting_enabled = True
                self.delete_pressed = False
                print("Deleting  mode Disabled")                
        else:
            self.draw_button.configure(fg_color='#E5E5E5')
            self.is_polygon_closed = False
            self.is_drawing_enabled = False
            self.draw_pressed = False
            print("Drawing mode disabled")
        
    def start_deleting(self):
        # Store the closed polygon in all_polygons
        if self.all_polygons:
            self.all_polygons.append({
                "points": self.polygon_points[:],
                "lines": self.drawing_lines[:],
                "dots": self.drawing_dots[:]
            })
            print("open Polygon added")
        if not self.delete_pressed:  
            self.delete_button.configure(fg_color='#96C11F')
            self.is_deleting_enabled = True
            self.delete_pressed = True
            print("Deleting  mode enabled")
            if self.draw_pressed:
                self.draw_button.configure(fg_color='#E5E5E5')
                self.is_polygon_closed = False
                self.is_drawing_enabled = False
                self.draw_pressed = False
                print("Drawing mode disabled")                
        else: 
            self.delete_button.configure(fg_color='#E5E5E5')
            self.is_deleting_enabled = True
            self.delete_pressed = False
            print("Deleting  mode Disabled")

    # Function to handle mouse clicks
    def on_click(self, event):
        if self.is_drawing_enabled:
            self.on_click_draw(event)
        if self.is_deleting_enabled:
            self.on_click_delete(event)
            
        
    def on_click_draw(self, event):
        self.check_undo_redo_viability()
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            new_point = (x, y)

            # Start a new polygon if the previous one is closed
            if self.is_polygon_closed:
                # Reset data for a new polygon
                self.polygon_points = []
                self.drawing_lines = []
                self.drawing_dots = []
                self.is_polygon_closed = False
                #self.create_aoi_gui()

            # If there are existing points, check for closing the polygon
            if self.polygon_points:
                start_point = self.polygon_points[0]

                # Check if the new point is close enough to close the polygon
                if len(self.polygon_points) > 2 and self._distance(new_point, start_point) < self.distance_threshold:
                    # Replace the new point with the starting point to close the polygon
                    new_point = start_point
                    self.is_polygon_closed = True

                    # Draw the closing line to complete the polygon visually
                    last_point = self.polygon_points[-1]
                    x_vals, y_vals = zip(*[last_point, start_point])
                    line_plot, = self.ax.plot(x_vals, y_vals, 'k-')
                    self.drawing_lines.append(line_plot)

                    # Store the closed polygon in all_polygons
                    self.all_polygons.append({
                        "points": self.polygon_points[:],
                        "lines": self.drawing_lines[:],
                        "dots": self.drawing_dots[:]
                    })
                    print("Polygon closed.")
                    if len(self.all_polygons) > 0:
                        self.create_aoi_gui()
                else:
                    # Draw a line segment as usual
                    last_point = self.polygon_points[-1]
                    x_vals, y_vals = zip(*[last_point, new_point])
                    line_plot, = self.ax.plot(x_vals, y_vals, 'k-')
                    self.drawing_lines.append(line_plot)

            # Add the new point if the polygon isn't closed
            if not self.is_polygon_closed:
                self.polygon_points.append(new_point)
                dot, = self.ax.plot(x, y, 'ro', markersize=0.5)  # Mark the point visually
                self.drawing_dots.append(dot)

            # Print the number of closed polygons
            print("Number of closed polygons:", len(self.all_polygons))

            # Redraw the canvas to update the plot
            self.fig.canvas.draw()


    def on_click_delete(self, event):
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            clicked_point = (x, y)
            polygon_to_delete = None

            # Define a tolerance for detecting nearby polygons
            tolerance = 10  # Adjust based on plot scale

            # Find the nearest polygon to delete by checking if the clicked point is near any point or line
            for polygon in self.all_polygons:
                for j in range(len(polygon["points"])):
                    start = polygon["points"][j]
                    end = polygon["points"][(j + 1) % len(polygon["points"])]  # Wrap around to create a closed loop

                    # Check distance to start and end points of each line segment
                    if self._distance(clicked_point, start) < tolerance or self._distance(clicked_point, end) < tolerance:
                        polygon_to_delete = polygon
                        print("Polygon to delete found")
                        break
                if polygon_to_delete:
                    break

            # If a nearby polygon was found, delete the entire polygon
            if polygon_to_delete is not None:
                # Remove the lines associated with this polygon
                for line_plot in polygon_to_delete["lines"]:
                    line_plot.remove()

                # Remove the dots associated with this polygon
                for dot in polygon_to_delete["dots"]:
                    dot.remove()

                # Remove polygon from all_polygons list
                self.all_polygons.remove(polygon_to_delete)

                # Redraw the canvas to reflect changes
                self.fig.canvas.draw()
                print("Deleted specific polygon.")

    # Helper function for distance calculation
    def _distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    
    def check_undo_redo_viability(self):
        current_undo_state = self.undo_button.cget("state")
        current_redo_state = self.undo_button.cget("state")
        if (self.polygon_points or self.all_polygons) and current_undo_state == "disabled":
            self.undo_button.configure(state="normal")
        elif (not self.polygon_points and not self.all_polygons) and current_undo_state == "normal":
            self.undo_button.configure(state="disabled")
        
        if ( self.redo_stack or self.closed_polygon_redo_stack) and current_redo_state == "disabled":
            self.redo_button.configure(state="normal")
        elif (not self.redo_stack or not self.closed_polygon_redo_stack) and current_redo_state == "normal":
            self.redo_button.configure(state='disabled')
       
    def undo_line(self):
        # Case 1: Undo within the current (open) polygon
        if not self.is_polygon_closed and self.polygon_points:
            # Remove the last line segment and dot from the current polygon in progress
            if self.drawing_lines:
                line_segment = self.drawing_lines.pop()
                self.redo_stack.append(line_segment)  # Save for redo
                line_segment.remove()

            if self.polygon_points:
                self.polygon_points.pop()
            if self.drawing_dots:
                last_dot = self.drawing_dots.pop()
                last_dot.remove()

            print("Undo last line in the current polygon.")

        # Case 2: Undo a closed polygon
        elif self.all_polygons:
            # Remove the last closed polygon and save it for redo
            last_polygon = self.all_polygons.pop()
            self.closed_polygon_redo_stack.append(last_polygon)  # Save for redo

            # Remove all lines and dots associated with the last closed polygon
            for line_plot in last_polygon["lines"]:
                line_plot.remove()
            for dot in last_polygon["dots"]:
                dot.remove()

            print("Undo last closed polygon.")

        # Update the plot after making changes
        self.fig.canvas.draw()


    


    def redo_line(self):
        self.check_undo_redo_viability()
        # Check if there are any lines in the redo stack to redo
        if self.redo_stack:
            # Retrieve the last undone line segment
            line_segment = self.redo_stack.pop()
            start, end = line_segment

            # If the redo line segment closes the polygon, set the closed flag
            if end == self.polygon_points[0] and len(self.polygon_points) > 2:
                self.is_polygon_closed = True
                print("Redo closing of the polygon.")

            # Add the line segment back to the polygon
            self.lines.append(line_segment)
            self.polygon_points.append(end)  # Restore the last point
            x_vals, y_vals = zip(*line_segment)
            line_plot, = self.ax.plot(x_vals, y_vals, 'r-')
            self.drawing_lines.append(line_plot)

            # Redraw the end point as a dot
            dot, = self.ax.plot(end[0], end[1], 'ro')
            self.dots.append(dot)

            self.fig.canvas.draw()
            print("Redo last line.")

        if self.closed_polygon_redo_stack:
            # Restore the last removed closed polygon
            restored_polygon = self.closed_polygon_redo_stack.pop()
            self.all_polygons.append(restored_polygon)

            # Redraw the lines and dots for the restored polygon
            for line_plot in restored_polygon["lines"]:
                self.ax.add_line(line_plot)
            for dot in restored_polygon["dots"]:
                self.ax.add_line(dot)

            # Update the plot after restoring
            self.fig.canvas.draw()
            print("Redo last closed polygon.")      
                    


