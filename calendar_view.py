import customtkinter as ctk
import datetime
import calendar
from datetime import timedelta
from babel.dates import get_month_names
from dateutil.relativedelta import relativedelta

class CalendarView:
    def __init__(self, calendar):
        self.calendar = calendar

    def fill_calendar(self):
        """Rellena los 42 días visibles en el calendario."""
        self.calendar.days_frame.grid_remove()
        self.calendar.update_idletasks()

        for frame in self.calendar.day_frames:
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    continue
                child.destroy()
            if hasattr(frame, "events_container") and frame.events_container is not None:
                frame.events_container.destroy()
                frame.events_container = None

        first_day_weekday, num_days = calendar.monthrange(self.calendar.current_year, self.calendar.current_month)
        first_day = datetime.date(self.calendar.current_year, self.calendar.current_month, 1)
        last_day_month = datetime.date(self.calendar.current_year, self.calendar.current_month, num_days)

        days_to_subtract = (first_day_weekday + 1) % 7
        start_date = first_day - timedelta(days=days_to_subtract)
        current_date = start_date

        for i, label in enumerate(self.calendar.day_nums):
            frame = self.calendar.day_frames[i]
            label.configure(text=current_date.day)
            frame.date = label.date = current_date

            is_today = (current_date == datetime.date.today())
            if current_date < first_day or current_date > last_day_month:
                frame.configure(fg_color=self.calendar.disabled_days_fg_color, cursor='arrow')
                label.configure(cursor='arrow')
            else:
                color = self.calendar.today_fg_color if is_today else 'white'
                frame.configure(fg_color=color, cursor='hand2')
                label.configure(cursor='hand2')

            self.calendar.event_manager.render_events_in_frame(frame)
            current_date += timedelta(days=1)

        self.calendar.days_frame.grid()
        self.calendar.update_idletasks()

    def change_month(self, delta_month: int):
        self.calendar.update_idletasks()
        self.calendar._suspend_redraw()
        self.calendar.current_date += relativedelta(months=delta_month)
        self.calendar.current_month = self.calendar.current_date.month
        self.calendar.current_year = self.calendar.current_date.year
        self.calendar.current_month_name = get_month_names('wide', locale=self.calendar.locale)[self.calendar.current_month]
        self.calendar.month_label.configure(text=self.calendar.current_month_name.title())
        self.calendar.year_label.configure(text=str(self.calendar.current_year))
        self.calendar.after(35, self.fill_calendar)


    def change_year(self, delta_year: int):
        self.calendar.update_idletasks()
        self.calendar._suspend_redraw()
        self.calendar.current_date += relativedelta(years=delta_year)
        self.calendar.current_month = self.calendar.current_date.month
        self.calendar.current_year = self.calendar.current_date.year
        self.calendar.current_month_name = get_month_names('wide', locale=self.calendar.locale)[self.calendar.current_month]
        self.calendar.year_label.configure(text=str(self.calendar.current_year))
        self.calendar.month_label.configure(text=self.calendar.current_month_name.title())
        self.calendar.after(35, self.fill_calendar)
