import customtkinter as ctk
from tkinter import filedialog



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
        
    def get_accepted_aoi(self):
        ...
        
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
        
    

class SimTimeSeries(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        sim_time_series_label = ctk.CTkLabel(self, text="Simulation Time Series", font=("Arial", 14, "bold"))
        sim_time_series_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        sim_time_series_label2 = ctk.CTkLabel(self, text="Variables:")
        sim_time_series_label2.grid(row=1,column =0, sticky='W', padx=4, pady=2)
        
        check_var_2 = ctk.StringVar(value="on")
        tair_checkbox = ctk.CTkCheckBox(self, text=" Air Temperature",border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        tair_checkbox.grid(row=2,column =0, sticky='W', padx=4, pady=2)

        check_var_2 = ctk.StringVar(value="on")
        tsurface_checkbox = ctk.CTkCheckBox(self, text='Surface Temperature',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        tsurface_checkbox.grid(row=2,column =1, sticky='W', padx=4, pady=(0,2))
        
        # _checkbox = ctk.CTkCheckBox(self, text='')
        # _checkbox.grid(row=,column=,sticky='W')
        
        et_checkbox = ctk.CTkCheckBox(self, text='ET',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        et_checkbox.grid(row=3,column=0,sticky='W', padx=4, pady=(0,2))

        rh_checkbox = ctk.CTkCheckBox(self, text='Relative Humidity',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        rh_checkbox.grid(row=3,column=1,sticky='W', padx=4, pady=(0,2))
        
        utci_checkbox = ctk.CTkCheckBox(self, text='UTCI',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        utci_checkbox.grid(row=4,column=0,sticky='W', padx=4, pady=(0,2))
        
        sim_time_series_label3 = ctk.CTkLabel(self, text="Areas of Intrest:")
        sim_time_series_label3.grid(row=5,column =0, sticky='W', padx=4) 
        
        # sized scrollbar for with frames of the ares of intrest and checkboxes 
        self.aoi_frames = SizedScrollableFrame(self, height=80)
        self.aoi_frames.grid(row=6, column =0, columnspan=2, sticky='WE', padx=4, pady=4)
        
        self.winter_checkbox_var = ctk.IntVar(value=0)
        winter_checkbox = ctk.CTkCheckBox(self, text='Winter Time series',border_width = 2,variable=self.winter_checkbox_var, onvalue="on", offvalue="off", command= self.on_winter_check)
        winter_checkbox.grid(row=7,column=0,sticky='W', padx=4, pady=(0,2))
        
        winter_frame = ctk.CTkFrame(self)
        winter_frame.grid(row=8, column=0, columnspan=2, sticky="NSWE",padx=4, pady=(0,2))
        
        self.winter_time_series = WinterTimeSeries(winter_frame)
        
        
    def on_winter_check(self):
        if self.winter_checkbox_var.get() == 1:
            self.winter_time_series.pack(side='top', fill='x', padx=4, pady=4)
        else:
            self.winter_time_series.pack_forget()
        
    def set_aoi_frames(self, aoi_list):
        for i in range(len(aoi_list)):
          aoi_frame = AoI(self.aoi_frames.scrollable_frame, i +1)
          aoi_frame.insert_data(aoi_list[i]) 


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
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        sim_results_label = ctk.CTkLabel(self, text="Simulation Results", font=("Arial", 14, "bold"))
        sim_results_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        sim_results_label2 = ctk.CTkLabel(self, text="Variables:")
        sim_results_label2.grid(row=1,column =0, sticky='W', padx=4)
        
        check_var_2 = ctk.StringVar(value="on")
        tair_checkbox = ctk.CTkCheckBox(self, text=" Air Temperature",border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        tair_checkbox.grid(row=2,column =0, sticky='W', padx=4, pady=2)

        check_var_2 = ctk.StringVar(value="on")
        tsurface_checkbox = ctk.CTkCheckBox(self, text='Surface Temperature',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        tsurface_checkbox.grid(row=2,column =1, sticky='W', padx=4, pady=2)
        
        # _checkbox = ctk.CTkCheckBox(self, text='')
        # _checkbox.grid(row=,column=,sticky='W')
        
        check_var_2 = ctk.StringVar(value="on")
        et_checkbox = ctk.CTkCheckBox(self, text='ET',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        et_checkbox.grid(row=3,column=0,sticky='W', padx=4, pady=(0,2))

        check_var_2 = ctk.StringVar(value="on")
        rh_checkbox = ctk.CTkCheckBox(self, text='Relative Humidity',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        rh_checkbox.grid(row=3,column=1,sticky='W', padx=4, pady=(0,2))
        
        check_var_2 = ctk.StringVar(value="on")
        utci_checkbox = ctk.CTkCheckBox(self, text='UTCI',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        utci_checkbox.grid(row=4,column=0,sticky='W', padx=4, pady=(0,2))
        
        sim_results_label3 = ctk.CTkLabel(self, text="Areas of Intrest:")
        sim_results_label3.grid(row=5,column =0, sticky='W', padx=4) 
        
        # sized scrollbar for with frames of the ares of intrest and checkboxes 
        self.aoi_frames = SizedScrollableFrame(self, height=80)
        self.aoi_frames.grid(row=6, column =0, columnspan=2, sticky='WE', padx=4, pady=4)      
        
    def set_aoi_frames(self, aoi_list):
        for i in range(len(aoi_list)):
          aoi_frame = AoI(self.aoi_frames.scrollable_frame, i +1)
          aoi_frame.insert_data(aoi_list[i])  

class SimulationComparison(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.no_of_dataframes = 0
        self.list_of_dataframes = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        sim_comparison_label = ctk.CTkLabel(self, text="Simulation Comparison", font=("Arial", 14, "bold"))
        sim_comparison_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))
        
        sim_comparison_label2 = ctk.CTkLabel(self, text="Variables:")
        sim_comparison_label2.grid(row=1,column =0, sticky='W', padx=4)
        
        check_var_2 = ctk.StringVar(value="on")
        tair_checkbox = ctk.CTkCheckBox(self, text=" Air Temperature",border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        tair_checkbox.grid(row=2,column =0, sticky='W', padx=4, pady=2)

        check_var_2 = ctk.StringVar(value="on")
        tsurface_checkbox = ctk.CTkCheckBox(self, text='Surface Temperature',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        tsurface_checkbox.grid(row=2,column =1, sticky='W', padx=4, pady=2)
        
        # _checkbox = ctk.CTkCheckBox(self, text='')
        # _checkbox.grid(row=,column=,sticky='W')
        
        check_var_2 = ctk.StringVar(value="on")
        et_checkbox = ctk.CTkCheckBox(self, text='ET',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        et_checkbox.grid(row=3,column=0,sticky='W', padx=4, pady=(0,2))

        check_var_2 = ctk.StringVar(value="on")
        rh_checkbox = ctk.CTkCheckBox(self, text='Relative Humidity',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        rh_checkbox.grid(row=3,column=1,sticky='W', padx=4, pady=(0,2))
        
        check_var_2 = ctk.StringVar(value="on")
        utci_checkbox = ctk.CTkCheckBox(self, text='UTCI',border_width = 2,variable=check_var_2, onvalue="on", offvalue="off")
        utci_checkbox.grid(row=4,column=0,sticky='W', padx=4, pady=(0,2))
        
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
        
    def set_aoi_frames(self, aoi_list):
        for i in range(len(aoi_list)):
          aoi_frame = AoI(self.aoi_frames.scrollable_frame, i +1)
          aoi_frame.insert_data(aoi_list[i])


class Airflow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        Airflow_label = ctk.CTkLabel(self, text="WindFlow", font=("Arial", 14, "bold"))
        Airflow_label.grid(row=0,column=0, sticky='W', padx=4,pady=(4,0))

        Airflow_label3 = ctk.CTkLabel(self, text="To Be Figured out")
        Airflow_label3.grid(row=1,column=0, sticky='W', padx=4,pady=(4,0))                            

class Windrose(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

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
        
            

    
class VariableConfigure(ctk.CTkFrame):
    def __init__(self, master, c0,c2,c3,c5,c6):
        super().__init__(master, fg_color='transparent')
        
        self.aoi_list = []
        
        self.simulation_time_series_checkbox,self.simulation_result_checkbox,self.simulation_comparison_checkbox = c0,c2,c3
        
        mainframe = ctk.CTkScrollableFrame(self, fg_color='transparent')
        mainframe.pack(side='top', fill='both', expand= True)
        
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(side='top', fill='x', padx=4, pady=4)
        
        run_button = ctk.CTkButton(bottom_frame, text="Run", width=80)
        run_button.pack(side='right', padx=4, pady=4)
        
        self.back_button = ctk.CTkButton(bottom_frame, text='Back', width=80)
        self.back_button.pack(side='right', padx=4, pady=4)
        
        #the following frames are for the the selected frames
        if c0 == 'on':
            self.simulation_time_series_frame = SimTimeSeries(mainframe)
            self.simulation_time_series_frame.pack(side='top', fill='x', padx=4, pady=4)
            


        if c2 == 'on':
            self.simulation_results = SimulationResults(mainframe)
            self.simulation_results.pack(side='top', fill='x', padx=4, pady=4)

        if c3 == 'on':
            self.simulation_comparison = SimulationComparison(mainframe)
            self.simulation_comparison.pack(side='top', fill='x', padx=4, pady=4)
            
        # NO Slices for now
            
        if c5 == 'on':
            air_flow = Airflow(mainframe)
            air_flow.pack(side='top', fill='x', padx=4, pady=4)
            
        if c6 == 'on':
            windrose = Windrose(mainframe)
            windrose.pack(side='top', fill='x', padx=4, pady=4)

        # NO UTCI

    def set_aoi(self, aoi):
        self.aoi_list = aoi
        
        if self.simulation_time_series_checkbox == 'on':
            self.simulation_time_series_frame.set_aoi_frames(self.aoi_list)
            
        if self.simulation_result_checkbox == 'on':
            self.simulation_results.set_aoi_frames(self.aoi_list)
            
        if self.simulation_comparison_checkbox == 'on':
            self.simulation_comparison.set_aoi_frames(self.aoi_list)