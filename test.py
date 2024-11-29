import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from shapely import Polygon, LineString, Point
import string

from functools import partial

from tkinter import ttk
import customtkinter as ctk

from model.graphmaker import SimulationResults,SimulationComparison,UTCICategory,Windrose,TimeSeriesDemonstration, Slice

from custom_widgets import CustomColorPicker, Spinbox, CTkRangeSlider
from CTkSpinbox import *

'''

-maybe add map color change, 

- if not geo file got provided in the future then height change in UTCI 

- add error values

- maybe make the name of the aoi global in the app

- add the ability to remeber each variable graph settings (colors, checks, etc)

- save current button

stuff to tell eliska:
- add a remove variable function and replot 
- replot when changing the time by only changing the colors
- what is the buffer and resolution ranges in slices


for time series:
- done - add the ability to see specific plots
- update the plotting algo, to be faster
- done - make the amount of timesteps dynamic
- done - add a export tab to check the time steps to output + tranparent background

simulation result:
- done - finish the choose result combobox
- done - put axis names nect to legends
- done - add an export tab for transparent
- done - set min limit for y axis and max
- done - remove legend when removing an aoi
- done - if an aoi name is empty keep the legend except if its unchecked
- done - add the color to the fg of the combobox on initiation
- change the title when changing the result

simulation comparison:
- done - finish the choose result combobox
- done - set min limit for y axis and max
- done - fix the changing name of the simulation
- change the name of the aoi ? globalize the aoi names

UTCI:
- done - title fontsize spinbox 
- done - export tab to choose the amount of timesteps needed and in which colors
- 

windrose:
- done - export tab for transparent?

slices:
- done - change slice button ? probably going to add multiple slices throug input 
- done - resolution spin box ?
- done - buffer ?
- done - timesteps slider
- done - export tab for choosing 


idea cancelled
export window:
- each class will have a get export settings function and the structure will be a list of dictionaries
- treeview with everything and a scrollbar 
- preview button to that opens a photoviewer
- photo type?
- 
- 

'''

class SizedScrollableFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, *args, **kwargs):
        super().__init__(master, fg_color='transparent', *args, **kwargs)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.place(x=0, y=0, anchor="nw", relwidth=1, relheight=1)


class TimeSeriesRes(ctk.CTkFrame):
    def __init__(self,parent, surfpoints_inputs,airpoints_inputs, surfmesh_input,surfdata_points, airdata_input):
        super().__init__(parent, fg_color='grey95', corner_radius=0,)
        self.pack(side='top', fill= 'both', expand = True)    

        self.tsd = TimeSeriesDemonstration(
            surfpoints=surfpoints_inputs,
            airpoints=airpoints_inputs,
            surfmesh=surfmesh_input,
            surfdata=surfdata_points,
            airdata=airdata_input,
        )

        variables = ['Tair', 'RelatHumid', 'WindSpeed', 'UTCI']

        for variable in variables:
            self.tsd.add_variable(variable)

        self.checkbox_vars = {}
        
        main_plot_frame = ctk.CTkFrame(self, fg_color='grey95')
        main_plot_frame.place(relx=0.3, y=0, relwidth=0.7, relheight=1)

        slider_frame = ctk.CTkFrame(main_plot_frame)
        slider_frame.pack(side='bottom', fill='x', pady=6, padx=6)

        plot_frame = self.tsd._create_plot(main_plot_frame, 12)
        plot_frame.pack(side='bottom', fill='both', expand=True)

        # need to be fixed 

        time_slider = ctk.CTkSlider(slider_frame, from_=1, to=24, number_of_steps=24, command=self.on_slider_change)
        time_slider.pack(side='top', fill='x', pady=6, padx=6)  
        
              
        side_bar_frame = ctk.CTkFrame(self,corner_radius=0, fg_color='#F2F2F2')
        side_bar_frame.place(x=0, y=0, relwidth=0.3, relheight=1)

        side_bar_frame2 = ctk.CTkFrame(side_bar_frame)
        side_bar_frame2.pack(side='top',fill='both',expand=True, pady=6,padx=6)


        sidebar_label = ctk.CTkLabel(side_bar_frame2, text='Time Series', font=("Arial", 14))
        sidebar_label.pack(side='top', pady=8)
        
        # choose what to show
        
        config_frame = ctk.CTkFrame(side_bar_frame2)
        config_frame.pack(side='top', fill='x', padx=2, pady=2)
                
        config_frame.grid_columnconfigure(0, weight=1)
        config_frame.grid_columnconfigure(1, weight=1)
        
        config_label = ctk.CTkLabel(config_frame, text="Plot Configuration",font=('Futura', 12,'bold'))
        config_label.grid(column=0, row=0,columnspan=2, stick='WE', pady=2, padx=2)

        self.title_checkbox_var = ctk.IntVar(value=1)
        self.title_checkbox = ctk.CTkCheckBox(config_frame, text='Title:', border_width=1.5, variable=self.title_checkbox_var,onvalue=1,offvalue=0,command=self.on_title_check)
        self.title_checkbox.grid(row=1,column=0, sticky="W", pady=2,padx=4) 
        
        self.title_size_spinbox = Spinbox(config_frame, start_value = 16, min_value = 8, max_value = 38, step_size=2, command = self.on_title_font)
        self.title_size_spinbox.grid(row=1,column=1, sticky="E", pady=2,padx=4) 
        
        self.title_entry_var = ctk.StringVar()
        self.title_entry_var.trace_add("write", self.on_title_text_change)
        self.title_entry = ctk.CTkEntry(config_frame, border_width=0, textvariable=self.title_entry_var)
        self.title_entry.grid(column=0, row=2,columnspan=2, stick='WE', pady=2, padx=2)
        self.title_entry.insert(0,self.tsd.title_content)
        
        checkbox_frame = ctk.CTkFrame(config_frame, fg_color='transparent')
        checkbox_frame.grid(column=0, row=3,columnspan=2, stick='NSWE')
        
        for var in variables:
            self.checkbox_vars[var] = ctk.IntVar(value=1)
            self.data_checkbox = ctk.CTkCheckBox(checkbox_frame, text=var, border_width=1.5, variable=self.checkbox_vars[var],onvalue=1,offvalue=0,command=self.on_data_check)
            self.data_checkbox.pack(side='top', fill='x', pady=2, padx=2)           
        
        export_frame = ctk.CTkFrame(side_bar_frame2)
        export_frame.pack(side='top', fill='x',pady=4,padx=4)
        
        export_frame.grid_columnconfigure(0, weight=1)
        export_frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(export_frame, text="Export Settings",font=('Futura', 12,'bold'))
        label.grid(column=0, row=0,columnspan=2, stick='WE', pady=2, padx=2)
        
        self.transparent_var = ctk.IntVar(value=0)
        self.transparent_checkbox = ctk.CTkCheckBox(export_frame, text='Transparent Background', border_width=1.5, variable=self.transparent_var,onvalue=1,offvalue=0,command=self.on_transparent_check)
        self.transparent_checkbox.grid(column=0, row=1, stick='W', pady=2, padx=2)
        
        self.figure_color_combobox = ctk.CTkComboBox(export_frame, border_width=0, width= 90)
        self.figure_color_combobox.grid(row=1,column=1, sticky="E", pady=2,padx=4) 
        self.figure_color_combobox.set('#FFFFFF')
        self.figure_color_combobox.configure(fg_color='#FFFFFF')
        figure_combobox_colorpicker = CustomColorPicker(self.figure_color_combobox)
        figure_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.figure_color_combobox: self.on_figure_change_color(entry))
        
        
        range_slider = CTkRangeSlider(export_frame,from_=1, to=24, number_of_steps=24, command=self.slider_value)
        range_slider.grid(column=0, row=2, columnspan=2, stick='WE', pady=(2,0), padx=4)
        
        slider_label = ctk.CTkLabel(export_frame, text='1')
        slider_label.grid(column=0, row=3, stick='W', pady=(0,2), padx=2)     
        
        slider_label2 = ctk.CTkLabel(export_frame, text='24')
        slider_label2.grid(column=1, row=3, stick='E', pady=(0,2), padx=2)
        
        self.slider_result_label = ctk.CTkLabel(export_frame, text='Timesteps Chosen: 24')  
        self.slider_result_label.grid(column=0, row=4, columnspan=2, stick='WE', pady=2, padx=2)  
        
    def on_data_check(self):
        print({key: var.get() for key, var in self.checkbox_vars.items()})
    
        
    def on_figure_change_color(self, entry):
        print(entry.get())

    def on_transparent_check(self):
        if self.transparent_var.get() == 1:
            self.figure_color_combobox.configure(state='disabled')
        else:
            self.figure_color_combobox.configure(state='normal')

    def slider_value(self, value):
        result = int(value[1]) - int(value[0])
        self.slider_result_label.configure(text=f'Timesteps Chosen: {result}')
        print(int(value[0]), int(value[1]))

    def on_slider_change(self, value):
        print("the value is:", int(round(value)))
        self.tsd.update_plot_time(int(round(value)))
        if self.title_checkbox_var.get() == 1:
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, self.tsd.title_content)
            
    def on_title_check(self):
        if self.title_checkbox_var.get() == 1:
            self.tsd.set_plot_title(self.title_entry.get())
        else:
            self.tsd.remove_title()
            
    def on_title_text_change(self, *args):
        self.tsd.set_plot_title(self.title_entry_var.get())

    def on_title_font(self, value):
        self.tsd.update_font_size(value)


class SimCompRes(ctk.CTkFrame):
    def __init__(self,parent, surfpoints_inputs,surfdata_points, aoi_list, sims_list ):
        super().__init__(parent, fg_color = "gray95", corner_radius=0)
        self.pack(side='top', fill= 'both', expand = True)
        
        self.surfpoints = surfpoints_inputs
        self.surfdata = surfdata_points
        
        self.chosen_results = ["Tair", "Tsurf", "UTCI", "RelatHumid"]
        
        self.aoi = aoi_list
        self.aoi_frames = {}
        self.sims_frame_counter = 0
               
        
        self.sims = sims_list
        self.sims_frames = {}
        self.sims_frame_counter = 0 
        

        self.sc = SimulationComparison(self.surfpoints, self.sims[0])
        for i in range(len(self.aoi)):    
            self.sc.add_aoi(self.aoi[i])
        
        for i in range(1,len(self.sims)):   
            self.sc.add_simulation(self.sims[i])
        
        for i in range(len(self.chosen_results)):
            self.sc.add_variable(self.chosen_results[i])
        
        
        graph_frame = self.sc._create_plot( master=self, variable_name=self.chosen_results[0], selected_area=0)
        graph_frame.place(x=0, rely=0.4, relwidth=1, relheight=0.6)

        main_left_config_frame = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        main_left_config_frame.place(x=0, y=0, relwidth=0.5, relheight=0.4)
        
        left_config_frame = ctk.CTkFrame(main_left_config_frame, fg_color='grey90')
        left_config_frame.pack(fill='both', expand=True, pady=4, padx=4)
        
        #left_config_frame.grid_rowconfigure(0, weight=1)  # configure grid system
        left_config_frame.grid_columnconfigure(0, weight=1)
        left_config_frame.grid_columnconfigure(1, weight=1)
        
        # change figure settings 
        left_config_label = ctk.CTkLabel(left_config_frame, text='Choose results:')
        left_config_label.grid(row=0,column=0, sticky="W", pady=(4,0),padx=4)
        
        self.left_config_dropdown = ctk.CTkComboBox(left_config_frame, width=180, values=self.chosen_results, border_width=0, command=self.on_variable_select)
        self.left_config_dropdown.grid(row=0,column=1, sticky="W", pady=(4,0),padx=4)
        
        left_config_label2 = ctk.CTkLabel(left_config_frame, text='Configure Graph look:')
        left_config_label2.grid(row=1,column=0,columnspan=2, sticky="W", pady=(0,4),padx=4)
        
        self.apply_all_var = ctk.IntVar(value=0)
        self.apply_all_var = ctk.CTkCheckBox(left_config_frame, text='Apply to all results', border_width=1.5, variable=self.apply_all_var,onvalue=1,offvalue=0,command=self.on_apply_all_check)
        self.apply_all_var.grid(row=1, column=1, sticky="W", pady=4, padx=4)
        
        self.hide_legend_checkbox_var = ctk.IntVar(value=1)
        self.hide_legend_checkbox = ctk.CTkCheckBox(left_config_frame, text='Legends', border_width=1.5, variable=self.hide_legend_checkbox_var,onvalue=1,offvalue=0,command=self.on_hide_legend_check)
        self.hide_legend_checkbox.grid(row=2, column=0, sticky="W", pady=(0,4),padx=4)

        self.axis_checkbox_var = ctk.IntVar(value=1)
        self.axis_checkbox_var = ctk.CTkCheckBox(left_config_frame, text='Axis names', border_width=1.5, variable=self.axis_checkbox_var,onvalue=1,offvalue=0,command=self.on_axis_check)
        self.axis_checkbox_var.grid(row=2, column=1, sticky="W", pady=4,padx=4)
        
        
        self.title_checkbox_var = ctk.IntVar(value=1)
        self.title_checkbox = ctk.CTkCheckBox(left_config_frame, text='Title:', border_width=1.5, variable=self.title_checkbox_var,onvalue=1,offvalue=0,command=self.on_title_check)
        self.title_checkbox.grid(row=3,column=0, sticky="W", pady=(0,4),padx=4)
        
        self.title_entry_var = ctk.StringVar()
        self.title_entry_var.trace_add("write", self.on_title_text_change)
        self.title_entry = ctk.CTkEntry(left_config_frame, border_width=0, textvariable=self.title_entry_var)
        self.title_entry.grid(row=3,column=1, sticky="WE", pady=(0,4),padx=4)
        self.title_entry.insert(0,f"{self.sc.get_title(self.left_config_dropdown.get())} (Area A): Existing vs. New Design{'s' if len(self.sims) > 2 else ''}")        
        

        self.aoi_frames_scrollable = SizedScrollableFrame(left_config_frame, height=76)
        self.aoi_frames_scrollable.grid(row=4, column=0,columnspan=2,rowspan=2, sticky="WE", pady=(0,4),padx=4)
        
        self.radio_var = ctk.StringVar(value="Area A") 
        
        selected_area = self.radio_var.get()
        selected_area = selected_area.replace('Area ', '')
        self.selected_area_order = self.char_to_alphabet_order(selected_area)
        
        letters = 65
        for i in range(len(self.aoi)):
            self.create_aoi_frame(f'Area {chr(letters)}')
            letters += 1              

        main_right_config_frame = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        main_right_config_frame.place(relx=0.5, y=0, relwidth=0.5, relheight=0.4)
        
        right_config_frame = ctk.CTkFrame(main_right_config_frame, fg_color='grey90')
        right_config_frame.pack(fill='both', expand=True, pady=4, padx=4)

        right_config_frame.grid_columnconfigure(0, weight=1)
        right_config_frame.grid_columnconfigure(1, weight=1)
        
        right_config_label = ctk.CTkLabel(right_config_frame, text='Max y-axis limits')
        right_config_label.grid(row=0, column=0, sticky="W", pady=(0,4),padx=4)
        
        self.max_yaxis_limit_entry = ctk.CTkEntry(right_config_frame, border_width=0, width = 60)
        self.max_yaxis_limit_entry.grid(row=0,column=0, sticky="E", pady=4,padx=4)
        self.max_yaxis_limit_entry.bind("<KeyRelease>", self.on_max_axis_limit_change)
        self.max_yaxis_limit_entry.insert(0,self.sc.ylims[1])
        
        right_config_label = ctk.CTkLabel(right_config_frame, text='Min y-axis limits')
        right_config_label.grid(row=0, column=1, sticky="W", pady=(0,4),padx=4)
        
        self.min_yaxis_limit_entry = ctk.CTkEntry(right_config_frame, border_width=0, width = 60)
        self.min_yaxis_limit_entry.grid(row=0,column=1, sticky="E", pady=(0,4),padx=4)
        self.min_yaxis_limit_entry.bind("<KeyRelease>", self.on_min_axis_limit_change)
        self.min_yaxis_limit_entry.insert(0,self.sc.ylims[0])
        
        self.sim_parent = SizedScrollableFrame(right_config_frame, height=86)
        self.sim_parent.grid(row=2,column=0,columnspan=2,rowspan=2, sticky="WE", pady=(0,4),padx=4)
        
        right_config_label = ctk.CTkLabel(right_config_frame, text='Export Settings:')
        right_config_label.grid(row=4, column=0, sticky="W", pady=(0,4),padx=4)
        
        self.transparent_figure_var = ctk.IntVar(value=0)
        self.transparent_figure = ctk.CTkCheckBox(right_config_frame, text='Transparent figure', border_width=1.5, variable=self.transparent_figure_var, onvalue=1, offvalue=0, command=self.on_transparent_figure_check)
        self.transparent_figure.grid(row=5,column=0, sticky="W", pady=(0,4),padx=4) 

        self.figure_color_combobox = ctk.CTkComboBox(right_config_frame, border_width=0, width= 92)
        self.figure_color_combobox.grid(row=5,column=0, sticky="E", pady=(0,4),padx=4) 
        self.figure_color_combobox.set('#FFFFFF')
        self.figure_color_combobox.configure(fg_color='#FFFFFF')
        figure_combobox_colorpicker = CustomColorPicker(self.figure_color_combobox)
        figure_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.figure_color_combobox: self.on_figure_change_color(entry))
        
        self.transparent_graph_var = ctk.IntVar(value=0)
        self.transparent_graph = ctk.CTkCheckBox(right_config_frame, text='Transparent graph', border_width=1.5, variable=self.transparent_graph_var, onvalue=1, offvalue=0, command=self.on_transparent_graph_check)
        self.transparent_graph.grid(row=5,column=1, sticky="W", pady=(0,4),padx=4)     
                   
        self.graph_color_combobox = ctk.CTkComboBox(right_config_frame, border_width=0, width= 92)
        self.graph_color_combobox.grid(row=5,column=1, sticky="E", pady=(0,4),padx=4) 
        self.graph_color_combobox.set('#FFFFFF')
        self.graph_color_combobox.configure(fg_color='#FFFFFF')
        graph_combobox_colorpicker = CustomColorPicker(self.graph_color_combobox)
        graph_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.graph_color_combobox: self.on_graph_change_color(entry))
               

        # Default selection   
        for i in range(len(self.sims)):
            i += 1
            self.create_sim_frame(f'Simulation {i}')
                
    def create_aoi_frame(self, placeholder ):
        self.aoi_frame = ctk.CTkFrame(self.aoi_frames_scrollable.scrollable_frame, fg_color='grey80')
        self.aoi_frame.pack(side="top", fill="x", padx=4, pady=2)        
        
        aoi_frame_checkbox = ctk.CTkRadioButton(self.aoi_frame, text=placeholder, variable=self.radio_var, value=placeholder, command=self.on_radio_select) 
        aoi_frame_checkbox.pack(side='left', pady=2, padx=2) 
        
    def on_radio_select(self):
        selected_area = self.radio_var.get()
        selected_area = selected_area.replace('Area ', '')
        self.selected_area_order = self.char_to_alphabet_order(selected_area)
        print(self.selected_area_order)
        self.sc.update_plot( variable_name=self.left_config_dropdown.get(), selected_area=self.selected_area_order)

    def char_to_alphabet_order(self, char):
        char = char.upper()  # Convert to uppercase for consistency
        return ord(char) - 65

    def create_sim_frame(self, placeholder):
        sim_frame = ctk.CTkFrame(self.sim_parent.scrollable_frame, fg_color='grey80')
        sim_frame.pack(side="top", fill="x", padx=4, pady=2)        
        
        sim_frame_checkbox_var = ctk.IntVar(value = 1)
        sim_frame_checkbox = ctk.CTkCheckBox(sim_frame, text='', border_width=1.5, width=12, variable=sim_frame_checkbox_var,
                                             onvalue=1, offvalue=0, command=partial(self.on_sim_frame_check, self.sims_frame_counter)) 
        sim_frame_checkbox.pack(side='left', pady=2, padx=2) 
        
        sim_frame_entry = ctk.CTkEntry(sim_frame, border_width=0)     
        sim_frame_entry.pack(side='left', pady=2, padx=2)
        sim_frame_entry.bind("<KeyRelease>", lambda event, frame_id=self.sims_frame_counter, entry=sim_frame_entry: self.on_sim_frame_name_change(frame_id, entry))
        sim_frame_entry.insert(0,placeholder)
        
        self.sims_frames[self.sims_frame_counter] = {
                "frame_id": self.sims_frame_counter,
                "frame": sim_frame,
                "check_var": sim_frame_checkbox_var,
                "sim_name": placeholder,           
        }
        
        self.sims_frame_counter += 1
        
    def on_sim_frame_check(self, frame_id):
        """Toggle visibility of AOI plot line based on checkbox state."""
        details = self.sims_frames[frame_id]
        frame_id = details['frame_id']
        check_var = details["check_var"]
        
        line = self.sc.sims_lines.get(frame_id)

        if not line:
            print(f"No line found for frame {frame_id}")
            
        # Toggle line visibility
        if check_var.get() == 1:
            line.set_visible(True)
            current_text = self.sims_frames[frame_id]["sim_name"]
            line.set_label(current_text)
        else:
            line.set_visible(False)
        self.sc.set_legend()
        self.sc.canvas.draw()
        
                    

    def on_sim_frame_name_change(self, frame_id, entry):
        details = self.sims_frames[frame_id]
        frame_id = details['frame_id']    
        
        line = self.sc.sims_lines.get(frame_id)
        if not line:
            print(f"No line found for frame {frame_id}.")
            return

        # Update only if checkbox is active
        if details["check_var"].get() == 1:
            current_text = entry.get()
            self.sims_frames[frame_id]["sim_name"] = current_text
            line.set_label(current_text)


            # Redraw the canvas to reflect the updated label
            self.sc.set_legend()

    def on_apply_all_check(self):
        print('called')

    def on_hide_legend_check(self):
        if self.hide_legend_checkbox_var.get() == 1:
            self.sc.set_legend()
        else:
            self.sc.remove_legend()
 
    def on_axis_check(self):
        if self.axis_checkbox_var.get() == 1:
            self.sc.show_axis_label()
        else:
            self.sc.hide_axis_label()

    def on_title_check(self):
        if self.title_checkbox_var.get() == 1:
            self.title_entry.configure(state='normal')
            self.sc.set_new_title(self.title_entry.get())

        else:
            self.title_entry.configure(state='disabled')
            self.sc.remove_title()
            
    def on_title_text_change(self, *args):
        self.sc.set_new_title(self.title_entry_var.get())

    def on_max_axis_limit_change(self, *args):
        if self.max_yaxis_limit_entry.get() == '':
            return
        
        new_limit = int(self.max_yaxis_limit_entry.get())
        self.sc.set_max_ylims(new_limit)

    def on_min_axis_limit_change(self, *args):
        if self.min_yaxis_limit_entry.get() == '':
            return
        
        new_limit = int(self.min_yaxis_limit_entry.get())
        self.sc.set_min_ylims(new_limit)
           
    def on_transparent_figure_check(self):    
        if self.transparent_figure_var.get() == 1:
            self.figure_color_combobox.configure(state='disabled')
        else:
            self.figure_color_combobox.configure(state='normal')
            
    def on_figure_change_color(self,entry):
        color = entry.get()
        entry.configure(fg_color= color)         
        
    def on_transparent_graph_check(self):
        if self.transparent_graph_var.get() == 1:
            self.graph_color_combobox.configure(state='disabled') 
        else:
            self.graph_color_combobox.configure(state='normal')
                       
    def on_graph_change_color(self, entry):                
        color = entry.get()
        entry.configure(fg_color= color)  
        
    def on_variable_select(self, event):
        selected = self.left_config_dropdown.get()
        self.sc.update_plot(selected, self.selected_area_order)
 
      
class SimResRes(ctk.CTkFrame):
    def __init__(self,parent, surfacepoints_input, surface_data_input , aoi_list):
        super().__init__(parent, fg_color = "gray95", corner_radius=0)
        self.pack(side='top', fill= 'both', expand = True)

        self.surfpoints = surfacepoints_input
        self.surfdata = surface_data_input
        
        self.chosen_results = ["Tair", "Tsurf", "UTCI", "RelatHumid"]
        
        self.aoi = aoi_list
        self.aoi_frames = {} 
        self.frame_counter = 0

        self.sr = SimulationResults(self.surfpoints, self.surfdata, self.chosen_results[0])
        
        for i in range(len(self.aoi)):
            self.sr.add_area_of_interest(self.aoi[i])

        
        
        
        plot_frame = self.sr.create_plot(self)
        plot_frame.place(x=0, rely=0.4, relwidth=1, relheight=0.6)
                
        main_left_config_frame = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        main_left_config_frame.place(x=0, y=0, relwidth=0.5, relheight=0.4)
        
        left_config_frame = ctk.CTkFrame(main_left_config_frame, fg_color='grey90')
        left_config_frame.pack(fill='both', expand=True, pady=4, padx=4)
        
        #left_config_frame.grid_rowconfigure(0, weight=1)  # configure grid system
        left_config_frame.grid_columnconfigure(0, weight=1)
        left_config_frame.grid_columnconfigure(1, weight=1)
        
        # change figure settings 
        left_config_label = ctk.CTkLabel(left_config_frame, text='Choose results:')
        left_config_label.grid(row=0,column=0, sticky="W", pady=(4,0),padx=4)
        
        self.left_config_dropdown = ctk.CTkComboBox(left_config_frame, width=180, values= self.chosen_results, border_width=0, command=self.on_variable_select)
        self.left_config_dropdown.grid(row=0,column=1, sticky="W", pady=(4,0),padx=4)
        self.left_config_dropdown.set(self.chosen_results[0])
        
        left_config_label2 = ctk.CTkLabel(left_config_frame, text='Configure Graph look:')
        left_config_label2.grid(row=1,column=0,columnspan=2, sticky="W", pady=(0,4),padx=4)
        
        self.apply_all_var = ctk.IntVar(value=0)
        self.apply_all_var = ctk.CTkCheckBox(left_config_frame, text='Apply to all results', border_width=1.5, variable=self.apply_all_var,onvalue=1,offvalue=0,command=self.on_apply_all_check)
        self.apply_all_var.grid(row=1, column=1, sticky="W", pady=4, padx=4)
        
        self.hide_legend_checkbox_var = ctk.IntVar(value=1)
        self.hide_legend_checkbox = ctk.CTkCheckBox(left_config_frame, text='Legends', border_width=1.5, variable=self.hide_legend_checkbox_var,onvalue=1,offvalue=0,command=self.on_hide_legend_check)
        self.hide_legend_checkbox.grid(row=2, column=0, sticky="W", pady=(0,4),padx=4)
        
        self.axis_checkbox_var = ctk.IntVar(value=1)
        self.axis_checkbox_var = ctk.CTkCheckBox(left_config_frame, text='Axis names', border_width=1.5, variable=self.axis_checkbox_var,onvalue=1,offvalue=0,command=self.on_axis_check)
        self.axis_checkbox_var.grid(row=2, column=1, sticky="W", pady=4, padx=4)
        
        self.title_checkbox_var = ctk.IntVar(value=1)
        self.title_checkbox = ctk.CTkCheckBox(left_config_frame, text='Title:', border_width=1.5, variable=self.title_checkbox_var,onvalue=1,offvalue=0,command=self.on_title_check)
        self.title_checkbox.grid(row=3,column=0, sticky="W", pady=(0,4),padx=4)
        
        self.title_entry_var = ctk.StringVar()
        self.title_entry_var.trace_add("write", self.on_title_text_change)
        self.title_entry = ctk.CTkEntry(left_config_frame, border_width=0, textvariable=self.title_entry_var)
        self.title_entry.grid(row=3,column=1, sticky="WE", pady=(0,4),padx=4)
        self.title_entry.insert(0,self.sr.get_title(self.left_config_dropdown.get()))        
        
        self.note_checkbox_var = ctk.IntVar(value=1)
        self.note_checkbox = ctk.CTkCheckBox(left_config_frame, text='Note:', border_width=1.5, variable=self.note_checkbox_var,onvalue=1,offvalue=0,command=self.on_note_check)
        self.note_checkbox.grid(row=4,column=0, sticky="WN", pady=(0,4),padx=4)
        
        self.note_textbox = ctk.CTkTextbox(left_config_frame, height=60)
        self.note_textbox.grid(row=4,column=1,rowspan=2, sticky="WE", pady=(0,4),padx=4)
        self.note_textbox.bind("<KeyRelease>", self.on_note_text_change)
        self.note_textbox.insert("1.0", self.sr.note_content)

        main_right_config_frame = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        main_right_config_frame.place(relx=0.5, y=0, relwidth=0.5, relheight=0.4)
        
        right_config_frame = ctk.CTkFrame(main_right_config_frame, fg_color='grey90')
        right_config_frame.pack(fill='both', expand=True, pady=4, padx=4)

        right_config_frame.grid_columnconfigure(0, weight=1)
        right_config_frame.grid_columnconfigure(1, weight=1)
        

        
        right_config_label = ctk.CTkLabel(right_config_frame, text='Max y-axis limits')
        right_config_label.grid(row=1, column=0, sticky="W", pady=(0,4),padx=4)
        
        self.max_yaxis_limit_entry = ctk.CTkEntry(right_config_frame, border_width=0, width = 60)
        self.max_yaxis_limit_entry.grid(row=1,column=0, sticky="E", pady=4,padx=4)
        self.max_yaxis_limit_entry.bind("<KeyRelease>", self.on_max_axis_limit_change)
        self.max_yaxis_limit_entry.insert(0,self.sr.ylims[1])
        
        right_config_label = ctk.CTkLabel(right_config_frame, text='Min y-axis limits')
        right_config_label.grid(row=1, column=1, sticky="W", pady=(0,4),padx=4)
        
        self.min_yaxis_limit_entry = ctk.CTkEntry(right_config_frame, border_width=0, width = 60)
        self.min_yaxis_limit_entry.grid(row=1,column=1, sticky="E", pady=(0,4),padx=4)
        self.min_yaxis_limit_entry.bind("<KeyRelease>", self.on_min_axis_limit_change)
        self.min_yaxis_limit_entry.insert(0,self.sr.ylims[0])
        
        self.aoi_parent = SizedScrollableFrame(right_config_frame, height=86)
        self.aoi_parent.grid(row=2,column=0,columnspan=2,rowspan=2, sticky="WE", pady=(0,4),padx=4)

        letters = 65
        colors = self.sr.get_colors(len(self.aoi))
        for i in range(len(aoi_list)):
            self.create_aoi_frame(f'Area {chr(letters)}', colors[i])
            letters += 1
        
        right_config_label = ctk.CTkLabel(right_config_frame, text='Export Settings:')
        right_config_label.grid(row=4, column=0, sticky="W", pady=(0,4),padx=4)
        
        self.transparent_figure_var = ctk.IntVar(value=0)
        self.transparent_figure = ctk.CTkCheckBox(right_config_frame, text='Transparent figure', border_width=1.5, variable=self.transparent_figure_var, onvalue=1, offvalue=0, command=self.on_transparent_figure_check)
        self.transparent_figure.grid(row=5,column=0, sticky="W", pady=(0,4),padx=4) 

        self.figure_color_combobox = ctk.CTkComboBox(right_config_frame, border_width=0, width= 92)
        self.figure_color_combobox.grid(row=5,column=0, sticky="E", pady=(0,4),padx=4) 
        self.figure_color_combobox.set('#FFFFFF')
        self.figure_color_combobox.configure(fg_color='#FFFFFF')
        figure_combobox_colorpicker = CustomColorPicker(self.figure_color_combobox)
        figure_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.figure_color_combobox: self.on_figure_change_color(entry))
        
        self.transparent_graph_var = ctk.IntVar(value=0)
        self.transparent_graph = ctk.CTkCheckBox(right_config_frame, text='Transparent graph', border_width=1.5, variable=self.transparent_graph_var, onvalue=1, offvalue=0, command=self.on_transparent_graph_check)
        self.transparent_graph.grid(row=5,column=1, sticky="W", pady=(0,4),padx=4)     
                   
        self.graph_color_combobox = ctk.CTkComboBox(right_config_frame, border_width=0, width= 92)
        self.graph_color_combobox.grid(row=5,column=1, sticky="E", pady=(0,4),padx=4) 
        self.graph_color_combobox.set('#FFFFFF')
        self.graph_color_combobox.configure(fg_color='#FFFFFF')
        graph_combobox_colorpicker = CustomColorPicker(self.graph_color_combobox)
        graph_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.graph_color_combobox: self.on_graph_change_color(entry))
                
    def on_variable_select(self, event):
        selected = self.left_config_dropdown.get()
        self.sr.update_plot(selected)
        
    def create_aoi_frame(self, placeholder, color):
        aoi_frame = ctk.CTkFrame(self.aoi_parent.scrollable_frame, fg_color='grey80')
        aoi_frame.pack(side="top", fill="x", padx=4, pady=2)        
        
        aoi_frame_checkbox_var = ctk.IntVar(value = 1)
        aoi_frame_checkbox = ctk.CTkCheckBox(aoi_frame, text='', border_width=1.5, width=12, variable=aoi_frame_checkbox_var,
                                             onvalue=1, offvalue=0, command=partial(self.on_aoi_frame_check, self.frame_counter)) 
        aoi_frame_checkbox.pack(side='left', pady=2, padx=2) 
        
        aoi_frame_entry = ctk.CTkEntry(aoi_frame, border_width=0)     
        aoi_frame_entry.pack(side='left', pady=2, padx=2)
        aoi_frame_entry.bind("<KeyRelease>", lambda event, frame_id=self.frame_counter, entry=aoi_frame_entry: self.on_aoi_frame_name_change(frame_id, entry))
        aoi_frame_entry.insert(0,placeholder)
        
        aoi_frame_label = ctk.CTkLabel(aoi_frame, text ='Color:')
        aoi_frame_label.pack(side='left', pady=2, padx=(4,2))
        
        aoi_color_combobox = ctk.CTkComboBox(aoi_frame, border_width=0, width= 92)
        aoi_color_combobox.pack(side="left", pady=2, padx=2)
        aoi_color_combobox.set(color)
        aoi_color_combobox.configure(fg_color=color)
        combobox_colorpicker = CustomColorPicker(aoi_color_combobox)
        combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, frame_id=self.frame_counter, entry=aoi_color_combobox: self.on_aoi_change_color(frame_id, entry))
        
        self.aoi_frames[self.frame_counter] = {
                "frame_id": self.frame_counter,
                "frame": aoi_frame,
                "check_var": aoi_frame_checkbox_var,
                "aoi_name": placeholder,
                "aoi_color":color
            }

        self.frame_counter += 1
            
    def on_aoi_frame_check(self, frame_id):
        """Toggle visibility of AOI plot line based on checkbox state."""
        details = self.aoi_frames[frame_id]
        frame_id = details['frame_id']
        check_var = details["check_var"]
        
        line = self.sr.aoi_lines.get(frame_id)

        if line:
            if check_var.get() == 1:
            # Toggle line visibility
                line.set_visible(True)
                current_text = self.aoi_frames[frame_id]["aoi_name"] 
                line.set_label(current_text)
            else:
                line.set_visible(False)
                line.set_label('')                
            self.sr.set_legend()
            self.sr.canvas.draw()
        else:
            print(f"No line found for frame {frame_id}")

    def on_aoi_frame_name_change(self, frame_id, entry):
        details = self.aoi_frames[frame_id]
        frame_id = details['frame_id']    
        
        line = self.sr.aoi_lines.get(frame_id)
        if not line:
            print(f"No line found for frame {frame_id}.")
            return

        # Update only if checkbox is active
        if details["check_var"].get() == 1:
            current_text = entry.get()
            if current_text == '':
                current_text = ' '
            self.aoi_frames[frame_id]["aoi_name"] = current_text
            line.set_label(current_text)
            print(f"Updated name for frame {frame_id}: {current_text}")

            # Redraw the canvas to reflect the updated label
            self.sr.set_legend()
            #self.sr.canvas.draw()

    def on_aoi_change_color(self, frame_id, combobox):
        details = self.aoi_frames[frame_id]
        frame_id = details['frame_id']    
        
        line = self.sr.aoi_lines.get(frame_id)
        if not line:
            print(f"No line found for frame {frame_id}.")
            return

        # Update only if checkbox is active
        if details["check_var"].get() == 1:
            current_selected_color = combobox.get()
            combobox.configure(fg_color=current_selected_color)
            self.aoi_frames[frame_id]["color"] = current_selected_color
            line.set_color(current_selected_color)
            print(f"Updated name for frame {frame_id}: {current_selected_color}")
        self.sr.set_legend()   
      
    def on_apply_all_check(self):
        print('called')  
        
    def on_hide_legend_check(self):
        if self.hide_legend_checkbox_var.get() == 1:
            self.sr.set_legend()
        else:
            self.sr.remove_legend()
    
    def on_title_check(self):
        if self.title_checkbox_var.get() == 1:
            self.title_entry.configure(state='normal')
            self.sr.set_title(self.title_entry.get())
            self.sr.set_plot_title()
        else:
            self.title_entry.configure(state='disabled')
            self.sr.remove_title()
            
    def on_title_text_change(self, *args):
        self.sr.set_title(self.title_entry_var.get())
        self.sr.set_plot_title()
        
    def on_note_check(self):
        if self.note_checkbox_var.get() == 1:
            self.note_textbox.configure(state='normal')
            new_note_text = self.note_textbox.get("1.0", "end-1c")
            self.sr.set_plot_note(new_note_text)
        else:
            self.note_textbox.configure(state='disabled')
            self.sr.remove_note()
            
    def on_note_text_change(self, *args):
        new_note_text = self.note_textbox.get("1.0", "end-1c")
        self.sr.set_plot_note(new_note_text)
        
    def on_axis_check(self):
        if self.axis_checkbox_var.get() == 1:
            self.sr.show_axis_label()
        else:
            self.sr.hide_axis_label()

    def on_max_axis_limit_change(self, *args):
        if self.max_yaxis_limit_entry.get() == '':
            return
        
        new_limit = int(self.max_yaxis_limit_entry.get())
        self.sr.set_max_ylims(new_limit)

    def on_min_axis_limit_change(self, *args):
        if self.min_yaxis_limit_entry.get() == '':
            return
        
        new_limit = int(self.min_yaxis_limit_entry.get())
        self.sr.set_min_ylims(new_limit)
        
    def on_transparent_figure_check(self):    
        if self.transparent_figure_var.get() == 1:
            self.figure_color_combobox.configure(state='disabled')
        else:
            self.figure_color_combobox.configure(state='normal')
            
    def on_figure_change_color(self,entry):
        color = entry.get()
        entry.configure(fg_color= color)         
        
    def on_transparent_graph_check(self):
        if self.transparent_graph_var.get() == 1:
            self.graph_color_combobox.configure(state='disabled') 
        else:
            self.graph_color_combobox.configure(state='normal')
                       
    def on_graph_change_color(self, entry):                
        color = entry.get()
        entry.configure(fg_color= color)  
        
        
class UTCICategoryRes(ctk.CTkFrame):
    def __init__(self, parent, surfpoints_inputs, surfdata_points, surfmesh_input):
        super().__init__(parent, fg_color='#F2F2F2')

        self.surfpoints = surfpoints_inputs
        self.surfdata = surfdata_points
        self.surfmesh = surfmesh_input

        # Create the main frames
        self.utci = UTCICategory(self.surfpoints, self.surfdata, self.surfmesh)

        # Main plot frame
        main_plot_frame = ctk.CTkFrame(self, fg_color='transparent')
        main_plot_frame.place(relx=0.3, y=0, relwidth=0.7, relheight=1)

        plot_frame = self.utci._create_plot(main_plot_frame)
        plot_frame.pack(side='top', fill='both', expand=True)
        
        slider_frame= ctk.CTkFrame(main_plot_frame)
        slider_frame.pack(side='top', fill='x',pady=6, padx=6)

        time_slider = ctk.CTkSlider(slider_frame, from_=1, to=24, number_of_steps=24, command=self.on_slider_change)
        time_slider.pack(side='top', fill='x',pady=6, padx=6)

        # Sidebar frame for radio buttons and slider
        side_bar_frame = ctk.CTkFrame(self,corner_radius=0, fg_color='#F2F2F2')
        side_bar_frame.place(x=0, y=0, relwidth=0.3, relheight=1)

        side_bar_frame2 = ctk.CTkFrame(side_bar_frame)
        side_bar_frame2.pack(side='top',fill='both',expand=True, pady=6,padx=6)


        sidebar_label = ctk.CTkLabel(side_bar_frame2, text='UTCI Category:', font=("Arial", 14))
        sidebar_label.pack(side='top', pady=8)

        radio_frame = ctk.CTkFrame(side_bar_frame2, fg_color='transparent')
        radio_frame.pack(side='top', pady=8, padx=8, fill="x")

        self.radio_var = ctk.StringVar(value="no thermal stress")

        # Define stress categories
        stress_categories = [
            ("extreme heat stress", "extreme", "#8B0000"),
            ("very strong heat stress", "very_strong", "#FF0000"),
            ("strong heat stress", "strong", "#FF4500"),
            ("moderate heat stress", "moderate", "#FFA500"),
            ("no thermal stress", "no", "#00FF00")
        ]

        # Loop to create radio buttons with specific padding
        for idx, (text, value, color) in enumerate(stress_categories):
            inner_frame = ctk.CTkFrame(radio_frame, fg_color=color, corner_radius=6)
            inner_frame.pack(side='top', fill='x')

            # Set padding conditions for the first, last, and other buttons
            if idx == 0:
                button_pady = (2, 0)  # First button
            elif idx == len(stress_categories) - 1:
                button_pady = (0, 2)  # Last button
            else:
                button_pady = 0  # Middle buttons

            # Create the radio button
            ctk.CTkRadioButton(inner_frame,text=text,height=32,variable=self.radio_var,value=value,
                fg_color="black",command=self.on_radio_select).pack(side='top', fill='x', pady=button_pady,padx=1)

        config_frame = ctk.CTkFrame(side_bar_frame2)
        config_frame.pack(side='top', fill='x', padx=2, pady=2)
                
        config_frame.grid_columnconfigure(0, weight=1)
        config_frame.grid_columnconfigure(1, weight=1)
        
        config_label = ctk.CTkLabel(config_frame, text="Plot Configuration",font=('Futura', 12,'bold'))
        config_label.grid(column=0, row=0,columnspan=2, stick='WE', pady=2, padx=2)

        self.title_checkbox_var = ctk.IntVar(value=1)
        self.title_checkbox = ctk.CTkCheckBox(config_frame, text='Title:', border_width=1.5, variable=self.title_checkbox_var,onvalue=1,offvalue=0,command=self.on_title_check)
        self.title_checkbox.grid(row=1,column=0, sticky="W", pady=2,padx=4) 
        
        self.title_size_spinbox = Spinbox(config_frame, start_value = 16, min_value = 8, max_value = 38, step_size=2, command = self.on_title_font)
        self.title_size_spinbox.grid(row=1,column=1, sticky="E", pady=2,padx=4) 
        
        self.title_entry_var = ctk.StringVar()
        self.title_entry_var.trace_add("write", self.on_title_text_change)
        self.title_entry = ctk.CTkEntry(config_frame, border_width=0, textvariable=self.title_entry_var)
        self.title_entry.grid(column=0, row=2,columnspan=2, stick='WE', pady=2, padx=2)
        self.title_entry.insert(0,self.utci.title_content) 
        
        export_frame = ctk.CTkFrame(side_bar_frame2)
        export_frame.pack(side='top', fill='x',pady=4,padx=4)
        
        export_frame.grid_columnconfigure(0, weight=1)
        export_frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(export_frame, text="Export Settings",font=('Futura', 12,'bold'))
        label.grid(column=0, row=0,columnspan=2, stick='WE', pady=2, padx=2)
        
        self.transparent_var = ctk.IntVar(value=0)
        self.transparent_checkbox = ctk.CTkCheckBox(export_frame, text='Transparent Background', border_width=1.5, variable=self.transparent_var,onvalue=1,offvalue=0,command=self.on_transparent_check)
        self.transparent_checkbox.grid(column=0, row=1, stick='W', pady=2, padx=2)
        
        self.figure_color_combobox = ctk.CTkComboBox(export_frame, border_width=0, width= 90)
        self.figure_color_combobox.grid(row=1,column=1, sticky="E", pady=2,padx=4) 
        self.figure_color_combobox.set('#FFFFFF')
        self.figure_color_combobox.configure(fg_color='#FFFFFF')
        figure_combobox_colorpicker = CustomColorPicker(self.figure_color_combobox)
        figure_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.figure_color_combobox: self.on_figure_change_color(entry))
        
        range_slider = CTkRangeSlider(export_frame,from_=1, to=24, number_of_steps=24, command=self.slider_value)
        range_slider.grid(column=0, row=2, columnspan=2, stick='WE', pady=(2,0), padx=4)
        
        slider_label = ctk.CTkLabel(export_frame, text='1')
        slider_label.grid(column=0, row=3, stick='W', pady=(0,2), padx=2)     
        
        slider_label2 = ctk.CTkLabel(export_frame, text='24')
        slider_label2.grid(column=1, row=3, stick='E', pady=(0,2), padx=2)
        
        self.slider_result_label = ctk.CTkLabel(export_frame, text='Timesteps Chosen: 24')  
        self.slider_result_label.grid(column=0, row=4, columnspan=2, stick='WE', pady=2, padx=2)  
        
    def on_figure_change_color(self, entry):
        print(entry.get())

    def on_transparent_check(self):
        if self.transparent_var.get() == 1:
            self.figure_color_combobox.configure(state='disabled')
        else:
            self.figure_color_combobox.configure(state='normal')

    def slider_value(self, value):
        result = int(value[1]) - int(value[0])
        self.slider_result_label.configure(text=f'Timesteps Chosen: {result}')
        print(int(value[0]), int(value[1]))

    def on_slider_change(self, value):
        self.utci.update_plot_time(int(round(value)))
        if self.title_checkbox_var.get() == 1:
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, self.utci.title_content)

    def on_radio_select(self):
        self.utci.update_plot_category(self.radio_var.get())
        if self.title_checkbox_var.get() == 1:
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, self.utci.title_content)
        
    def on_title_check(self):
        if self.title_checkbox_var.get() == 1:
            self.utci.set_title(self.title_entry.get())
        else:
            self.utci.remove_title()
            
    def on_title_text_change(self, *args):
        self.utci.set_title(self.title_entry_var.get())

    def on_title_font(self, value):
        self.utci.update_font_size(value)        
 
        
class WindRoseRes(ctk.CTkFrame):
    def __init__(self, parent, airponts_input, airdata_input):
        super().__init__(parent, fg_color='transparent')  
        
        self.airpoints = airponts_input
        self.airdata = airdata_input
        
        self.current_cmap = "YlOrRd_r"
        self.colormaps = ['magma', 'inferno', 'plasma', 'viridis', 'cividis', 'twilight', 'twilight_shifted', 'turbo', 'Blues',"YlOrRd","YlOrRd_r"]
        
        self.wr = Windrose(self.airpoints, self.airdata)

        

        main_plot_frame = ctk.CTkFrame(self, fg_color='transparent')
        main_plot_frame.place(relx=0.3, y=0, relwidth=0.7, relheight=1)
        
        self.wr._create_plot(main_plot_frame)     
        
        side_bar_frame = ctk.CTkFrame(self,corner_radius=0, fg_color='#F2F2F2')
        side_bar_frame.place(x=0, y=0, relwidth=0.3, relheight=1)

        side_bar_frame2 = ctk.CTkFrame(side_bar_frame)
        side_bar_frame2.pack(side='top',fill='both',expand=True, pady=6,padx=6)


        sidebar_label = ctk.CTkLabel(side_bar_frame2, text='Windorose:', font=("Arial", 14))
        sidebar_label.pack(side='top', pady=8)  
        
        configuration_frame = ctk.CTkFrame(side_bar_frame2, fg_color='transparent')
        configuration_frame.pack(side='top',fill='both',expand=True, pady=2) 

        configuration_frame.grid_columnconfigure(0, weight=1)
        configuration_frame.grid_columnconfigure(1, weight=1)

        self.title_checkbox_var = ctk.IntVar(value=0)
        self.title_checkbox = ctk.CTkCheckBox(configuration_frame, text='Title:', border_width=1.5, variable=self.title_checkbox_var,onvalue=1,offvalue=0,command=self.on_title_check)
        self.title_checkbox.grid(row=0,column=0, sticky="W", pady=(4,0),padx=4)
        
        self.title_size_spinbox = Spinbox( configuration_frame, start_value = 16, min_value = 8, max_value = 38, step_size=2, command = self.on_title_font)
        self.title_size_spinbox.grid(row=0,column=1, sticky="E", pady=(4,0),padx=4)

        self.title_entry_var = ctk.StringVar()
        self.title_entry_var.trace_add("write", self.on_title_text_change)
        self.title_entry = ctk.CTkEntry(configuration_frame, border_width=0, textvariable=self.title_entry_var)
        self.title_entry.grid(row=1,column=0, columnspan=2, sticky="WE", pady=(4,0),padx=4)
        self.title_entry.insert(0,self.wr.title_content) 
        
        self.legends_checkbox_var = ctk.IntVar(value=1)
        self.legends_checkbox = ctk.CTkCheckBox(configuration_frame, text='Legends', border_width=1.5, variable=self.legends_checkbox_var,onvalue=1,offvalue=0,command=self.on_legends_check)
        self.legends_checkbox.grid(row=2,column=0, sticky="W", pady=(4,0),padx=4)
        
        sidebar_label2 = ctk.CTkLabel(configuration_frame, text='Colors:')
        sidebar_label2.grid(row=3,column=0, sticky="W", pady=(4,0),padx=4)
        
        self.color_combobox = ctk.CTkComboBox(configuration_frame, values=self.colormaps, border_width=0, state="readonly", command=self.on_cmap_change)
        self.color_combobox.grid(row=3,column=1, sticky="WE", pady=(4,0),padx=4)
        self.color_combobox.set(self.current_cmap)
        
        label = ctk.CTkLabel(configuration_frame, text="Export Settings")
        label.grid(column=0, row=4,columnspan=2, stick='WE', pady=2, padx=2)        
        
        self.transparent_var = ctk.IntVar(value=0)
        self.transparent_checkbox = ctk.CTkCheckBox(configuration_frame, text='Transparent Background', border_width=1.5, variable=self.transparent_var,onvalue=1,offvalue=0,command=self.on_transparent_check)
        self.transparent_checkbox.grid(column=0, row=5, stick='W', pady=2, padx=2)
        
        self.figure_color_combobox = ctk.CTkComboBox(configuration_frame, border_width=0, width= 90)
        self.figure_color_combobox.grid(row=5,column=1, sticky="E", pady=2,padx=4) 
        self.figure_color_combobox.set('#FFFFFF')
        self.figure_color_combobox.configure(fg_color='#FFFFFF')
        figure_combobox_colorpicker = CustomColorPicker(self.figure_color_combobox)
        figure_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.figure_color_combobox: self.on_figure_change_color(entry))

    def on_figure_change_color(self, entry):
        print(entry.get())

    def on_transparent_check(self):
        if self.transparent_var.get() == 1:
            self.figure_color_combobox.configure(state='disabled')
        else:
            self.figure_color_combobox.configure(state='normal')
       
        
    def on_title_check(self):
        if self.title_checkbox_var.get() == 1:
            self.wr.set_plot_title(self.title_entry.get())
        else:
            self.wr.remove_title()
            
    def on_title_text_change(self, *args):
        self.wr.set_plot_title(self.title_entry_var.get())
        
    def on_legends_check(self):
        if self.legends_checkbox_var.get() == 1:
            self.wr.set_legends()
        else:
            self.wr.remove_legends()
            
    def on_cmap_change(self, event):
        """Update the windrose plot with the selected colormap."""
        self.current_cmap = self.color_combobox.get()  # Get the selected colormap
        print('called succesfully')
        self.wr.color_change(self.current_cmap)
        self.on_legends_check()

    def on_title_font(self, value):
        self.wr.update_font_size(value)
        

class SliceRes(ctk.CTkFrame):
    def __init__(self, parent, airpoints_input, airdata_input):
        super().__init__(parent, fg_color="grey95")
        
        self.airpoints = airpoints_input
        self.airdata = airdata_input
        
        self.current_cmap = "coolwarm"
        self.colormaps = ["coolwarm", 'magma', 'inferno', 'plasma', 'viridis', 'cividis', 'twilight', 'twilight_shifted', 'turbo', 'Blues',"YlOrRd","YlOrRd_r",'Purples']

        self.slices_frame_counter = 0
        self.slices_frames = {}
        
        slice = LineString([[25496100, 6672150], [25496300, 6671800]])
        self.sl = Slice(self.airpoints, self.airdata, slice, "Tair")
        self.sl.set_resolution(7)
        self.sl.set_buffer(2)
        
        graph_frame = self.sl._create_plot(self)
        graph_frame.place(x=0, rely=0.4, relwidth=1, relheight=0.6) 
        
        main_left_config_frame = ctk.CTkFrame(self, fg_color='grey95', corner_radius=0)
        main_left_config_frame.place(x=0, y=0, relwidth=0.5, relheight=0.4)
        
        left_config_frame = ctk.CTkFrame(main_left_config_frame, fg_color='grey90')
        left_config_frame.pack(fill='both', expand=True, pady=4, padx=4)
        
        #left_config_frame.grid_rowconfigure(0, weight=1)  # configure grid system
        left_config_frame.grid_columnconfigure(0, weight=1)
        left_config_frame.grid_columnconfigure(1, weight=1)
        
        # change figure settings 
        left_config_label = ctk.CTkLabel(left_config_frame, text='Choose results:')
        left_config_label.grid(row=0,column=0, sticky="W", pady=(4,0),padx=4)
        
        self.left_config_dropdown = ctk.CTkComboBox(left_config_frame, width=180, values=['UTCI', 'Tair'], border_width=0)
        self.left_config_dropdown.grid(row=0,column=1, sticky="W", pady=(4,0),padx=4)
        
        left_config_label2 = ctk.CTkLabel(left_config_frame, text='Configure Graph look:')
        left_config_label2.grid(row=1,column=0,columnspan=2, sticky="W", pady=(0,4),padx=4)
        
        self.hide_legend_checkbox_var = ctk.IntVar(value=1)
        self.hide_legend_checkbox = ctk.CTkCheckBox(left_config_frame, text='Colorbar', border_width=1.5, variable=self.hide_legend_checkbox_var,onvalue=1,offvalue=0,command=self.on_hide_legend_check)
        self.hide_legend_checkbox.grid(row=2, column=0, sticky="W", pady=(0,4),padx=4)
        
        self.color_combobox = ctk.CTkComboBox(left_config_frame, values=self.colormaps, border_width=0, state="readonly", command=self.on_cmap_change)
        self.color_combobox.grid(row=2,column=1, sticky="W", pady=(4,0),padx=4)
        self.color_combobox.set(self.current_cmap) 
        
        self.title_checkbox_var = ctk.IntVar(value=1)
        self.title_checkbox = ctk.CTkCheckBox(left_config_frame, text='Title:', border_width=1.5, variable=self.title_checkbox_var,onvalue=1,offvalue=0,command=self.on_title_check)
        self.title_checkbox.grid(row=3,column=0, sticky="W", pady=(0,4),padx=4)

        self.axis_checkbox_var = ctk.IntVar(value=1)
        self.axis_checkbox_var = ctk.CTkCheckBox(left_config_frame, text='Axis names', border_width=1.5, variable=self.axis_checkbox_var,onvalue=1,offvalue=0,command=self.on_axis_check)
        self.axis_checkbox_var.grid(row=2, column=1, sticky="E", pady=4,padx=4)
                
        self.title_entry_var = ctk.StringVar()
        self.title_entry_var.trace_add("write", self.on_title_text_change)
        self.title_entry = ctk.CTkEntry(left_config_frame, border_width=0, textvariable=self.title_entry_var)
        self.title_entry.grid(row=3,column=1, sticky="WE", pady=4,padx=4)
        self.title_entry.insert(0,"tair")        
        
        left_config_label3 = ctk.CTkLabel(left_config_frame, text='Resolution:')
        left_config_label3.grid(row=4,column=0, sticky="W", pady=2,padx=4)
        
        resultion_spinbox = Spinbox(left_config_frame,start_value = 7, min_value = 0, max_value = 12, step_size=1, command = self.on_resolution_change )
        resultion_spinbox.grid(row=4,column=0, sticky="E", pady=2,padx=4)
        
        left_config_label4 = ctk.CTkLabel(left_config_frame, text='Buffer:')
        left_config_label4.grid(row=4,column=1, sticky="W", pady=2,padx=4)
        
        buffer_spinbox = Spinbox(left_config_frame,start_value = 7, min_value = 0, max_value = 12, step_size=1, command = self.on_buffer_change )
        buffer_spinbox.grid(row=4,column=1, sticky="E", pady=2,padx=4)
        
        slider_frame = ctk.CTkFrame(left_config_frame)
        slider_frame.grid(row=5, column=0, columnspan=2, sticky="WE", pady=(2,0),padx=4)
        
        left_config_label5 = ctk.CTkLabel(slider_frame, text='1')
        left_config_label5.pack(side='left', padx=(4,0))
        
        timestep_slider = ctk.CTkSlider(slider_frame, from_=0, to=24, number_of_steps=24, command=self.on_slider_change)
        timestep_slider.pack(side='left', fill='x', expand=True)
        
        left_config_label6 = ctk.CTkLabel(slider_frame, text='24')
        left_config_label6.pack(side='left', padx=(0,4))
                       
        main_right_config_frame = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        main_right_config_frame.place(relx=0.5, y=0, relwidth=0.5, relheight=0.4)
        
        right_config_frame = ctk.CTkFrame(main_right_config_frame, fg_color='grey90')
        right_config_frame.pack(fill='both', expand=True, pady=4, padx=4)

        right_config_frame.grid_columnconfigure(0, weight=1)
        right_config_frame.grid_columnconfigure(1, weight=1)

        right_config_label = ctk.CTkLabel(right_config_frame, text='Slices:')
        right_config_label.grid(row=0, column=0, sticky="W", pady=(0,4),padx=4)        
        
        self.slices_frame = SizedScrollableFrame(right_config_frame, height=86)
        self.slices_frame.grid(row=2,column=0,columnspan=2,rowspan=2, sticky="WE", pady=(0,4),padx=4)
        
        self.radio_var = ctk.StringVar(value="Area A") 
        
        self.create_slice_frame("Slice 1")
        self.create_slice_frame('Slice 2')
        
        right_config_label = ctk.CTkLabel(right_config_frame, text='Export Settings:')
        right_config_label.grid(row=4, column=0, sticky="W", pady=(0,4),padx=4)
        
        self.transparent_figure_var = ctk.IntVar(value=0)
        self.transparent_figure = ctk.CTkCheckBox(right_config_frame, text='Transparent figure', border_width=1.5, variable=self.transparent_figure_var, onvalue=1, offvalue=0, command=self.on_transparent_figure_check)
        self.transparent_figure.grid(row=5,column=0, sticky="W", pady=(0,4),padx=4) 

        self.figure_color_combobox = ctk.CTkComboBox(right_config_frame, border_width=0, width= 92)
        self.figure_color_combobox.grid(row=5,column=0, sticky="E", pady=(0,4),padx=4) 
        self.figure_color_combobox.set('#FFFFFF')
        self.figure_color_combobox.configure(fg_color='#FFFFFF')
        figure_combobox_colorpicker = CustomColorPicker(self.figure_color_combobox)
        figure_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.figure_color_combobox: self.on_figure_change_color(entry))
        
        self.transparent_graph_var = ctk.IntVar(value=0)
        self.transparent_graph = ctk.CTkCheckBox(right_config_frame, text='Transparent graph', border_width=1.5, variable=self.transparent_graph_var, onvalue=1, offvalue=0, command=self.on_transparent_graph_check)
        self.transparent_graph.grid(row=5,column=1, sticky="W", pady=(0,4),padx=4)     
                   
        self.graph_color_combobox = ctk.CTkComboBox(right_config_frame, border_width=0, width= 92)
        self.graph_color_combobox.grid(row=5,column=1, sticky="E", pady=(0,4),padx=4) 
        self.graph_color_combobox.set('#FFFFFF')
        self.graph_color_combobox.configure(fg_color='#FFFFFF')
        graph_combobox_colorpicker = CustomColorPicker(self.graph_color_combobox)
        graph_combobox_colorpicker.bind("<<ColorPickerColorSelected>>", lambda event, entry=self.graph_color_combobox: self.on_graph_change_color(entry))
  
    def create_slice_frame(self, placeholder):
        frame = ctk.CTkFrame(self.slices_frame.scrollable_frame)
        frame.pack(side='top', fill='x')
 
        slice_frame_checkbox = ctk.CTkRadioButton(frame, text=placeholder, variable=self.radio_var, value=placeholder, command=self.on_radio_select) 
        slice_frame_checkbox.pack(side='left', pady=2, padx=2) 
        
        # slice_frame_entry = ctk.CTkEntry(frame, border_width=0)     
        # slice_frame_entry.pack(side='left', pady=2, padx=2)
        # slice_frame_entry.bind("<KeyRelease>", lambda event, frame_id=self.slices_frame_counter, entry=slice_frame_entry: self.on_sim_frame_name_change(frame_id, entry))
        # slice_frame_entry.insert(0,placeholder)
        
        self.slices_frames[self.slices_frame_counter] = {
                "frame_id": self.slices_frame_counter,
                "frame": frame,
                "sim_name": placeholder,           
        }       
            
    def on_radio_select(self):
        selected_area = self.radio_var.get()
        #selected_area = selected_area.replace('Area ', '')
        #self.selected_area_order  = self.char_to_alphabet_order(selected_area)
        print(selected_area)
        
    def on_slider_change(self, value):
        print(value)
    
    def on_resolution_change(self, value):
        print(value)  
        
    def on_buffer_change(self,value):
        print(value)     
        
    def on_cmap_change(self, event):
        self.sl.set_new_cmap(self.color_combobox.get())            
        
    def on_title_check(self):
        if self.title_checkbox_var.get() == 1:
            self.title_entry.configure(state='normal')
            self.sl.set_new_title(self.title_entry.get())

        else:
            self.title_entry.configure(state='disabled')
            self.sl.remove_title()
            
    def on_title_text_change(self, *args):
        self.sl.set_new_title(self.title_entry_var.get())
        
    def on_hide_legend_check(self):
        if self.hide_legend_checkbox_var.get() == 1:
            self.sl.set_new_colorbar()
        else:
            self.sl.remove_colorbar()
            
    def on_axis_check(self):
        if self.axis_checkbox_var.get() == 1:
            self.sl.set_axis()
        else:
            self.sl.remove_axis()       

    def on_transparent_figure_check(self):    
        if self.transparent_figure_var.get() == 1:
            self.figure_color_combobox.configure(state='disabled')
        else:
            self.figure_color_combobox.configure(state='normal')
            
    def on_figure_change_color(self,entry):
        color = entry.get()
        entry.configure(fg_color= color)         
        
    def on_transparent_graph_check(self):
        if self.transparent_graph_var.get() == 1:
            self.graph_color_combobox.configure(state='disabled') 
        else:
            self.graph_color_combobox.configure(state='normal')
                       
    def on_graph_change_color(self, entry):                
        color = entry.get()
        entry.configure(fg_color= color)  


class Notebook(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)  # Initialize the parent class
        
        
        self.parent = parent
        
        # Customising the treeview because there is no 
        selected_tab_color = self.parent._apply_appearance_mode(ctk.ThemeManager.theme["CTk"]["fg_color"])
        tabview_background = self.parent._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        unselected_tab_color = self.parent._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])
        
        
        tabstyle = ttk.Style()
        tabstyle.theme_use('default')
        tabstyle.configure("TNotebook", background=tabview_background, fieldbackground=unselected_tab_color, borderwidth=0)

        
        tabstyle.configure('TNotebook.Tab', font=('Helvetica', 12), borderwidth=0)
        tabstyle.map('TNotebook.Tab', background=[('selected', selected_tab_color)])
        tabstyle.configure("TNotebook.Tab", padding=[28, 6])
        
        
        
        self.tab_frame1 = TimeSeriesRes(self, self.parent.surfpoints, self.parent.airpoints, self.parent.surfmesh, self.parent.surfdata, self.parent.airdata)
        self.add(self.tab_frame1, text='Simulation Time Series') 
        
        self.tab_frame2 = SimResRes(self, self.parent.surfpoints, self.parent.surfdata, self.parent.aoi)
        self.add(self.tab_frame2, text='Simulation Result')
        
        self.tab_frame3 = SimCompRes(self, self.parent.surfpoints, self.parent.surfdata, self.parent.aoi, self.parent.sims)
        self.add(self.tab_frame3, text='Simulation Comaprison')
        
        self.tab_frame4 = UTCICategoryRes(self, self.parent.surfpoints, self.parent.surfdata, self.parent.surfmesh)
        self.add(self.tab_frame4, text='UTCI Category')
        
        self.tab_frame5 = WindRoseRes(self, self.parent.airpoints, self.parent.airdata)
        self.add(self.tab_frame5, text='Windrose')
        
        self.tab_frame6 = SliceRes(self, self.parent.airpoints, self.parent.airdata)
        self.add(self.tab_frame6, text='Slices')

        

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color = "gray95")
        
        self.surfpoints = gpd.read_file("data/surface_point_SHP.shp")
        self.airpoints = gpd.read_file("data/air_point_SHP.shp")
        self.surfmesh = gpd.read_file("data/surface_triangle_SHP.shp")
        self.surfdata = pd.read_csv("data/surface_data_2021_07_15.csv")
        self.airdata = pd.read_csv("data/air_data_2021_07_15.csv")

        surfdata2 = self.surfdata.copy()
        surfdata2["Tair"] = [x + 2 for x in self.surfdata["Tair"].values]
        surfdata2["UTCI"] = [x + 2 for x in self.surfdata["UTCI"].values]

        aoi1 = Polygon(((25496100, 6672050), (25496115, 6672000), (25496215, 6672070), (25496190, 6672100), (25496100, 6672050)))
        aoi2 = Polygon(((25496200, 6672050), (25496215, 6672000), (25496315, 6672070), (25496290, 6672100), (25496200, 6672050)))
        aoi3 = Polygon(((25496100, 6671900), (25496170, 6671800), (25496200, 6671820), (25496160, 6671900), (25496100, 6671900)))
        aoi4 = Polygon(((25496200, 6671950), (25496220, 6671850), (25496300, 6671820), (25496260, 6671950), (25496200, 6671950)))

        self.aoi = [aoi1,aoi2,aoi3,aoi4]
        
        self.sims = [self.surfdata, surfdata2]
        
        # main setup
        self.title('Solene Pre-Proccesing')
        self.geometry('1000x600')
        self.minsize(600,600)
        #ctk.set_default_color_theme("dark-blue.json")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
 
        self.notebook = Notebook(self)
        self.notebook.pack(side='top', fill='both', expand=True)
        
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(side='top', fill='x')
        
        export_button = ctk.CTkButton(bottom_frame, text='Export', width=80)
        export_button.pack(side='right',pady=2,padx=2)
        
        back_button = ctk.CTkButton(bottom_frame, text='Back', width=80)
        back_button.pack(side='left',pady=2,padx=2)
        
    def on_closing(self):
        # Close all matplotlib figures
        plt.close('all')
        # Quit and destroy the Tkinter application
        self.quit()
        self.destroy()
 
 
    def mainloop(self):
        super().mainloop()













        
if __name__ == "__main__":
    app = App() 
    app.mainloop()  
    # Instantiate