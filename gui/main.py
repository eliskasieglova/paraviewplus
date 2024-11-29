from view import App
from tkinter import ttk
import customtkinter as ctk


'''
do shapefiles come with the csv outputed by ferda ? (if not to add the ability to add csv files)

'''
'''
To do:

- make the result gui
- add slicing in the area of intrest gui 
- add errors for the submit button
- add the filedialig for the ferda and the browse segments
- 

'''

class Controller:
    def __init__(self):
        self.gui = App()  # Main view
        
        self.connect_events()

        self.gui.mainloop()  # Starts the GUI main loop


    def connect_events(self):
        self.gui.side_bar.submit_button.configure(command=self.on_submit)
        
        
    def on_submit(self):
        show_aoi = False
        selected_import_path = self.gui.side_bar.input_segmented_button.get()
        if selected_import_path == 'Browse':
            self.shp_file = self.gui.side_bar.path_bar.get()
            self.air_shp_file = self.gui.side_bar.path_bar2.get()
        # ferda chosen
        else:
           # disect the ferda directory into files
           self.ferda_directory_path = self.gui.side_bar.ferda_path_bar.get()

        self.export_path = self.gui.side_bar.export_path_bar.get()
       
        #Simulation Time series
        if self.gui.side_bar.check_var_0.get() == 'on':
            show_aoi = True
            
        # #Simulation Winter Time
        # if self.gui.side_bar.check_var_1.get() == 'on':
        #     show_aoi = True        
        #Simulation result
        if self.gui.side_bar.check_var_2.get() == 'on':
            show_aoi = True
        #Simulation Comparison
        if self.gui.side_bar.check_var_3.get() == 'on':
            show_aoi = True

            
        if show_aoi:
            self.gui.sim_config.show_aoi(self.shp_file)
            self.gui.sim_config.areas_of_intrest_picker.next_button.configure(command=self.on_next)
        else:
            self.gui.sim_config.show_var_config( self.gui.side_bar.check_var_0.get(),self.gui.side_bar.check_var_1.get(),self.gui.side_bar.check_var_2.get(),self.gui.side_bar.check_var_3.get(),self.gui.side_bar.check_var_5.get(),self.gui.side_bar.check_var_6.get())
        
        
        
            
    def on_next(self):
        self.gui.sim_config.areas_of_intrest_picker.pack_forget()
        self.gui.sim_config.show_var_config( self.gui.side_bar.check_var_0.get(),self.gui.side_bar.check_var_1.get(),self.gui.side_bar.check_var_2.get(),self.gui.side_bar.check_var_3.get(),self.gui.side_bar.check_var_5.get(),self.gui.side_bar.check_var_6.get())
        
        self.gui.sim_config.variable_config.set_aoi(self.gui.sim_config.aoi_list)
            

# Main
if __name__ == "__main__":
       
    # Instantiate
    controller = Controller()
    