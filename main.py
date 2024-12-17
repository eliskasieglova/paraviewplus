
from tkinter import ttk
import customtkinter as ctk

import geopandas as gpd
import pandas as pd
import glob
import os

from gui.view import App
from gui.results import ResultWindow


'''
To do:

- done - make the ferda input main input
- done - change manual input to surface data
- done - automate the input
- add the airpoints and airdata to the time series
- done - make the header of slice and aoi picker bold
- either remove or vreate an export window
- remove windflow for the time being?
- add an error if not everythin is inputed 
- fix the sumbit button and creation of the sim_config frames
- make the line drawing more proffesional in aoi and where it follows the mouse motion
- lower the threshhold of the aoi slector
- fill the airdata and airpoints in case of ferda input
- make the variables checkboxes its own frame so its doesnt affect the other widgets
- put airdata and airpoints in windorse if ferda input was selected 
- mulitthread the program and add progress bar 
- add ticks to all slider
- fix the create plot of time series
- standarize the variables for input
- fix the change of the plots variables in sim res and comp
- fix the slices radiobutton
- fix the slices error that i am getting 
- fix the resolution and buffer for the slices
- lay down a plan for the geo file incorperation
- export button
- integrate with ferda 

-add graphic comaprison


- make the result gui
- done - add slicing in the area of intrest gui 
- add errors for the submit button
- add the filedialig for the ferda and the browse segments
- 

- done - add slices to aoi
- make the variable choosing more dynamic
- done - fix the coloring with the frames 
- 

- automate the variables input into the entire app

- done - clicking next on aoi saves the aoi list and sends it to variable frame same for slices 

'''

class Controller:
    def __init__(self):
        self.gui = App()  # Main view
        
        self.show_slicer = False
        self.show_aoi = False
            
        self.connect_events()

        self.gui.mainloop()  # Starts the GUI main loop


    def connect_events(self):
        self.gui.side_bar.submit_button.configure(command=self.on_submit)
        
    def on_submit(self):
        self.show_aoi = False
        selected_import_path = self.gui.side_bar.input_segmented_button.get()
        if selected_import_path == 'Browse':
            self.surfpoints = gpd.read_file(self.gui.side_bar.path_bar.get())
            self.surfmesh = gpd.read_file(self.gui.side_bar.path_bar2.get())
            self.surfdata = pd.read_csv(self.gui.side_bar.path_bar3.get())
        # ferda chosen
        else:
           # disect the ferda directory into files
            self.ferda_directory_path = self.gui.side_bar.ferda_path_bar.get()
            self.surfpoints = gpd.read_file(f"{self.ferda_directory_path}/surface_point_SHP.shp")
            self.surfmesh = gpd.read_file(f"{self.ferda_directory_path}/surface_triangle_SHP.shp")
            self.airpoints = gpd.read_file(f"{self.ferda_directory_path}/air_point_SHP.shp")
            
            # looks for any other simulations  
            files_in_directory = os.listdir(self.ferda_directory_path)    
            self.surface_matching_files = [os.path.join(self.ferda_directory_path, f) for f in files_in_directory if "surface_data" in f and f.endswith(".csv")]
            self.surfdata = pd.read_csv(self.surface_matching_files[0])
            
            # looks for the airdata automatically
            air_matching_files = glob.glob(os.path.join(self.ferda_directory_path, "*air_data*.csv"))
            air_file_to_load = air_matching_files[0]
            self.airdata = pd.read_csv(air_file_to_load)
        
        self.export_path = self.gui.side_bar.export_path_bar.get()
       
           #Simulation result                             #Simulation Comparison
        if self.gui.side_bar.check_var_2.get() == 'on' or self.gui.side_bar.check_var_3.get() == 'on':
            self.show_aoi = True       
         
        # Slices   
        if self.gui.side_bar.check_var_4.get() == 'on':
            self.show_slicer = True
            
        if self.show_aoi:
            self.gui.sim_config.show_aoi(self.surfmesh)
            self.gui.sim_config.areas_of_intrest_picker.next_button.configure(command=self.on_aoi_next)
        else:
            if self.show_slicer:
                self.gui.sim_config.show_slicer(self.surfmesh)
                self.gui.sim_config.slice_picker.next_button.configure(command=self.on_slice_next)
            else:
                self._set_show_varconfig()
        
        
            
    def on_aoi_next(self):
        if self.show_slicer:
            self.gui.sim_config.areas_of_intrest_picker.pack_forget()
            self.gui.sim_config.show_slicer(self.surfmesh)
            self.gui.sim_config.slice_picker.next_button.configure(command=self.on_slice_next)
        else:
            self.gui.sim_config.areas_of_intrest_picker.pack_forget()
            self._set_show_varconfig()
            
            self.gui.sim_config.variable_config.set_aoi(self.gui.sim_config.aoi_list)
            self.gui.sim_config.variable_config.set_slices(self.gui.sim_config.slice_picker.get_slices_list())
            self.gui.sim_config.variable_config.run_button.configure(command= self.on_var_run)
        # or use the get_aoi_list
        
    def on_slice_next(self):
        self.gui.sim_config.slice_picker.pack_forget()
        self._set_show_varconfig()
             
        if self.show_aoi:
            self.gui.sim_config.variable_config.set_aoi(self.gui.sim_config.aoi_list)
            
        self.gui.sim_config.variable_config.set_slices(self.gui.sim_config.slice_picker.get_slices_list())
        
        self.gui.sim_config.variable_config.run_button.configure(command= self.on_var_run)
        
    def on_var_run(self):
        
        print("works")
     
        self.gui.withdraw()
        self.result_window = ResultWindow(self.gui)
             
        print('working here')
        
    # Set plot data and variable dictionaries
        self.result_window.set_plot_data(surfpoint_input=self.surfpoints,airpoints_input=self.airpoints,
            surfmesh_input=self.surfmesh,surfdata_input=self.surfdata,airdata_input=self.airdata)
        
        if self.gui.side_bar.check_var_0.get() == 'on': # time series sim
            self.result_window.checked_types[0] = 1
            self.result_window.add_var_dictionaries('time series',self.gui.sim_config.variable_config.simulation_time_series.get_all_data())
        if self.gui.side_bar.check_var_2.get() == 'on': # results
            self.result_window.checked_types[1] = 1
            self.result_window.add_var_dictionaries('results',self.gui.sim_config.variable_config.simulation_results.get_all_data())
        if self.gui.side_bar.check_var_3.get() == 'on': # comparison
            self.result_window.checked_types[2] = 1
            self.result_window.add_var_dictionaries('comparison',self.gui.sim_config.variable_config.simulation_comparison.get_all_data())
        if self.gui.side_bar.check_var_4.get() == 'on': # slices
            self.result_window.checked_types[3] = 1
            self.result_window.add_var_dictionaries('slices',self.gui.sim_config.variable_config.slices.get_all_data())
        if self.gui.side_bar.check_var_6.get() == 'on':
            self.result_window.checked_types[4] = 1
        if self.gui.side_bar.check_var_7.get() == 'on':
            self.result_window.checked_types[5] = 1

        print('also here', self.result_window.checked_types)

        
        self.result_window.initiate_results()
        
        print("all good")

################################################## helper functions ####################################################
    def _set_show_varconfig(self):
        
        self.gui.sim_config.show_var_config( self.gui.side_bar.check_var_0.get(),self.gui.side_bar.check_var_2.get(),self.gui.side_bar.check_var_3.get(),self.gui.side_bar.check_var_4.get(),self.gui.side_bar.check_var_5.get(),self.gui.side_bar.check_var_6.get())
        # set the variables of the varconfig
        self.gui.sim_config.variable_config.set_var_list(self.surfdata)
        self.gui.sim_config.variable_config.iniate_varconfig()
        if len(self.surface_matching_files) > 1 and self.gui.sim_config.variable_config.simulation_comparison != None:
            self.gui.sim_config.variable_config.set_paths(self.surface_matching_files[1:])        
            

# Main
if __name__ == "__main__":
       
    # Instantiate
    controller = Controller()
    