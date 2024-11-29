

from CTkColorPicker import *
import customtkinter
import customtkinter as ctk


            
            

class CustomColorPicker(customtkinter.CTkToplevel):
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
        self.attach.bind("<FocusOut>", self._withdraw())
        # Create a frame for color picker
        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)
        
        # Create the color picker widget
        self.colorpicker = CTkColorPicker(
            self.frame, 
            orientation='horizental', 
            width=260, 
            height=180, 
            corner_radius=6, 
            command=self._color_selected,  # Pass the callback function here
            **kwargs
        )
        self.colorpicker.pack(expand=True, fill="both", padx=4, pady=4)
        
        # Initial setup
        self.update_idletasks()
        self.deiconify()
        self.withdraw()  # Start hidden
        
        self.hide = True
        
        # Bind click outside event
        
        
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
            
    def _withdraw(self):
        if self.winfo_ismapped():
            self.withdraw()
            self.hide = True
            
    def _color_selected(self, color):
        """Callback function when a color is selected."""
        #print(f"Selected color: {color}")  # Print the selected color
        self.attach.set(f"{color}")
        self.event_generate("<<ColorPickerColorSelected>>", when="tail")
        
    def place_dropdown(self):
        x_pos = self.attach.winfo_rootx() 
        y_pos = self.attach.winfo_rooty() + self.attach.winfo_reqheight()

        self.geometry('{}x{}+{}+{}'.format(self.width, self.height, x_pos, y_pos))

from typing import Callable

class Spinbox(ctk.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 start_value: int = 0,
                 step_size: int = 1,
                 min_value: int = 0,  # Specify type for min_value
                 max_value: int = 100,  # Specify type for max_value
                 command: Callable[[int], None] = None,  # Command receives the current value
                 **kwargs):
        self.start_value = start_value
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))

        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.subtract_button = ctk.CTkButton(self, text="-", width=height-6, height=height-6,
                                             command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = ctk.CTkEntry(self, width=width-(70), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="nsew")

        self.add_button = ctk.CTkButton(self, text="+", width=height-6, height=height-6,
                                        command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # Default value
        self.entry.insert(0, self.start_value)

        # Bind all elements to mouse wheel event
        self.entry.bind("<MouseWheel>", self.on_mouse_wheel)
        self.subtract_button.bind("<MouseWheel>", self.on_mouse_wheel)
        self.add_button.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<MouseWheel>", self.on_mouse_wheel)

    def add_button_callback(self):
        try:
            value = int(self.entry.get()) + self.step_size
            if value <= self.max_value:
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
                if self.command is not None:
                    self.command(value)
        except ValueError:
            return

    def subtract_button_callback(self):
        try:
            value = int(self.entry.get()) - self.step_size
            if value >= self.min_value:
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
                if self.command is not None:
                    self.command(value)
        except ValueError:
            return

    def get(self) -> int:
        try:
            return int(self.entry.get())
        except ValueError:
            return 0

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.add_button_callback()
        else:
            self.subtract_button_callback()

    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, int(value))


"""
CTkRangeSlider
Range slider for customtkinter
Author: Akash Bora
Version: 0.2
"""

import math
import tkinter
import sys
from typing import Union, Tuple, Callable, Optional, List

from customtkinter.windows.widgets.core_rendering import DrawEngine
from customtkinter.windows.widgets.theme import ThemeManager
from customtkinter.windows.widgets.core_rendering import CTkCanvas
from customtkinter.windows.widgets.core_widget_classes import CTkBaseClass

class CustomDrawEngine:
    """
    This is a custom version of the core of the CustomTkinter library where all the drawing on the tkinter.Canvas happens.
    It is tailored towards the range slider.
    """

    preferred_drawing_method: str = "font_shapes" # 'polygon_shapes', 'font_shapes', 'circle_shapes'

    def __init__(self, canvas: CTkCanvas):
        self._canvas = canvas
        
    def _DrawEngine__draw_rounded_rect_with_border_font_shapes(self, width: int, height: int, corner_radius: int, border_width: int, inner_corner_radius: int,
                                                    exclude_parts: tuple) -> bool:
        requires_recoloring = False

        # create border button parts
        if border_width > 0:
            if corner_radius > 0:
                # create canvas border corner parts if not already created, but only if needed, and delete if not needed
                if not self._canvas.find_withtag("border_oval_1_a") and "border_oval_1" not in exclude_parts:
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_1_a", "border_corner_part", "border_parts"), anchor=tkinter.CENTER)
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_1_b", "border_corner_part", "border_parts"), anchor=tkinter.CENTER, angle=180)
                    requires_recoloring = True
                elif self._canvas.find_withtag("border_oval_1_a") and "border_oval_1" in exclude_parts:
                    self._canvas.delete("border_oval_1_a", "border_oval_1_b")

                if not self._canvas.find_withtag("border_oval_2_a") and width > 2 * corner_radius and "border_oval_2" not in exclude_parts:
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_2_a", "border_corner_part", "border_parts"), anchor=tkinter.CENTER)
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_2_b", "border_corner_part", "border_parts"), anchor=tkinter.CENTER, angle=180)
                    requires_recoloring = True
                elif self._canvas.find_withtag("border_oval_2_a") and (not width > 2 * corner_radius or "border_oval_2" in exclude_parts):
                    self._canvas.delete("border_oval_2_a", "border_oval_2_b")

                if not self._canvas.find_withtag("border_oval_3_a") and height > 2 * corner_radius \
                    and width > 2 * corner_radius and "border_oval_3" not in exclude_parts:
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_3_a", "border_corner_part", "border_parts"), anchor=tkinter.CENTER)
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_3_b", "border_corner_part", "border_parts"), anchor=tkinter.CENTER, angle=180)
                    requires_recoloring = True
                elif self._canvas.find_withtag("border_oval_3_a") and (not (height > 2 * corner_radius
                                                                            and width > 2 * corner_radius) or "border_oval_3" in exclude_parts):
                    self._canvas.delete("border_oval_3_a", "border_oval_3_b")

                if not self._canvas.find_withtag("border_oval_4_a") and height > 2 * corner_radius and "border_oval_4" not in exclude_parts:
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_4_a", "border_corner_part", "border_parts"), anchor=tkinter.CENTER)
                    self._canvas.create_aa_circle(0, 0, 0, tags=("border_oval_4_b", "border_corner_part", "border_parts"), anchor=tkinter.CENTER, angle=180)
                    requires_recoloring = True
                elif self._canvas.find_withtag("border_oval_4_a") and (not height > 2 * corner_radius or "border_oval_4" in exclude_parts):
                    self._canvas.delete("border_oval_4_a", "border_oval_4_b")

                # change position of border corner parts
                self._canvas.coords("border_oval_1_a", corner_radius, corner_radius, corner_radius)
                self._canvas.coords("border_oval_1_b", corner_radius, corner_radius, corner_radius)
                self._canvas.coords("border_oval_2_a", width - corner_radius, corner_radius, corner_radius)
                self._canvas.coords("border_oval_2_b", width - corner_radius, corner_radius, corner_radius)
                self._canvas.coords("border_oval_3_a", width - corner_radius, height - corner_radius, corner_radius)
                self._canvas.coords("border_oval_3_b", width - corner_radius, height - corner_radius, corner_radius)
                self._canvas.coords("border_oval_4_a", corner_radius, height - corner_radius, corner_radius)
                self._canvas.coords("border_oval_4_b", corner_radius, height - corner_radius, corner_radius)

            else:
                self._canvas.delete("border_corner_part")  # delete border corner parts if not needed

            # create canvas border rectangle parts if not already created
            if not self._canvas.find_withtag("border_rectangle_1"):
                self._canvas.create_rectangle(0, 0, 0, 0, tags=("border_rectangle_1", "border_rectangle_part", "border_parts"), width=0)
                self._canvas.create_rectangle(0, 0, 0, 0, tags=("border_rectangle_2", "border_rectangle_part", "border_parts"), width=0)
                requires_recoloring = True

            # change position of border rectangle parts
            self._canvas.coords("border_rectangle_1", (0, corner_radius, width, height - corner_radius))
            self._canvas.coords("border_rectangle_2", (corner_radius, 0, width - corner_radius, height))

        else:
            self._canvas.delete("border_parts")

        # create inner button parts
        if inner_corner_radius > 0:

            # create canvas border corner parts if not already created, but only if they're needed and delete if not needed
            if not self._canvas.find_withtag("inner_oval_1_a") and "inner_oval_1" not in exclude_parts:
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_1_a", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER)
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_1_b", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER, angle=180)
                requires_recoloring = True
            elif self._canvas.find_withtag("inner_oval_1_a") and "inner_oval_1" in exclude_parts:
                self._canvas.delete("inner_oval_1_a", "inner_oval_1_b")

            if not self._canvas.find_withtag("inner_oval_2_a") and width - (2 * border_width) > 2 * inner_corner_radius and "inner_oval_2" not in exclude_parts:
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_2_a", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER)
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_2_b", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER, angle=180)
                requires_recoloring = True
            elif self._canvas.find_withtag("inner_oval_2_a") and (not width - (2 * border_width) > 2 * inner_corner_radius or "inner_oval_2" in exclude_parts):
                self._canvas.delete("inner_oval_2_a", "inner_oval_2_b")

            if not self._canvas.find_withtag("inner_oval_3_a") and height - (2 * border_width) > 2 * inner_corner_radius \
                and width - (2 * border_width) > 2 * inner_corner_radius and "inner_oval_3" not in exclude_parts:
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_3_a", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER)
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_3_b", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER, angle=180)
                requires_recoloring = True
            elif self._canvas.find_withtag("inner_oval_3_a") and (not (height - (2 * border_width) > 2 * inner_corner_radius
                                                                       and width - (2 * border_width) > 2 * inner_corner_radius) or "inner_oval_3" in exclude_parts):
                self._canvas.delete("inner_oval_3_a", "inner_oval_3_b")

            if not self._canvas.find_withtag("inner_oval_4_a") and height - (2 * border_width) > 2 * inner_corner_radius and "inner_oval_4" not in exclude_parts:
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_4_a", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER)
                self._canvas.create_aa_circle(0, 0, 0, tags=("inner_oval_4_b", "inner_corner_part", "inner_parts"), anchor=tkinter.CENTER, angle=180)
                requires_recoloring = True
            elif self._canvas.find_withtag("inner_oval_4_a") and (not height - (2 * border_width) > 2 * inner_corner_radius or "inner_oval_4" in exclude_parts):
                self._canvas.delete("inner_oval_4_a", "inner_oval_4_b")

            # change position of border corner parts
            self._canvas.coords("inner_oval_1_a", border_width + inner_corner_radius, border_width + inner_corner_radius, inner_corner_radius)
            self._canvas.coords("inner_oval_1_b", border_width + inner_corner_radius, border_width + inner_corner_radius, inner_corner_radius)
            self._canvas.coords("inner_oval_2_a", width - border_width - inner_corner_radius, border_width + inner_corner_radius, inner_corner_radius)
            self._canvas.coords("inner_oval_2_b", width - border_width - inner_corner_radius, border_width + inner_corner_radius, inner_corner_radius)
            self._canvas.coords("inner_oval_3_a", width - border_width - inner_corner_radius, height - border_width - inner_corner_radius, inner_corner_radius)
            self._canvas.coords("inner_oval_3_b", width - border_width - inner_corner_radius, height - border_width - inner_corner_radius, inner_corner_radius)
            self._canvas.coords("inner_oval_4_a", border_width + inner_corner_radius, height - border_width - inner_corner_radius, inner_corner_radius)
            self._canvas.coords("inner_oval_4_b", border_width + inner_corner_radius, height - border_width - inner_corner_radius, inner_corner_radius)
        else:
            self._canvas.delete("inner_corner_part")  # delete inner corner parts if not needed

        # create canvas inner rectangle parts if not already created
        if not self._canvas.find_withtag("inner_rectangle_1"):
            self._canvas.create_rectangle(0, 0, 0, 0, tags=("inner_rectangle_1", "inner_rectangle_part", "inner_parts"), width=0)
            requires_recoloring = True

        if not self._canvas.find_withtag("inner_rectangle_2") and inner_corner_radius * 2 < height - (border_width * 2):
            self._canvas.create_rectangle(0, 0, 0, 0, tags=("inner_rectangle_2", "inner_rectangle_part", "inner_parts"), width=0)
            requires_recoloring = True

        elif self._canvas.find_withtag("inner_rectangle_2") and not inner_corner_radius * 2 < height - (border_width * 2):
            self._canvas.delete("inner_rectangle_2")

        # change position of inner rectangle parts
        self._canvas.coords("inner_rectangle_1", (border_width + inner_corner_radius,
                                                  border_width,
                                                  width - border_width - inner_corner_radius,
                                                  height - border_width))
        self._canvas.coords("inner_rectangle_2", (border_width,
                                                  border_width + inner_corner_radius,
                                                  width - border_width,
                                                  height - inner_corner_radius - border_width))

        if requires_recoloring:  # new parts were added -> manage z-order
            self._canvas.tag_lower("inner_parts")
            self._canvas.tag_lower("border_parts")

        return requires_recoloring
    
    def draw_rounded_slider_with_border_and_2_button(self, width: Union[float, int], height: Union[float, int], corner_radius: Union[float, int],
                                                   border_width: Union[float, int], button_length: Union[float, int], button_corner_radius: Union[float, int],
                                                   slider_value: float, slider_2_value: float, orientation: str) -> bool:

        width = math.floor(width / 2) * 2  # round _current_width and _current_height and restrict them to even values only
        height = math.floor(height / 2) * 2

        if corner_radius > width / 2 or corner_radius > height / 2:  # restrict corner_radius if it's too larger
            corner_radius = min(width / 2, height / 2)

        if button_corner_radius > width / 2 or button_corner_radius > height / 2:  # restrict button_corner_radius if it's too larger
            button_corner_radius = min(width / 2, height / 2)

        button_length = round(button_length)
        border_width = round(border_width)
        button_corner_radius = round(button_corner_radius)
        corner_radius = DrawEngine._DrawEngine__calc_optimal_corner_radius(self, corner_radius)  # optimize corner_radius for different drawing methods (different rounding)

        if corner_radius >= border_width:
            inner_corner_radius = corner_radius - border_width
        else:
            inner_corner_radius = 0

        if self.preferred_drawing_method == "polygon_shapes" or self.preferred_drawing_method == "circle_shapes":
            return self.__draw_rounded_slider_with_border_and_2_button_polygon_shapes(width, height, corner_radius, border_width, inner_corner_radius,
                                                                                    button_length, button_corner_radius, slider_value, slider_2_value, orientation)
        elif self.preferred_drawing_method == "font_shapes":
            return self.__draw_rounded_slider_with_border_and_2_button_font_shapes(width, height, corner_radius, border_width, inner_corner_radius,
                                                                                 button_length, button_corner_radius, slider_value, slider_2_value, orientation)

    def __draw_rounded_slider_with_border_and_2_button_polygon_shapes(self, width: int, height: int, corner_radius: int, border_width: int, inner_corner_radius: int,
                                                                    button_length: int, button_corner_radius: int, slider_value: float, slider_2_value: float, orientation: str) -> bool:

        # draw normal progressbar
        requires_recoloring = DrawEngine._DrawEngine__draw_rounded_progress_bar_with_border_polygon_shapes(self, width, height, corner_radius, border_width, inner_corner_radius,
                                                                                          slider_value, slider_2_value, orientation)

        # create slider button part
        if not self._canvas.find_withtag("slider_parts"):
            self._canvas.create_polygon((0, 0, 0, 0), tags=("slider_line_1", "slider_parts", "slider_0_parts"), joinstyle=tkinter.ROUND)
            self._canvas.create_polygon((0, 0, 0, 0), tags=("slider_2_line_1", "slider_parts", "slider_1_parts"), joinstyle=tkinter.ROUND)
            self._canvas.tag_raise("slider_parts")  # manage z-order
            requires_recoloring = True

        if corner_radius <= border_width:
            bottom_right_shift = -1  # weird canvas rendering inaccuracy that has to be corrected in some cases
        else:
            bottom_right_shift = 0

        if orientation == "w":
            slider_x_position = corner_radius + (button_length / 2) + (width - 2 * corner_radius - button_length) * slider_value
            self._canvas.coords("slider_line_1",
                                slider_x_position - (button_length / 2), button_corner_radius,
                                slider_x_position + (button_length / 2), button_corner_radius,
                                slider_x_position + (button_length / 2), height - button_corner_radius,
                                slider_x_position - (button_length / 2), height - button_corner_radius)
            self._canvas.itemconfig("slider_line_1",
                                    width=button_corner_radius * 2)

            slider_x_position = corner_radius + (button_length / 2) + (width - 2 * corner_radius - button_length) * slider_2_value
            self._canvas.coords("slider_2_line_1",
                                slider_x_position - (button_length / 2), button_corner_radius,
                                slider_x_position + (button_length / 2), button_corner_radius,
                                slider_x_position + (button_length / 2), height - button_corner_radius,
                                slider_x_position - (button_length / 2), height - button_corner_radius)
            self._canvas.itemconfig("slider_2_line_1",
                                    width=button_corner_radius * 2)
        elif orientation == "s":
            slider_y_position = corner_radius + (button_length / 2) + (height - 2 * corner_radius - button_length) * (1 - slider_value)
            self._canvas.coords("slider_line_1",
                                button_corner_radius, slider_y_position - (button_length / 2),
                                button_corner_radius, slider_y_position + (button_length / 2),
                                width - button_corner_radius, slider_y_position + (button_length / 2),
                                width - button_corner_radius, slider_y_position - (button_length / 2))
            self._canvas.itemconfig("slider_line_1",
                                    width=button_corner_radius * 2)

            slider_y_position = corner_radius + (button_length / 2) + (height - 2 * corner_radius - button_length) * (1 - slider_2_value)
            self._canvas.coords("slider_2_line_1",
                                button_corner_radius, slider_y_position - (button_length / 2),
                                button_corner_radius, slider_y_position + (button_length / 2),
                                width - button_corner_radius, slider_y_position + (button_length / 2),
                                width - button_corner_radius, slider_y_position - (button_length / 2))
            self._canvas.itemconfig("slider_2_line_1",
                                    width=button_corner_radius * 2)

        return requires_recoloring

    def __draw_rounded_slider_with_border_and_2_button_font_shapes(self, width: int, height: int, corner_radius: int, border_width: int, inner_corner_radius: int,
                                                                 button_length: int, button_corner_radius: int, slider_value: float, slider_2_value: float, orientation: str) -> bool:

        # draw normal progressbar
        requires_recoloring = DrawEngine._DrawEngine__draw_rounded_progress_bar_with_border_font_shapes(self, width, height, corner_radius, border_width,
                                                                                                        inner_corner_radius, slider_value, slider_2_value, orientation)

        # create 4 circles (if not needed, then less)
        if not self._canvas.find_withtag("slider_oval_1_a"):
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_1_a", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_1_b", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True

        if not self._canvas.find_withtag("slider_oval_2_a") and button_length > 0:
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_a", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_b", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_oval_2_a") and not button_length > 0:
            self._canvas.delete("slider_oval_2_a", "slider_oval_2_b")

        if not self._canvas.find_withtag("slider_oval_4_a") and height > 2 * button_corner_radius:
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_4_a", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_4_b", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_oval_4_a") and not height > 2 * button_corner_radius:
            self._canvas.delete("slider_oval_4_a", "slider_oval_4_b")

        if not self._canvas.find_withtag("slider_oval_3_a") and button_length > 0 and height > 2 * button_corner_radius:
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_3_a", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_3_b", "slider_corner_part", "slider_parts", "slider_0_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True
        elif self._canvas.find_withtag("border_oval_3_a") and not (button_length > 0 and height > 2 * button_corner_radius):
            self._canvas.delete("slider_oval_3_a", "slider_oval_3_b")

        # create the 2 rectangles (if needed)
        if not self._canvas.find_withtag("slider_rectangle_1") and button_length > 0:
            self._canvas.create_rectangle(0, 0, 0, 0, tags=("slider_rectangle_1", "slider_rectangle_part", "slider_parts", "slider_0_parts"), width=0)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_rectangle_1") and not button_length > 0:
            self._canvas.delete("slider_rectangle_1")

        if not self._canvas.find_withtag("slider_rectangle_2") and height > 2 * button_corner_radius:
            self._canvas.create_rectangle(0, 0, 0, 0, tags=("slider_rectangle_2", "slider_rectangle_part", "slider_parts", "slider_0_parts"), width=0)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_rectangle_2") and not height > 2 * button_corner_radius:
            self._canvas.delete("slider_rectangle_2")

        # set positions of circles and rectangles
        if orientation == "w":
            slider_x_position = corner_radius + (button_length / 2) + (width - 2 * corner_radius - button_length) * slider_value
            self._canvas.coords("slider_oval_1_a", slider_x_position - (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_1_b", slider_x_position - (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_a", slider_x_position + (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_b", slider_x_position + (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_3_a", slider_x_position + (button_length / 2), height - button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_3_b", slider_x_position + (button_length / 2), height - button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_4_a", slider_x_position - (button_length / 2), height - button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_4_b", slider_x_position - (button_length / 2), height - button_corner_radius, button_corner_radius)

            self._canvas.coords("slider_rectangle_1",
                                slider_x_position - (button_length / 2), 0,
                                slider_x_position + (button_length / 2), height)
            self._canvas.coords("slider_rectangle_2",
                                slider_x_position - (button_length / 2) - button_corner_radius, button_corner_radius,
                                slider_x_position + (button_length / 2) + button_corner_radius, height - button_corner_radius)

        elif orientation == "s":
            slider_y_position = corner_radius + (button_length / 2) + (height - 2 * corner_radius - button_length) * (1 - slider_value)
            self._canvas.coords("slider_oval_1_a", button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_1_b", button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_a", button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_b", button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_3_a", width - button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_3_b", width - button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_4_a", width - button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_4_b", width - button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)

            self._canvas.coords("slider_rectangle_1",
                                0, slider_y_position - (button_length / 2),
                                width, slider_y_position + (button_length / 2))
            self._canvas.coords("slider_rectangle_2",
                                button_corner_radius, slider_y_position - (button_length / 2) - button_corner_radius,
                                width - button_corner_radius, slider_y_position + (button_length / 2) + button_corner_radius)

        ######## second button ##########
        # create 4 circles (if not needed, then less)
        if not self._canvas.find_withtag("slider_oval_2_1_a"):
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_1_a", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_1_b", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True

        if not self._canvas.find_withtag("slider_oval_2_2_a") and button_length > 0:
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_2_a", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_2_b", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_oval_2_2_a") and not button_length > 0:
            self._canvas.delete("slider_oval_2_2_a", "slider_oval_2_2_b")

        if not self._canvas.find_withtag("slider_oval_2_4_a") and height > 2 * button_corner_radius:
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_4_a", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_4_b", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_oval_2_4_a") and not height > 2 * button_corner_radius:
            self._canvas.delete("slider_oval_2_4_a", "slider_oval_2_4_b")

        if not self._canvas.find_withtag("slider_oval_2_3_a") and button_length > 0 and height > 2 * button_corner_radius:
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_3_a", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER)
            self._canvas.create_aa_circle(0, 0, 0, tags=("slider_oval_2_3_b", "slider_corner_part", "slider_parts", "slider_1_parts"), anchor=tkinter.CENTER, angle=180)
            requires_recoloring = True
        elif self._canvas.find_withtag("border_oval_2_3_a") and not (button_length > 0 and height > 2 * button_corner_radius):
            self._canvas.delete("slider_oval_2_3_a", "slider_oval_2_3_b")

        # create the 2 rectangles (if needed)
        if not self._canvas.find_withtag("slider_rectangle_2_1") and button_length > 0:
            self._canvas.create_rectangle(0, 0, 0, 0, tags=("slider_rectangle_2_1", "slider_rectangle_part", "slider_parts", "slider_1_parts"), width=0)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_rectangle_2_1") and not button_length > 0:
            self._canvas.delete("slider_rectangle_2_1")

        if not self._canvas.find_withtag("slider_rectangle_2_2") and height > 2 * button_corner_radius:
            self._canvas.create_rectangle(0, 0, 0, 0, tags=("slider_rectangle_2_2", "slider_rectangle_part", "slider_parts", "slider_1_parts"), width=0)
            requires_recoloring = True
        elif self._canvas.find_withtag("slider_rectangle_2_2") and not height > 2 * button_corner_radius:
            self._canvas.delete("slider_rectangle_2_2")

        # set positions of circles and rectangles
        if orientation == "w":
            slider_x_position = corner_radius + (button_length / 2) + (width - 2 * corner_radius - button_length) * slider_2_value
            self._canvas.coords("slider_oval_2_1_a", slider_x_position - (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_1_b", slider_x_position - (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_2_a", slider_x_position + (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_2_b", slider_x_position + (button_length / 2), button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_3_a", slider_x_position + (button_length / 2), height - button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_3_b", slider_x_position + (button_length / 2), height - button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_4_a", slider_x_position - (button_length / 2), height - button_corner_radius, button_corner_radius)
            self._canvas.coords("slider_oval_2_4_b", slider_x_position - (button_length / 2), height - button_corner_radius, button_corner_radius)

            self._canvas.coords("slider_rectangle_2_1",
                                slider_x_position - (button_length / 2), 0,
                                slider_x_position + (button_length / 2), height)
            self._canvas.coords("slider_rectangle_2_2",
                                slider_x_position - (button_length / 2) - button_corner_radius, button_corner_radius,
                                slider_x_position + (button_length / 2) + button_corner_radius, height - button_corner_radius)

        elif orientation == "s":
            slider_y_position = corner_radius + (button_length / 2) + (height - 2 * corner_radius - button_length) * (1 - slider_2_value)
            self._canvas.coords("slider_oval_2_1_a", button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_1_b", button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_2_a", button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_2_b", button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_3_a", width - button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_3_b", width - button_corner_radius, slider_y_position + (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_4_a", width - button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)
            self._canvas.coords("slider_oval_2_4_b", width - button_corner_radius, slider_y_position - (button_length / 2), button_corner_radius)

            self._canvas.coords("slider_rectangle_2_1",
                                0, slider_y_position - (button_length / 2),
                                width, slider_y_position + (button_length / 2))
            self._canvas.coords("slider_rectangle_2_2",
                                button_corner_radius, slider_y_position - (button_length / 2) - button_corner_radius,
                                width - button_corner_radius, slider_y_position + (button_length / 2) + button_corner_radius)

        if requires_recoloring:  # new parts were added -> manage z-order
            self._canvas.tag_raise("slider_parts")

        return requires_recoloring

class CTkRangeSlider(CTkBaseClass):
    """
    Range slider with rounded corners, border, number of steps, variable support, vertical orientation.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 master: any,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 corner_radius: Optional[int] = None,
                 button_corner_radius: Optional[int] = None,
                 border_width: Optional[int] = None,
                 button_length: Optional[int] = None,

                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 border_color: Union[str, Tuple[str, str]] = "transparent",
                 progress_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,

                 from_: int = 0,
                 to: int = 1,
                 state: str = "normal",
                 number_of_steps: Union[int, None] = None,
                 hover: bool = True,
                 command: Union[Callable[[float], None], Tuple[Callable[[float], None], Callable[[float], None]], None] = None,
                 variables: Union[Tuple[tkinter.Variable, tkinter.Variable], None] = None,
                 orientation: str = "horizontal",
                 **kwargs):

        # set default dimensions according to orientation
        if width is None:
            if orientation.lower() == "vertical":
                width = 16
            else:
                width = 200
        if height is None:
            if orientation.lower() == "vertical":
                height = 200
            else:
                height = 16

        # transfer basic functionality (bg_color, size, _appearance_mode, scaling) to CTkBaseClass
        super().__init__(master=master, bg_color=bg_color, width=width, height=height, **kwargs)

        # color
        self._border_color = self._check_color_type(border_color, transparency=True)
        self._fg_color = ThemeManager.theme["CTkSlider"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._progress_color = ThemeManager.theme["CTkSlider"]["progress_color"] if progress_color is None else self._check_color_type(progress_color, transparency=True)

        if button_color is None:
            self._button_color_0 = ThemeManager.theme["CTkSlider"]["button_color"] if button_color is None else self._check_color_type(button_color)
            self._button_color_1 = ThemeManager.theme["CTkSlider"]["button_color"] if button_color is None else self._check_color_type(button_color)
        else:
            if (type(button_color[0]) and type(button_color[1])) is tuple:
                self._button_color_0 = ThemeManager.theme["CTkSlider"]["button_color"] if button_color[0] is None else self._check_color_type(button_color[0])
                self._button_color_1 = ThemeManager.theme["CTkSlider"]["button_color"] if button_color[1] is None else self._check_color_type(button_color[1])
            else:
                self._button_color_0 = ThemeManager.theme["CTkSlider"]["button_color"] if button_color is None else self._check_color_type(button_color)
                self._button_color_1 = ThemeManager.theme["CTkSlider"]["button_color"] if button_color is None else self._check_color_type(button_color)
            
        self._button_hover_color = ThemeManager.theme["CTkSlider"]["button_hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        
        # shape
        self._corner_radius = ThemeManager.theme["CTkSlider"]["corner_radius"] if corner_radius is None else corner_radius
        self._button_corner_radius = ThemeManager.theme["CTkSlider"]["button_corner_radius"] if button_corner_radius is None else button_corner_radius
        self._border_width = ThemeManager.theme["CTkSlider"]["border_width"] if border_width is None else border_width
        self._button_length = ThemeManager.theme["CTkSlider"]["button_length"] if button_length is None else button_length        
        self._values = 0, 1  # initial values of slider in percent
        self._orientation = orientation
        self._hover_states = False, False
        self._hover = hover
        self._from_ = from_
        self._to = to
        self._number_of_steps = number_of_steps
        self._output_values = self._from_ + (self._values[0] * (self._to - self._from_)), self._from_ + (self._values[1] * (self._to - self._from_))

        if self._corner_radius < self._button_corner_radius:
            self._corner_radius = self._button_corner_radius

        # callback and control variables
        self._command = command
        self._variables: tuple[tkinter.Variable] = variables
        self._variable_callback_blocked = False
        self._variable_callback_name = [None, None]
        self._state = state
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = CTkCanvas(master=self,
                                highlightthickness=0,
                                width=self._apply_widget_scaling(self._desired_width),
                                height=self._apply_widget_scaling(self._desired_height))
        self._canvas.grid(column=0, row=0, rowspan=1, columnspan=1, sticky="nswe")
        self._draw_engine = CustomDrawEngine(self._canvas)
        
        self._create_bindings()
        self._set_cursor()
        self._draw()  # initial draw

        if self._variables is not None:
            self._variable_callback_name[0] = self._variables[0].trace_add("write", self._variable_callback)
            self._variable_callback_name[1] = self._variables[1].trace_add("write", self._variable_callback)
            self._variable_callback_blocked = True
            self.set([self._variables[0].get(), self._variables[1].get()], from_variable_callback=True)
            self._variable_callback_blocked = False
            
    def _create_bindings(self, sequence: Optional[str] = None):
        """ set necessary bindings for functionality of widget, will overwrite other bindings """
        if sequence is None or sequence == "<Enter>":
            self._canvas.bind("<Enter>", self._on_enter)
        if sequence is None or sequence == "<Motion>":
            self._canvas.bind("<Motion>", self._on_enter)
        if sequence is None or sequence == "<Leave>":
            self._canvas.bind("<Leave>", self._on_leave)
        if sequence is None or sequence == "<Button-1>":
            self._canvas.bind("<Button-1>", self._clicked)
        if sequence is None or sequence == "<B1-Motion>":
            self._canvas.bind("<B1-Motion>", self._clicked)
            
    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height))
        self._draw()

    def _set_dimensions(self, width=None, height=None):
        super()._set_dimensions(width, height)

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                              height=self._apply_widget_scaling(self._desired_height))
        self._draw()

    def _destroy(self):
        # remove variable_callback from variable callbacks if variable exists
        if self._variables is not None:
            self._variables[0].trace_remove("write", self._variable_callback_name)

        super().destroy()

    def _set_cursor(self):
        if self._state == "normal" and self._cursor_manipulation_enabled:
            if sys.platform == "darwin":
                self.configure(cursor="pointinghand")
            elif sys.platform.startswith("win"):
                self.configure(cursor="hand2")

        elif self._state == "disabled" and self._cursor_manipulation_enabled:
            if sys.platform == "darwin":
                self.configure(cursor="arrow")
            elif sys.platform.startswith("win"):
                self.configure(cursor="arrow")

    def _draw(self, no_color_updates=False):
        super()._draw(no_color_updates)
        
        if self._orientation.lower() == "horizontal":
            orientation = "w"
        elif self._orientation.lower() == "vertical":
            orientation = "s"
        else:
            orientation = "w"

        requires_recoloring = self._draw_engine.draw_rounded_slider_with_border_and_2_button(self._apply_widget_scaling(self._current_width),
                                                                                          self._apply_widget_scaling(self._current_height),
                                                                                          self._apply_widget_scaling(self._corner_radius),
                                                                                          self._apply_widget_scaling(self._border_width),
                                                                                          self._apply_widget_scaling(self._button_length),
                                                                                          self._apply_widget_scaling(self._button_corner_radius),
                                                                                          self._values[0],self._values[1], orientation)

        if no_color_updates is False or requires_recoloring:
            self._canvas.configure(bg=self._apply_appearance_mode(self._bg_color))

            if self._border_color == "transparent":
                self._canvas.itemconfig("border_parts", fill=self._apply_appearance_mode(self._bg_color),
                                       outline=self._apply_appearance_mode(self._bg_color))
            else:
                self._canvas.itemconfig("border_parts", fill=self._apply_appearance_mode(self._border_color),
                                       outline=self._apply_appearance_mode(self._border_color))

            self._canvas.itemconfig("inner_parts", fill=self._apply_appearance_mode(self._fg_color),
                                   outline=self._apply_appearance_mode(self._fg_color))

            if self._progress_color == "transparent":
                self._canvas.itemconfig("progress_parts", fill=self._apply_appearance_mode(self._fg_color),
                                       outline=self._apply_appearance_mode(self._fg_color))
            else:
                self._canvas.itemconfig("progress_parts", fill=self._apply_appearance_mode(self._progress_color),
                                       outline=self._apply_appearance_mode(self._progress_color))
            
            if (self._hover_states[0] and self._hover) is True:
                self._canvas.itemconfig("slider_0_parts",
                                       fill=self._apply_appearance_mode(self._button_hover_color),
                                       outline=self._apply_appearance_mode(self._button_hover_color))
            else:
                self._canvas.itemconfig("slider_0_parts",
                                       fill=self._apply_appearance_mode(self._button_color_0),
                                       outline=self._apply_appearance_mode(self._button_color_0))

            if (self._hover_states[1] and self._hover) is True:
                self._canvas.itemconfig("slider_1_parts",
                                       fill=self._apply_appearance_mode(self._button_hover_color),
                                       outline=self._apply_appearance_mode(self._button_hover_color))
            else:
                self._canvas.itemconfig("slider_1_parts",
                                       fill=self._apply_appearance_mode(self._button_color_1),
                                       outline=self._apply_appearance_mode(self._button_color_1))

    def _clicked(self, event=None):
        if self._state == "normal":

            if self._orientation.lower() == "horizontal":
                clickPos = self._reverse_widget_scaling(event.x / self._current_width)
                if clickPos < self._values[0] or abs(clickPos-self._values[0]) < abs(clickPos-self._values[1]):
                    if self._active_slider:
                        self._values = clickPos, self._values[1]
                else:
                    if not self._active_slider:
                        self._values = self._values[0], clickPos
                    
            else:
                clickPos = 1 - self._reverse_widget_scaling(event.y / self._current_height)
                if clickPos < self._values[0] or abs(clickPos-self._values[0]) < abs(clickPos-self._values[1]):
                    if self._active_slider:
                        self._values = clickPos, self._values[1]
                else:
                    if not self._active_slider:
                        self._values = self._values[0], clickPos

            self._values=[max(min(x, 1.), 0.) for x in self._values]

            self._output_values = (self._round_to_step_size(self._from_ + (self._values[0] * (self._to - self._from_))),
                                   self._round_to_step_size(self._from_ + (self._values[1] * (self._to - self._from_))))
            self._values = (self._output_values[0] - self._from_) / (self._to - self._from_), (self._output_values[1] - self._from_) / (self._to - self._from_)

            self._draw(no_color_updates=False)

            if self._variables is not None:
                self._variable_callback_blocked = True
                self._variables[0].set(round(self._output_values[0]) if isinstance(self._variables[0], tkinter.IntVar) else self._output_values[0])
                self._variables[1].set(round(self._output_values[1]) if isinstance(self._variables[1], tkinter.IntVar) else self._output_values[1])
                self._variable_callback_blocked = False

            if self._command is not None:
                if type(self._command) is tuple:
                    if self._active_slider:
                       self._command[0](self._output_values[0])
                    else:
                       self._command[1](self._output_values[1])
                else:
                    self._command(self._output_values)

    def _on_enter(self, event=0):
        if self._state == "normal":
            
            if self._orientation.lower() == "horizontal":
                enterPos = self._reverse_widget_scaling(event.x / self._current_width)
                if enterPos < self._values[0] or abs(enterPos-self._values[0]) <= abs(enterPos-self._values[1]):
                    highlightTag='slider_0_parts'
                    normalTag='slider_1_parts'
                    color = self._button_color_1
                    self._hover_states = True, False
                    self._active_slider = True
                else:
                    highlightTag='slider_1_parts'
                    normalTag='slider_0_parts'
                    color = self._button_color_0
                    self._hover_states = False, True
                    self._active_slider = False
            else:
                enterPos = 1 - self._reverse_widget_scaling(event.y / self._current_height)
                if enterPos < self._values[0] or abs(enterPos-self._values[0]) <= abs(enterPos-self._values[1]):
                    highlightTag='slider_0_parts'
                    normalTag='slider_1_parts'
                    color = self._button_color_1
                    self._hover_states = True, False
                    self._active_slider = True
                else:
                    highlightTag='slider_1_parts'
                    normalTag='slider_0_parts'
                    color = self._button_color_0
                    self._hover_states = False, True
                    self._active_slider = False
                    
            if self._hover:
                self._canvas.itemconfig(highlightTag,
                                       fill=self._apply_appearance_mode(self._button_hover_color),
                                       outline=self._apply_appearance_mode(self._button_hover_color))

            self._canvas.itemconfig(normalTag,
                                fill=self._apply_appearance_mode(color),
                                outline=self._apply_appearance_mode(color))

    def _on_leave(self, event=0):
        self._hover_states = False, False
        self._canvas.itemconfig("slider_0_parts",
                               fill=self._apply_appearance_mode(self._button_color_0),
                               outline=self._apply_appearance_mode(self._button_color_0))
        self._canvas.itemconfig("slider_1_parts",
                               fill=self._apply_appearance_mode(self._button_color_1),
                               outline=self._apply_appearance_mode(self._button_color_1))
        
    def _round_to_step_size(self, values):
        if self._number_of_steps is not None:
            step_size = (self._to - self._from_) / self._number_of_steps
            if type(values) is list:
                values = [self._to - (round((self._to - x) / step_size) * step_size) for x in values]
            else:
                values = self._to - (round((self._to - values) / step_size) * step_size)
            return values
        else:
            return values
    
    def get(self) -> float:
        return self._output_values

    def set(self, output_values: List[float], from_variable_callback=False):

        if self._from_ < self._to:
            output_values = [max(min(x, self._to), self._from_) for x in output_values]
        else:
            output_values = [max(min(x, self._from_), self._to) for x in output_values]
                
        self._output_values = self._round_to_step_size(output_values)
        self._values = ((self._output_values[0] - self._from_) / (self._to - self._from_),
                        (self._output_values[1] - self._from_) / (self._to - self._from_))

        self._draw(no_color_updates=False)

        if self._variables is not None and not from_variable_callback:
            self._variable_callback_blocked = True
            self._variables[0].set(round(self._output_values[0]) if isinstance(self._variables[0], tkinter.IntVar) else self._output_values[0])
            self._variables[1].set(round(self._output_values[1]) if isinstance(self._variables[1], tkinter.IntVar) else self._output_values[1])
            self._variable_callback_blocked = False

    def _variable_callback(self, var_name, index, mode):
        if not self._variable_callback_blocked:
            self.set([self._variables[0].get(),self._variables[1].get()], from_variable_callback=True)
            
    def bind(self, sequence: str = None, command: Callable = None, add: Union[str, bool] = True):
        """ called on the tkinter.Canvas """
        if not (add == "+" or add is True):
            raise ValueError("'add' argument can only be '+' or True to preserve internal callbacks")
        self._canvas.bind(sequence, command, add=True)

    def unbind(self, sequence: str = None, funcid: str = None):
        """ called on the tkinter.Label and tkinter.Canvas """
        if funcid is not None:
            raise ValueError("'funcid' argument can only be None, because there is a bug in" +
                             " tkinter and its not clear whether the internal callbacks will be unbinded or not")
        self._canvas.unbind(sequence, None)
        self._create_bindings(sequence=sequence)  # restore internal callbacks for sequence
    
    def configure(self, require_redraw=False, **kwargs):
        if "state" in kwargs:
            self._state = kwargs.pop("state")
            self._set_cursor()
            require_redraw = True

        if "fg_color" in kwargs:
            self._fg_color = self._check_color_type(kwargs.pop("fg_color"))
            require_redraw = True

        if "progress_color" in kwargs:
            self._progress_color = self._check_color_type(kwargs.pop("progress_color"), transparency=True)
            require_redraw = True

        if "button_color" in kwargs:
            self._button_color_0 = self._check_color_type(kwargs["button_color"])
            self._button_color_1 = self._check_color_type(kwargs.pop("button_color"))
            require_redraw = True

        if "button_hover_color" in kwargs:
            self._button_hover_color = self._check_color_type(kwargs.pop("button_hover_color"))
            require_redraw = True

        if "border_color" in kwargs:
            self._border_color = self._check_color_type(kwargs.pop("border_color"), transparency=True)
            require_redraw = True

        if "border_width" in kwargs:
            self._border_width = kwargs.pop("border_width")
            require_redraw = True

        if "from_" in kwargs:
            self._from_ = kwargs.pop("from_")

        if "to" in kwargs:
            self._to = kwargs.pop("to")

        if "number_of_steps" in kwargs:
            self._number_of_steps = kwargs.pop("number_of_steps")

        if "hover" in kwargs:
            self._hover = kwargs.pop("hover")

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "variables" in kwargs:
            if self._variables is not None:

                self._variables[0].trace_remove("write", self._variable_callback_name[0])
                self._variables[1].trace_remove("write", self._variable_callback_name[1])

            self._variables = kwargs["variables"]

            if self._variables is not None and self._variables != "":
                self._variable_callback_name[0] = self._variables[0].trace_add("write", self._variable_callback)
                self._variable_callback_name[1] = self._variables[1].trace_add("write", self._variable_callback)
                self.set([self._variables[0].get(), self._variables[1].get()], from_variable_callback=True)
            else:
                self._variables = None

            del kwargs["variables"]
            
        if "corner_radius" in kwargs:
            self._corner_radius = kwargs.pop("corner_radius")
            require_redraw = True

        if "button_corner_radius" in kwargs:
            self._button_corner_radius = kwargs.pop("button_corner_radius")
            require_redraw = True

        if "button_length" in kwargs:
            self._button_length = kwargs.pop("button_length")
            require_redraw = True
            
        super().configure(require_redraw=require_redraw, **kwargs)
        
    def cget(self, attribute_name: str) -> any:
        if attribute_name == "corner_radius":
            return self._corner_radius
        elif attribute_name == "button_corner_radius":
            return self._button_corner_radius
        elif attribute_name == "border_width":
            return self._border_width
        elif attribute_name == "button_length":
            return self._button_length

        elif attribute_name == "fg_color":
            return self._fg_color
        elif attribute_name == "border_color":
            return self._border_color
        elif attribute_name == "progress_color":
            return self._progress_color
        elif attribute_name == "button_color":
            return self._button_color_0
        elif attribute_name == "button_hover_color":
            return self._button_hover_color

        elif attribute_name == "from_":
            return self._from_
        elif attribute_name == "to":
            return self._to
        elif attribute_name == "state":
            return self._state
        elif attribute_name == "number_of_steps":
            return self._number_of_steps
        elif attribute_name == "hover":
            return self._hover
        elif attribute_name == "command":
            return self._command
        elif attribute_name == "variables":
            return self._variables
        elif attribute_name == "orientation":
            return self._orientation

        else:
            return super().cget(attribute_name)
        
    def focus(self):
        return self._canvas.focus()

    def focus_set(self):
        return self._canvas.focus_set()

    def focus_force(self):
        return self._canvas.focus_force()


# class App(ctk.CTk):
#     def __init__(self):
#         super().__init__()
#         ctk.set_default_color_theme("green")
#         self.title("Spinbox_sample")
#         self.geometry(f"{300}x{100}")

#         # Creating Main_Frame
#         self.main_frame = ctk.CTkFrame(self, width=510, height=290, corner_radius=0)
#         self.main_frame.grid(row=0, column=10, columnspan=10, rowspan=10, ipadx=5, ipady=0, padx=0, pady=0, sticky="nw")
#         self.main_frame.grid_rowconfigure(3, weight=1)

#         # Spinboxes
#         self.spinbox_hours = Spinbox(self.main_frame, width=105, start_value=16, step_size=2, 
#                                      min_value=8, max_value=38, command=self.on_spinbox_change)
#         self.spinbox_hours.grid(row=0, column=2, rowspan=1, ipadx=0, ipady=0, padx=0, pady=0)

#     def on_spinbox_change(self, value):
#         print(f"Spinbox value changed: {value}")




                
# if __name__ == "__main__":
#     app = App()
#     app.resizable(width=False, height=False)
#     app.mainloop()
        
# root = customtkinter.CTk()


# def on_color_picker_color_selected(event):
#     selected_color = combobox.get()
#     print(f'{selected_color}')



# combobox = customtkinter.CTkComboBox(root, border_width=0, width=90)
# combobox.pack(pady=30, padx=30)
# combobox.set('#FFFFFF')

# # Initialize the ComboBoxColorPicker
# color_picker = CustomColorPicker(combobox)
# color_picker.bind("<<ColorPickerColorSelected>>", on_color_picker_color_selected)




# root.mainloop()
