import customtkinter as ctk
from tkinter import filedialog

import pandas as pd

from collections import defaultdict
from dataclasses import dataclass, field


class SizedScrollableFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.place(x=0, y=0, anchor="nw", relwidth=1, relheight=1)


class AoI(ctk.CTkFrame):
    def __init__(self, master, number):
        super().__init__(master, fg_color='grey80')   
        self.pack(side="top", fill="x", padx=4, pady=2)
        
        self.frame_key = number
        
        
        self.check_var = ctk.StringVar(value="on") 
        aoi_checkbox = ctk.CTkCheckBox(self, text=f'Area {self.frame_key}',border_width = 2,variable=self.check_var, onvalue="on", offvalue="off")
        aoi_checkbox.pack(side='left', padx=8, pady=2)        
        
        self.aoi_result_entry = ctk.CTkEntry(self, width=280, border_width=0)
        self.aoi_result_entry.pack(side='left', fill='x', padx=8, pady=2)

    def insert_data(self,data):
        self.aoi_result_entry.insert(0,data)
        
    def get_state(self):
        """Return the state of the AoI frame."""
        return {
            "is_checked": self.check_var.get() == "on",
            "text": self.aoi_result_entry.get()
        }
       
        
class SliceFrame(ctk.CTkFrame):
    def __init__(self, master, number):
        super().__init__(master, fg_color='grey80')   
        self.pack(side="top", fill="x", padx=4, pady=2)
        
        self.frame_key = number
        
        
        self.check_var = ctk.StringVar(value="on") 
        slice_checkbox = ctk.CTkCheckBox(self, text=f'Slice {self.frame_key}',border_width = 2,variable=self.check_var, onvalue="on", offvalue="off")
        slice_checkbox.pack(side='left', padx=8, pady=2)        
        
        self.slice_result_entry = ctk.CTkEntry(self, width=280, border_width=0)
        self.slice_result_entry.pack(side='left', fill='x', padx=8, pady=2)

    def insert_data(self,data):
        self.slice_result_entry.insert(0,data)
        
    def get_state(self):
        """Return the state of the AoI frame."""
        return {
            "is_checked": self.check_var.get() == "on",
            "text": self.slice_result_entry.get()
        }       
        
        
class DataFrame(ctk.CTkFrame):
    def __init__(self, master, number):
        super().__init__(master, fg_color='grey80')
        self.pack(side="top", fill="x", padx=4, pady=2)
        
        dataframe_label = ctk.CTkLabel(self, text=f'Dataframe {number}:')  
        dataframe_label.pack(side="left",padx=8, pady=2 )
        
        self.dataframe_entry = ctk.CTkEntry(self, width=280, border_width=0)
        self.dataframe_entry.pack(side="left", padx=(8,4), pady=2)
        
        dataframe_browse_button = ctk.CTkButton(self, text='Browse', width=80, command=self.on_browse)
        dataframe_browse_button.pack(side='left', pady=2 )
        
    def on_browse(self):
        file_path = filedialog.askopenfilename(title="Select a File", 
                                            filetypes=[("csv files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.dataframe_entry.insert(0, file_path)   
        else:
            print("File not selected")
            
    def get_state(self):
        """Return the state of the AoI frame."""
        return {
            "path": self.dataframe_entry.get()
        }
        
    def insert_data(self, input):
        self.dataframe_entry.insert(0,input)
        
@dataclass
class VariableState:
    is_checked: bool
    value: str = "off"


class SimTimeSeries(ctk.CTkFrame):
    def __init__(self, parent, var_list_input):
        super().__init__(parent)
        
        self.checkboxes = [] 
        self.var_list = var_list_input
        
        self.variables = defaultdict(VariableState)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        sim_time_series_label = ctk.CTkLabel(self, text="Simulation Time Series", font=("Arial", 14, "bold"))
        sim_time_series_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        sim_time_series_label2 = ctk.CTkLabel(self, text="Variables:")
        sim_time_series_label2.grid(row=1,column =0, sticky='W', padx=4, pady=2)
        
        self.select_all_var = ctk.StringVar(value="off")
        select_all_checkbox = ctk.CTkCheckBox(
            self,
            text="Select All",
            variable=self.select_all_var,
            border_width=2,
            onvalue="on",
            offvalue="off",
            command=self.toggle_all_checkboxes
        )
        select_all_checkbox.grid(row=1, column=1, sticky='E', padx=4)

        row = 2  # Starting row for checkboxes
        column = 0  # Starting column for checkboxes
        
        for header in self.var_list:
            self.add_checkbox(header, header, row, column)
            
            # Move to the next column or row as needed
            column += 1
            if column > 1:  # Move to the next row after 2 columns
                column = 0
                row += 1
        
        sim_time_series_label3 = ctk.CTkLabel(self, text="Areas of Intrest:")
        sim_time_series_label3.grid(row=5,column =0, sticky='W', padx=4) 
        
        self.winter_checkbox_var = ctk.IntVar(value=0)
        winter_checkbox = ctk.CTkCheckBox(self, text='Winter Time series',border_width = 2,variable=self.winter_checkbox_var, onvalue=1, offvalue=0, command= self.on_winter_check)
        winter_checkbox.grid(row=7,column=0,sticky='W', padx=4, pady=(0,2))
        
        self.winter_time_series = WinterTimeSeries(self)
 
        
    def add_checkbox(self, text, var_key, row, column):
        """Helper function to add a checkbox tied to a variable state."""
        self.variables[var_key] = VariableState(is_checked=False)
        var = ctk.StringVar(value="off")
        checkbox = ctk.CTkCheckBox(
            self,
            text=text,
            border_width=2,
            variable=var,
            onvalue="on",
            offvalue="off",
            command=lambda: self.update_variable_state(var_key, var)
        )
        checkbox.grid(row=row, column=column, sticky='W', padx=4, pady=2)
        self.checkboxes.append((var_key, var, checkbox))


    def update_variable_state(self, var_key, var):
        """Update the state of a variable when the checkbox is toggled."""
        self.variables[var_key].is_checked = var.get() == "on"
        self.variables[var_key].value = var.get()
        
        
    def on_winter_check(self):
        if self.winter_checkbox_var.get() == 1:
            self.winter_time_series.grid(row=8, column=0, columnspan=2, sticky="NSWE",padx=4, pady=(0,2))
            
        else:
            self.winter_time_series.grid_forget()
 
    def toggle_all_checkboxes(self):
        """Toggle all checkboxes based on the "Select All" checkbox."""
        select_all_state = self.select_all_var.get() == "on"
        for var_key, var, checkbox in self.checkboxes:
            var.set("on" if select_all_state else "off")
            self.update_variable_state(var_key, var) 
 
    def get_all_data(self):
        """Retrieve and print all data (checkboxes and AoI frames)."""
        # Collect checkbox data
        checkbox_data = {key: vars(state) for key, state in self.variables.items()}
        
        # Combine the data into a dictionary
        all_data = {
            "checkboxes": checkbox_data,
        }
        
        # Print the data
        print("All Data in all time series:")
        for section, data in all_data.items():
            print(f"{section.capitalize()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    print(f"  Frame {i + 1}: {item}")
        return all_data 
      

class WinterTimeSeries(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        winter_time_series_label = ctk.CTkLabel(self, text="Winter Time series", font=("Arial", 14, "bold"))
        winter_time_series_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        winter_time_series_label2 = ctk.CTkLabel(self, text="Variables:")
        winter_time_series_label2.grid(row=1,column=0, sticky='W', padx=4,pady=(4,0))    
             
        # _checkbox = ctk.CTkCheckBox(self, text='')
        # _checkbox.grid(row=,column=,sticky='W') 
        
        check_var_2 = ctk.StringVar(value="on")
        tair_checkbox = ctk.CTkCheckBox(self, text='Air Temperature',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        tair_checkbox.grid(row=2,column=0,sticky='W', padx=4)
        
        check_var_2 = ctk.StringVar(value="on")
        winter_checkbox = ctk.CTkCheckBox(self, text='Wind',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        winter_checkbox.grid(row=2,column=1,sticky='W', padx=4) 
        
        winter_time_series_label3 = ctk.CTkLabel(self, text="Airpoints:")
        winter_time_series_label3.grid(row=3,column=0, sticky='W', padx=4,pady=(4,0))
        
        # check if found within the ferda directory
        airpoints = ctk.CTkEntry(self, border_width=0)
        airpoints.grid(row=3,column=1, sticky='WE', padx=4, pady=4)
 
               
class SimulationResults(ctk.CTkFrame):
    def __init__(self, parent, var_list_input):
        super().__init__(parent)
        
        self.variables = defaultdict(VariableState)
        self.aoi_frames_list = []
        self.checkboxes = []
        self.var_list = var_list_input 

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        sim_results_label = ctk.CTkLabel(self, text="Simulation Results", font=("Arial", 14, "bold"))
        sim_results_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        sim_results_label2 = ctk.CTkLabel(self, text="Variables:")
        sim_results_label2.grid(row=1,column =0, sticky='W', padx=4)
        
        self.select_all_var = ctk.StringVar(value="off")
        select_all_checkbox = ctk.CTkCheckBox(
            self,
            text="Select All",
            variable=self.select_all_var,
            border_width=2,
            onvalue="on",
            offvalue="off",
            command=self.toggle_all_checkboxes
        )
        select_all_checkbox.grid(row=1, column=1, sticky='E', padx=4)
        
        row = 2  # Starting row for checkboxes
        column = 0  # Starting column for checkboxes
        
        for header in self.var_list:
            self.add_checkbox(header, header, row, column)
            
            # Move to the next column or row as needed
            column += 1
            if column > 1:  # Move to the next row after 2 columns
                column = 0
                row += 1
        

        
        sim_results_label3 = ctk.CTkLabel(self, text="Areas of Intrest:")
        sim_results_label3.grid(row=5,column =0, sticky='W', padx=4) 
        
        # sized scrollbar for with frames of the ares of intrest and checkboxes 
        self.aoi_frames = SizedScrollableFrame(self, height=80)
        self.aoi_frames.grid(row=6, column =0, columnspan=2, sticky='WE', padx=4, pady=4)      


        
    def set_aoi_frames(self, aoi_list):
        for i in range(len(aoi_list)):
            aoi_frame = AoI(self.aoi_frames.scrollable_frame, i +1)
            aoi_frame.insert_data(aoi_list[i])  
            self.aoi_frames_list.append(aoi_frame)

    def get_aoi_frames_state(self):
        """Get the state of all AoI frames."""
        return [aoi_frame.get_state() for aoi_frame in self.aoi_frames_list]

    def add_checkbox(self, text, var_key, row, column):
        """Helper function to add a checkbox tied to a variable state."""
        self.variables[var_key] = VariableState(is_checked=False)
        var = ctk.StringVar(value="off")
        checkbox = ctk.CTkCheckBox(
            self,
            text=text,
            border_width=2,
            variable=var,
            onvalue="on",
            offvalue="off",
            command=lambda: self.update_variable_state(var_key, var)
        )
        checkbox.grid(row=row, column=column, sticky='W', padx=4, pady=2)
        self.checkboxes.append((var_key, var, checkbox))

    def update_variable_state(self, var_key, var):
        """Update the state of a variable when the checkbox is toggled."""
        self.variables[var_key].is_checked = var.get() == "on"
        self.variables[var_key].value = var.get()
        
    def toggle_all_checkboxes(self):
        """Toggle all checkboxes based on the "Select All" checkbox."""
        select_all_state = self.select_all_var.get() == "on"
        for var_key, var, checkbox in self.checkboxes:
            var.set("on" if select_all_state else "off")
            self.update_variable_state(var_key, var)

    def get_all_data(self):
        """Retrieve and print all data (checkboxes and AoI frames)."""
        # Collect checkbox data
        checkbox_data = {key: vars(state) for key, state in self.variables.items()}
        
        # Combine the data into a dictionary
        all_data = {
            "checkboxes": checkbox_data,
            "aoi_frames": self.get_aoi_frames_state()
        }
        
        # Print the data
        print("All Data in simulation result:")
        for section, data in all_data.items():
            print(f"{section.capitalize()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    print(f"  Frame {i + 1}: {item}")
        return all_data


class SimulationComparison(ctk.CTkFrame):
    def __init__(self, parent, var_list_input):
        super().__init__(parent)

        self.no_of_dataframes = 0
        self.list_of_dataframes = {}
        
        self.aoi_frames_list = []
        self.checkboxes = [] 
        self.var_list = var_list_input
        
        self.variables = defaultdict(VariableState)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        sim_comparison_label = ctk.CTkLabel(self, text="Simulation Comparison", font=("Arial", 14, "bold"))
        sim_comparison_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        sim_comparison_label2 = ctk.CTkLabel(self, text="Variables:")
        sim_comparison_label2.grid(row=1,column =0, sticky='W', padx=4)
        
        self.select_all_var = ctk.StringVar(value="off")
        select_all_checkbox = ctk.CTkCheckBox(
            self,
            text="Select All",
            variable=self.select_all_var,
            border_width=2,
            onvalue="on",
            offvalue="off",
            command=self.toggle_all_checkboxes
        )
        select_all_checkbox.grid(row=1, column=1, sticky='E', padx=4)
        
        
        row = 2  # Starting row for checkboxes
        column = 0  # Starting column for checkboxes
        
        for header in self.var_list:
            self.add_checkbox(header, header, row, column)
            
            # Move to the next column or row as needed
            column += 1
            if column > 1:  # Move to the next row after 2 columns
                column = 0
                row += 1
        
        sim_comparison_label3 = ctk.CTkLabel(self, text="DataFrames:")
        sim_comparison_label3.grid(row=5,column =0, sticky='W', padx=4) 
                
        dataframe_add_button = ctk.CTkButton(self, text='Add', width=80, command=self.set_dataframes)
        dataframe_add_button.grid(row=5,column =1, sticky='E', padx=4) 
        
        self.dataframes_frame = SizedScrollableFrame(self, height = 80, fg_color='grey80')
        self.dataframes_frame.grid(row=6, column =0, columnspan=2, sticky='WE', padx=4, pady=4)
        
        sim_comparison_label4 = ctk.CTkLabel(self, text="Areas of Intrest:")
        sim_comparison_label4.grid(row=7,column =0, sticky='W', padx=4) 
        
        # sized scrollbar for with frames of the ares of intrest and checkboxes 
        self.aoi_frames = SizedScrollableFrame(self, height=80)
        self.aoi_frames.grid(row=8, column =0, columnspan=2, sticky='WE', padx=4, pady=4) 
        
        self.set_dataframes()
     
    def set_dataframes(self):
        self.no_of_dataframes +=1
        data_frame = DataFrame( self.dataframes_frame.scrollable_frame, self.no_of_dataframes)
        self.list_of_dataframes[self.no_of_dataframes] = data_frame

    def set_existing_dataframes(self, input_list):
        # remove the widgets from set_dataframes
        for widget in self.dataframes_frame.scrollable_frame.winfo_children():
            widget.destroy()  # Destroy each widget inside the container
        self.list_of_dataframes.clear()  # Clear the dictionary
        self.no_of_dataframes = 0  # Reset the counter    
        # insert the data from the input ferda file    
        for i in range(len(input_list)):
            self.no_of_dataframes +=1
            data_frame = DataFrame( self.dataframes_frame.scrollable_frame, self.no_of_dataframes)
            data_frame.insert_data(input_list[i])
            self.list_of_dataframes[self.no_of_dataframes] = data_frame
        
    def get_dataframes_state(self):
        """Get the state of all DataFrame objects."""
        return {key: df.get_state() for key, df in self.list_of_dataframes.items()}
        
    def set_aoi_frames(self, aoi_list):
        for i in range(len(aoi_list)):
          aoi_frame = AoI(self.aoi_frames.scrollable_frame, i +1)
          aoi_frame.insert_data(aoi_list[i])
          self.aoi_frames_list.append(aoi_frame)

    def get_aoi_frames_state(self):
        """Get the state of all AoI frames."""
        return [aoi_frame.get_state() for aoi_frame in self.aoi_frames_list]
          
    def add_checkbox(self, text, var_key, row, column):
        """Helper function to add a checkbox tied to a variable state."""
        self.variables[var_key] = VariableState(is_checked=False)
        var = ctk.StringVar(value="off")
        checkbox = ctk.CTkCheckBox(
            self,
            text=text,
            border_width=2,
            variable=var,
            onvalue="on",
            offvalue="off",
            command=lambda: self.update_variable_state(var_key, var)
        )
        checkbox.grid(row=row, column=column, sticky='W', padx=4, pady=2)
        self.checkboxes.append((var_key, var, checkbox))

    def toggle_all_checkboxes(self):
        """Toggle all checkboxes based on the "Select All" checkbox."""
        select_all_state = self.select_all_var.get() == "on"
        for var_key, var, checkbox in self.checkboxes:
            var.set("on" if select_all_state else "off")
            self.update_variable_state(var_key, var)

    def update_variable_state(self, var_key, var):
        """Update the state of a variable when the checkbox is toggled."""
        self.variables[var_key].is_checked = var.get() == "on"
        self.variables[var_key].value = var.get()

    def get_all_data(self):
        """Retrieve and print all data (checkboxes and AoI frames)."""
        # Collect checkbox data
        checkbox_data = {key: vars(state) for key, state in self.variables.items()}
        
        # Combine the data into a dictionary
        all_data = {
            "checkboxes": checkbox_data,
            "aoi_frames": self.get_aoi_frames_state(),
            "dataframes": self.get_dataframes_state()
        }
        
        # Print the data
        print("All Data in simualtion comparison:")
        for section, data in all_data.items():
            print(f"{section.capitalize()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    print(f"  Frame {i + 1}: {item}")
        return all_data


# class Airflow(ctk.CTkFrame):
#     def __init__(self, parent):
#         super().__init__(parent)
        
#         self.variables = defaultdict(VariableState)

#         self.grid_columnconfigure(0, weight=1)
#         self.grid_columnconfigure(1, weight=1)
        
#         Airflow_label = ctk.CTkLabel(self, text="WindFlow", font=("Arial", 14, "bold"))
#         Airflow_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))

#         Airflow_label3 = ctk.CTkLabel(self, text="To Be Figured out")
#         Airflow_label3.grid(row=1,column=0, sticky='W', padx=4,pady=(4,0))                            


class Windrose(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.variables = defaultdict(VariableState)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        windrose_label = ctk.CTkLabel(self, text="Windrose", font=("Arial", 14, "bold"))
        windrose_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))

        windrose_label3 = ctk.CTkLabel(self, text="Airpoints:")
        windrose_label3.grid(row=1,column=0, sticky='W', padx=4,pady=(4,0))
        
        # check if found within the ferda directory
        airpoints = ctk.CTkEntry(self, border_width=0)
        airpoints.grid(row=1,column=1, sticky='WE', padx=4, pady=4)
        
        windrose_label3 = ctk.CTkLabel(self, text="Airdata:")
        windrose_label3.grid(row=2,column=0, sticky='W', padx=4,pady=(4,0))
        
        # check if found within the ferda directory
        airpoints = ctk.CTkEntry(self, border_width=0)
        airpoints.grid(row=2,column=1, sticky='WE', padx=4, pady=4)
 
        
class Slices(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)       
        
        self.variables = defaultdict(VariableState)     
        self.slice_frames_list = []
        self.checkboxes = []         

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        slice_results_label = ctk.CTkLabel(self, text="Slices", font=("Arial", 14, "bold"))
        slice_results_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        slice_results_label2 = ctk.CTkLabel(self, text="Variables:")
        slice_results_label2.grid(row=1,column =0, sticky='W', padx=4)
        
        self.select_all_var = ctk.StringVar(value="off")
        select_all_checkbox = ctk.CTkCheckBox(
            self,
            text="Select All",
            variable=self.select_all_var,
            border_width=2,
            onvalue="on",
            offvalue="off",
            command=self.toggle_all_checkboxes
        )
        select_all_checkbox.grid(row=1, column=1, sticky='E', padx=4)
       
        
        self.add_checkbox("Air Temperature", "air_temp", row=2, column=0)
        self.add_checkbox("Surface Temperature", "surface_temp", row=2, column=1)

        self.slices_frames = SizedScrollableFrame(self, height=80)
        self.slices_frames.grid(row=6, column =0, columnspan=2, sticky='WE', padx=4, pady=4)      
        
    def set_slices_frames(self, slice_list):
        for i in range(len(slice_list)):
          slices_frame = SliceFrame(self.slices_frames.scrollable_frame, i+1)
          slices_frame.insert_data(slice_list[i]) 
          self.slice_frames_list.append(slices_frame)        

    def get_slices_frames_state(self):
        """Get the state of all AoI frames."""
        return [slice_frame.get_state() for slice_frame in self.slice_frames_list]


    def toggle_all_checkboxes(self):
        """Toggle all checkboxes based on the "Select All" checkbox."""
        select_all_state = self.select_all_var.get() == "on"
        for var_key, var, checkbox in self.checkboxes:
            var.set("on" if select_all_state else "off")
            self.update_variable_state(var_key, var)

        
    def add_checkbox(self, text, var_key, row, column):
        """Helper function to add a checkbox tied to a variable state."""
        self.variables[var_key] = VariableState(is_checked=False)
        var = ctk.StringVar(value="off")
        checkbox = ctk.CTkCheckBox(
            self,
            text=text,
            border_width=2,
            variable=var,
            onvalue="on",
            offvalue="off",
            command=lambda: self.update_variable_state(var_key, var)
        )
        checkbox.grid(row=row, column=column, sticky='W', padx=4, pady=2)
        self.checkboxes.append((var_key, var, checkbox))

    def update_variable_state(self, var_key, var):
        """Update the state of a variable when the checkbox is toggled."""
        self.variables[var_key].is_checked = var.get() == "on"
        self.variables[var_key].value = var.get()
        
    def get_all_data(self):
        """Retrieve and print all data (checkboxes and AoI frames)."""
        # Collect checkbox data
        checkbox_data = {key: vars(state) for key, state in self.variables.items()}
        
        # Combine the data into a dictionary
        all_data = {
            "checkboxes": checkbox_data,
            "aoi_frames": self.get_slices_frames_state(),
        }
        
        # Print the data
        print("All Data in slices variables:")
        for section, data in all_data.items():
            print(f"{section.capitalize()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    print(f"  Frame {i + 1}: {item}")
        return all_data

    
class VariableConfigure(ctk.CTkFrame):
    def __init__(self, master, c0,c2,c3,c4,c5,c6):
        super().__init__(master, fg_color='transparent')
        
        self.aoi_list = []
        self.var_list = []
        
        self.simulation_comparison = None
        
        self.simulation_time_series_checkbox,self.simulation_result_checkbox,self.simulation_comparison_checkbox, self.slices_checkbox, self.windrose_checkbox = c0, c2, c3, c4, c6
        
    def iniate_varconfig(self):    
        
        mainframe = ctk.CTkScrollableFrame(self, fg_color='transparent')
        mainframe.pack(side='top', fill='both', expand= True)
        
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(side='top', fill='x', padx=4, pady=4)
        
        self.run_button = ctk.CTkButton(bottom_frame, text="Run", width=80, command=self.on_run)
        self.run_button.pack(side='right', padx=4, pady=4)
        
        self.back_button = ctk.CTkButton(bottom_frame, text='Back', width=80)
        self.back_button.pack(side='right', padx=4, pady=4)
        
        #the following frames are for the the selected frames
        if self.simulation_time_series_checkbox == 'on':
            self.simulation_time_series = SimTimeSeries(mainframe, self.var_list)
            self.simulation_time_series.pack(side='top', fill='x', padx=4, pady=4)
            
        if self.simulation_result_checkbox == 'on':
            self.simulation_results = SimulationResults(mainframe, self.var_list)
            self.simulation_results.pack(side='top', fill='x', padx=4, pady=4)

        if self.simulation_comparison_checkbox == 'on':
            self.simulation_comparison = SimulationComparison(mainframe, self.var_list)
            self.simulation_comparison.pack(side='top', fill='x', padx=4, pady=4)
                
        if self.slices_checkbox == 'on':
            self.slices = Slices(mainframe)
            self.slices.pack(side='top', fill='x', padx=4, pady=4)
           
        # if c5 == 'on':
        #     air_flow = Airflow(mainframe)
        #     air_flow.pack(side='top', fill='x', padx=4, pady=4)
            
        if self.windrose_checkbox == 'on':
            windrose = Windrose(mainframe)
            windrose.pack(side='top', fill='x', padx=4, pady=4)

        # NO UTCI

    def set_aoi(self, aoi):
        self.aoi_list = aoi
            
        if self.simulation_result_checkbox == 'on':
            self.simulation_results.set_aoi_frames(self.aoi_list)
            
        if self.simulation_comparison_checkbox == 'on':
            self.simulation_comparison.set_aoi_frames(self.aoi_list)
            
    def set_slices(self, slices_list):
        self.slices.set_slices_frames(slices_list)
        
    def set_paths(self, inputlist):
        self.simulation_comparison.set_existing_dataframes(inputlist)
        
    def on_run(self):
        print("works")
        print(self.simulation_results.get_all_data())
        
    def set_var_list(self, csv_file):
        '''Input a csv file and get the header columns'''
        column_headers = csv_file.columns.tolist()[1:-1]
        self.var_list = column_headers