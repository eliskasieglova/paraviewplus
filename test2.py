

from CTkColorPicker import *
import customtkinter



class ComboBoxColorPicker(customtkinter.CTkToplevel):
    def __init__(self, master, height=220, width=200, **kwargs):
        super().__init__(takefocus=1)

        self.attach = master
        self.height = height
        self.width = width

        self.overrideredirect(True)  # Remove window decorations

        # Bind icons or dropdown arrow to iconify the color picker
        self.attach._canvas.tag_bind("right_parts", "<Button-1>", lambda e: self._iconify())
        self.attach._canvas.tag_bind("dropdown_arrow", "<Button-1>", lambda e: self._iconify())
        
        # Bind configure to hide dropdown when resized
        self.attach.bind('<Configure>', lambda e: self._withdraw(), add="+")
        self.attach.winfo_toplevel().bind('<Configure>', lambda e: self._withdraw(), add="+")        
        
        # Create a frame for color picker
        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)
        
        # Create the color picker widget
        self.colorpicker = CTkColorPicker(self.frame, orientation='horizental', width=260, height=180, corner_radius=6, command=self._pass, **kwargs)
        self.colorpicker.pack(expand=True, fill="both", padx=4, pady=4)
        
        # Initial setup
        self.update_idletasks()
        self.deiconify()
        self.withdraw()  # Start hidden
        
        self.hide = True
        
        # Bind click outside event
        self.bind("<FocusOut>", self._withdraw_focus_out)
        
    def _iconify(self):
        if self.attach.cget("state") == "disabled":
            return

        if self.winfo_ismapped():
            self.hide = False
            
        if self.hide:
            self.deiconify()        
            self.hide = False
            self.place_dropdown()
        else:
            self.withdraw()
            self.hide = True
            
    def _withdraw_focus_out(self, event):
        """Detect when the dropdown loses focus and close it."""
        # This ensures that when the dropdown loses focus, it gets hidden
        if self.winfo_ismapped():
            self.withdraw()
            self.hide = True
            
    def _withdraw(self):
        if self.winfo_ismapped():
            self.withdraw()
            self.hide = True
            
    def _pass(self, date):
        self.attach.set(f"{date}")
        # self._withdraw() # Optionally withdraw when color is selected
        
    def place_dropdown(self):
        x_pos = self.attach.winfo_rootx() 
        y_pos = self.attach.winfo_rooty() + self.attach.winfo_reqheight()

        self.geometry('{}x{}+{}+{}'.format(self.width, self.height, x_pos, y_pos))
        
         
        
# root = customtkinter.CTk()

# # colorpicker = CTkColorPicker(root,orientation='horizental', command=lambda e: print(e))
# # colorpicker.pack(expand=True, fill="both", padx=10, pady=10)

# def change_combobox_color(event):
#     # Get the selected color from the combobox
#     selected_color = combobox.get()
    
#     # Set the background color of the combobox based on the selected color
#     combobox.configure(fg_color=selected_color)


# combobox = customtkinter.CTkComboBox(root, border_width= 0)
# combobox.pack()

# # def printcolor(event):
# #     print(event)

# coolor = ComboBoxColorPicker(combobox)#, command=printcolor)

# combobox.bind("<<<ComboboxSelected>>>", change_combobox_color)

# root.mainloop()



import customtkinter as ctk

def change_combobox_color(event):
    # Get the selected color from the combobox
    selected_color = combobox.get()
    
    # Set the background color of the combobox based on the selected color
    combobox.configure(fg_color=selected_color)

# Set up the main window
root = ctk.CTk()

# Create a CTkComboBox with predefined colors (hex values)
combobox = ctk.CTkComboBox(root, command=change_combobox_color, border_width=0)
combobox.pack(pady=20)

# Set a default color
coolor = ComboBoxColorPicker(combobox)#, command=printcolor)

# Bind the combobox selection event to change color automatically when a value is selected


root.mainloop()
