import customtkinter as ctk

class SelectionManager:
    def __init__(self, calendar):
        self.calendar = calendar
        self.selected_day_frame = None


    def select_frame(self, frame: ctk.CTkFrame):
        self.clear_selection()
        frame.configure(border_width=3)
        frame.is_selected = True
        self.selected_day_frame = frame


    def deselect_frame(self, frame: ctk.CTkFrame):
        frame.configure(border_width=0)
        frame.is_selected = False
        if self.selected_day_frame is frame:
            self.selected_day_frame = None


    def clear_selection(self):
        if self.selected_day_frame is not None:
            self.deselect_frame(self.selected_day_frame)
            self.selected_day_frame = None


    def handle_click(self, event):
        widget = event.widget.master
        clicked_frame = widget if isinstance(widget, ctk.CTkFrame) else getattr(widget, 'master', None)
        date_obj = getattr(widget, 'date', None) or getattr(widget.master, 'date', None)

        if not date_obj:
            return
        if date_obj.month != self.calendar.current_month or date_obj.year != self.calendar.current_year:
            return

        if getattr(clicked_frame, 'is_selected', False):
            self.deselect_frame(clicked_frame)
            return
        else:
            self.select_frame(clicked_frame)
            print(date_obj)
            return date_obj
