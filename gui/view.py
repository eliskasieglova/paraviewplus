from tkinter import ttk
import customtkinter as ctk
import matplotlib.pyplot as plt

from gui.areas_of_intrest import AreaOfIntrest
from gui.variable_frames import VariableConfigure
from gui.slice_picker import Slicer


class SimulationConfiguration(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent, fg_color='transparent')
        
        self.aoi_list = []
        self.slices_list = []
           
        #self.configure(fg_color='green')
        
    def show_slicer(self, shp_path):
        self.slice_picker = Slicer(self, shp_path)
        self.slice_picker.pack( side='top', fill='both', expand=True)
        
    def show_aoi(self, shp_path):
        self.areas_of_intrest_picker = AreaOfIntrest(self, shp_path)
        self.areas_of_intrest_picker.pack( side='top', fill='both', expand=True)
        
    def show_var_config(self, c0, c2, c3, c4, c5, c6):
        self.variable_config = VariableConfigure(self, c0, c2, c3, c4, c5, c6)
        self.variable_config.pack( side='top', fill='both', expand=True)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
            # main setup
        self.title('Paraview Plus')
        self.geometry('1000x600')
        self.minsize(600,600)
        ctk.set_default_color_theme("dark-blue.json")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.side_bar = SideBar(self)
        self.side_bar.place(x=0,y=0, relwidth= 0.35, relheight=1)
        
        self.sim_config = SimulationConfiguration(self)
        self.sim_config.place(relx=0.35, y=0, relwidth=0.65, relheight=1)               
        
    def mainloop(self):
        super().mainloop()
        
    def on_closing(self):
        plt.close('all')  # Close all matplotlib figures
        self.quit()
        self.destroy()     # Close the Tkinter window

        
class SideBar(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent, fg_color='transparent')
      
        self.main_input().pack(side='top', fill='x', pady=(4,0), padx=4)  
        self.main_output().pack(side='top', fill='x', pady=(8,0), padx=4)
        self.simulation_type().pack(side='top', fill ='x', pady=(8,0), padx=4)
        
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(side='bottom', fill='x', pady=4, padx=4)
        
        self.submit_button = ctk.CTkButton(bottom_frame, text='Submit', width=80)
        self.submit_button.pack(side='right', padx= 4, pady=4)
        
    def main_input(self):
        self.main_input_frame = ctk.CTkFrame(self)
        
        main_label = ctk.CTkLabel(self.main_input_frame, text='Input Files', font=('Futura', 14,'bold'))
        main_label.pack(side='top', fill='both', expand= True, pady=(0,2), padx=2)
        
        self.input_segmented_button = ctk.CTkSegmentedButton(self.main_input_frame, values=['Ferda','Browse'], command=self.input_segmented_button_command)
        self.input_segmented_button.pack(side='top', pady=(4,0))
        self.input_segmented_button.set('Ferda')

        self.input_file_2 = self.ferda_input()
        self.input_file_2.pack(side='top', fill='both', expand= True, pady=(0,2), padx=2)
          
        self.input_file = self.browse_input()
        self.input_file.pack_forget()
    
        return self.main_input_frame
    
    def input_segmented_button_command(self, selected_value):
        if selected_value == 'Ferda':
            self.input_file.pack_forget()
            self.input_file_2.pack(side='top', fill='both', expand= True, pady=(0,2), padx=2)
        if selected_value == 'Browse':
            self.input_file_2.pack_forget() 
            self.input_file.pack(side='top', fill='both', expand= True, pady=(0,2), padx=2)
           
    def browse_input(self):
        browse_frame = ctk.CTkFrame(self.main_input_frame, fg_color='transparent')
        
        browse_frame.grid_columnconfigure(0, weight=1)
        browse_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(browse_frame, text="Surface Points:")
        search_label.grid(column=0, row=0,sticky='W', padx=(8,0), pady=(2,0))  
         
        browse_button_frame = ctk.CTkFrame(browse_frame, fg_color='transparent')
        browse_button_frame.grid(column=0, row=1,columnspan=2, sticky='WE', padx=(8,8))
    
        self.path_bar = ctk.CTkEntry(browse_button_frame, border_width=0)
        self.path_bar.pack(side='left', fill='x',expand=True, padx=(0,4))

        self.browse_button = ctk.CTkButton(browse_button_frame, text='Browse', width=80)
        self.browse_button.pack(side='left')
        
        search_label2 = ctk.CTkLabel(browse_frame, text="Surface Polygons:")
        search_label2.grid(column=0, row=2,sticky='W', padx=(8,0), pady=(2,0))  
        
        browse_button_frame2 = ctk.CTkFrame(browse_frame, fg_color='transparent')
        browse_button_frame2.grid(column=0, row=3,columnspan=2, sticky='WE', padx=(8,8), pady=(0,4))
    
        self.path_bar2 = ctk.CTkEntry(browse_button_frame2, border_width=0)
        self.path_bar2.pack(side='left', fill='x',expand=True, padx=(0,4))

        self.browse_button2 = ctk.CTkButton(browse_button_frame2, text='Browse', width=80)
        self.browse_button2.pack(side='left')
        
        search_label3 = ctk.CTkLabel(browse_frame, text="Surface Data:")
        search_label3.grid(column=0, row=4,sticky='W', padx=(8,0), pady=(2,0))  
        
        browse_button_frame3 = ctk.CTkFrame(browse_frame, fg_color='transparent')
        browse_button_frame3.grid(column=0, row=5,columnspan=2, sticky='WE', padx=(8,8), pady=(0,4))
    
        self.path_bar3 = ctk.CTkEntry(browse_button_frame3, border_width=0)
        self.path_bar3.pack(side='left', fill='x',expand=True, padx=(0,4))

        self.browse_button3 = ctk.CTkButton(browse_button_frame3, text='Browse', width=80)
        self.browse_button3.pack(side='left')
        
        return browse_frame
    
    def ferda_input(self):
        ferda_frame = ctk.CTkFrame(self.main_input_frame, fg_color='transparent')
        
        ferda_frame.grid_columnconfigure(0, weight=1)
        ferda_frame.grid_columnconfigure(1, weight=1)        
        
        search_info_label = ctk.CTkLabel(ferda_frame, text="Ferda output Directory", justify="left",wraplength=270)
        search_info_label.grid(column=0, row=1, columnspan=2, sticky='W', padx=8, pady=(0,4))        
    
        browse_button_frame = ctk.CTkFrame(ferda_frame, fg_color='transparent')
        browse_button_frame.grid(column=0, row=2,columnspan=2, sticky='WE', padx=(8,8))
    
        self.ferda_path_bar = ctk.CTkEntry(browse_button_frame, border_width=0)
        self.ferda_path_bar.pack(side='left', fill='x',expand=True, padx=(0,4))
        
        # TO REMOVE
        #self.ferda_path_bar.insert(0,"C:\\Users\\farid\\Documents\\GitHub\\paraviewplus\\data")
        self.ferda_path_bar.insert(0,"data")

        self.browse_button = ctk.CTkButton(browse_button_frame, text='Browse', width=80)
        self.browse_button.pack(side='left')
        
        return ferda_frame
        
        
    def main_output(self):
        output_frame = ctk.CTkFrame(self)
        
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(1, weight=1)
        
        output_label = ctk.CTkLabel(output_frame, text="Export Path", font=('Futura', 14,'bold'), height= 12)
        output_label.grid(column=0, row=1, columnspan=2, padx=(8,0), pady=(2,0))  
        
        output_info_label = ctk.CTkLabel(output_frame, text="please select the export Directory", justify="left",wraplength=270, text_color='#727373')
        output_info_label.grid(column=0, row=2, columnspan=2, sticky='W', padx=8, pady=(0,4))        
    
        output_button_frame = ctk.CTkFrame(output_frame, fg_color='transparent')
        output_button_frame.grid(column=0, row=3,columnspan=2, sticky='WE', padx=(8,8), pady=(0,4))
    
        self.export_path_bar = ctk.CTkEntry(output_button_frame, border_width=0)
        self.export_path_bar.pack(side='left', fill='x',expand=True, padx=(0,4))

        self.browse_button = ctk.CTkButton(output_button_frame, text='Browse', width=80)
        self.browse_button.pack(side='left') 
        
        return output_frame   
    
    
    def simulation_type(self):
        sim_frame = ctk.CTkFrame(self)

        output_label = ctk.CTkLabel(sim_frame, text="Simulation Types", font=('Futura', 14,'bold'), height= 12)
        output_label.pack(side ='top', padx=(8,0), pady=(2,0)) 
        
        self.check_var_0 = ctk.StringVar(value="off")
        checkbox_0 = ctk.CTkCheckBox(sim_frame, text="Simulation Time series",border_width = 2,variable=self.check_var_0, onvalue="on", offvalue="off")#, state='disabled')
        checkbox_0.pack(side='top', fill = 'x', pady=4)       
        
        self.check_var_2 = ctk.StringVar(value="on")
        checkbox_2 = ctk.CTkCheckBox(sim_frame, text="Simulation result",border_width = 2,variable=self.check_var_2, onvalue="on", offvalue="off")
        checkbox_2.pack(side='top', fill = 'x', pady=(0,4))

        self.check_var_3 = ctk.StringVar(value="on")
        checkbox_3 = ctk.CTkCheckBox(sim_frame, text="Simulation Comparison",border_width = 2,variable=self.check_var_3, onvalue="on", offvalue="off")
        checkbox_3.pack(side='top', fill = 'x', pady=(0,4))
        
        self.check_var_4 = ctk.StringVar(value="off")
        checkbox_4 = ctk.CTkCheckBox(sim_frame, text="Slices",border_width = 2,variable=self.check_var_4, onvalue="on", offvalue="off")#, state='disabled')
        checkbox_4.pack(side='top', fill = 'x', pady=(0,4))
        
        self.check_var_5 = ctk.StringVar(value="off")
        checkbox_5 = ctk.CTkCheckBox(sim_frame, text="Windflow",border_width = 2,variable=self.check_var_5, onvalue="on", offvalue="off", state='disabled')
        checkbox_5.pack(side='top', fill = 'x', pady=(0,4))
        
        self.check_var_6 = ctk.StringVar(value="off")
        checkbox_6 = ctk.CTkCheckBox(sim_frame, text="Windrose",border_width = 2,variable=self.check_var_6, onvalue="on", offvalue="off")
        checkbox_6.pack(side='top', fill = 'x', pady=(0,4))
        
        self.check_var_7 = ctk.StringVar(value="on")
        checkbox_7 = ctk.CTkCheckBox(sim_frame, text="UTCI Heat Stress",border_width = 2,variable=self.check_var_7, onvalue="on", offvalue="off")
        checkbox_7.pack(side='top', fill = 'x', pady=(0,4))
        
        return sim_frame 
    
# to remember call the following class by the calling a function to create the class by         
    

