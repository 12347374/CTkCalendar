import customtkinter as ctk

from typing import Any, Union, Tuple

# --- Imports de fechas ---
import datetime
from babel.dates import get_day_names, get_month_names
from calendar_view import CalendarView
from selection_manager import SelectionManager
from event_manager import EventManager

# --- Constantes ---
DEFAULT_BTN: dict = {
    "fg_color": "transparent",
    "cursor": "hand2",
}

ARROW_BTN: dict = {
    **DEFAULT_BTN,
    "corner_radius": 0,
    "width": 25
}


class CTkCalendar(ctk.CTkFrame):
    def __init__(self,
        #Parametros del frame madre
        master: Any, width: int = 200, height: int = 200, corner_radius: Union[int, str, None] = 0, border_width: Union[int, str, None] = 0,
        bg_color:Union[str, Tuple[str, str]] = "transparent", border_color: Union[str, Tuple[str, str], None] = None, 
        background_corner_colors: Union[str, Tuple[str, str], None] = None, overwrite_preferred_drawing_method: Union[str, None] = None,
        #Parámetros del header frame
        header_color: Union[str, Tuple[str, str], None] = 'gray', header_font: Union[tuple, ctk.CTkFont, None] = None,
        header_text_color: Union[str, Tuple[str, str], None] = None, header_hover_color: Union[str, Tuple[str, str], None] = None,
        #Parámetros para el days frame
        fg_color: Union[str, Tuple[str, str], None] = None,
        days_fg_color: Union[str, Tuple[str, str], None] = 'white',
        disabled_days_fg_color: Union[str, Tuple[str, str], None] = 'gray70',
        today_fg_color: Union[str, Tuple[str, str], None] = 'lightblue',
        days_label_text_color: Union[str, Tuple[str, str], None] = None,
        selected_day_border_color: Union[str, Tuple[str, str], None] = None,
        days_font: Union[tuple, ctk.CTkFont, None] = None,
        day_number_font: Union[tuple, ctk.CTkFont, None] = None,
        # Lenguaje
        locale: str = 'en',
        
        **kwargs
    ):
        super().__init__(master=master, width=width, height=height, corner_radius=corner_radius, border_width=border_width, bg_color=bg_color,
                         fg_color=fg_color, border_color=border_color, background_corner_colors=background_corner_colors, # type: ignore
                         overwrite_preferred_drawing_method=overwrite_preferred_drawing_method, **kwargs
        )
        self.pack_propagate(False)
        self.grid_propagate(False)
        # --- Variables ---
        self.locale = locale
        self.current_date = datetime.date.today()
        self.current_month = self.current_date.month
        self.current_month_name = get_month_names('wide', locale=locale)[self.current_date.month]
        self.current_year = self.current_date.year
        self.days_name_abbr = get_day_names('abbreviated', locale=locale)
        l=[]
        for i in range(len(self.days_name_abbr)):
            l.append(self.days_name_abbr[i])
        self.days_name_abbr = l[-1:] + l[:-1]
        self.events: dict[datetime.date, list[dict]] = {}

        # --- Grid ---
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=1)  # días
        self.grid_columnconfigure(0, weight=1)

        self.fg_color = fg_color

        # --- Clases auxiliares ---
        self.event_manager = EventManager(self)
        self.selection_manager = SelectionManager(self)
        self.calendar_view = CalendarView(self)

        # --- Header ---
        self.header_color = header_color
        self.header_font = header_font
        self.header_text_color = header_text_color
        self.header_hover_color = header_hover_color
        self._header_frame()

        # --- Days ---
        self.days_font = days_font
        self.days_fg_color = days_fg_color
        self.disabled_days_fg_color = disabled_days_fg_color
        self.today_fg_color = today_fg_color
        self.days_label_text_color = days_label_text_color
        self.selected_day_border_color = selected_day_border_color
        self.day_number_font = day_number_font
        self._days_frame()

        # --- Configurar altura y evitar flicking ---
        self.update_idletasks()
        self.configure(height=self.winfo_reqheight(), width=self.winfo_reqwidth())

        self.calendar_view.fill_calendar()


    # --------------------------------------------------
    # -------------- [INTERFÁZ GRÁFICA] ----------------
    # --------------------------------------------------
    def _header_frame(self):
        """ Función para retornar el encabezado del calendario, está compuesto de 2 frames más, el frame de meses y el de años,
            para cambiar cada uno respectivamente.
        """
        self.header_frame = ctk.CTkFrame(master=self, fg_color=self.header_color, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky='ew')


        # --- Month Section ---
        self.month_frame = ctk.CTkFrame(master=self.header_frame, fg_color='transparent', corner_radius=0)
        self.month_frame.pack(side='left', padx=(10, 0))

        self.substract_month = ctk.CTkButton(master=self.month_frame, text='◀', **ARROW_BTN, text_color=self.header_text_color,
                                             hover_color=self.header_hover_color, command=lambda: self._change_month(-1))
        self.substract_month.grid(row=0, column=0, padx=(0, 5))
        
        self.month_label = ctk.CTkLabel(master=self.month_frame, text=self.current_month_name.title(), font=self.header_font, text_color=self.header_text_color, width=120)
        self.month_label.grid(row=0, column=1)
        self.add_month = ctk.CTkButton(master=self.month_frame, text='▶', **ARROW_BTN, text_color=self.header_text_color, hover_color=self.header_hover_color,
                                       command=lambda: self._change_month(+1))
        self.add_month.grid(row=0, column=2, padx=(5, 0))

        # --- Year Section ---
        self.year_frame = ctk.CTkFrame(master=self.header_frame, fg_color='transparent', corner_radius=0)
        self.year_frame.pack(side='right', padx=(0, 10), pady=2)

        self.substract_year = ctk.CTkButton(master=self.year_frame, text='◀', **ARROW_BTN, text_color=self.header_text_color, hover_color=self.header_hover_color,
                                            command=lambda: self._change_year(-1))
        self.substract_year.grid(row=0, column=0, padx=(0, 5))        
        self.year_label = ctk.CTkLabel(master=self.year_frame, text=str(self.current_year), font=self.header_font, text_color=self.header_text_color)
        self.year_label.grid(row=0, column=1)
        self.add_year = ctk.CTkButton(master=self.year_frame, text='▶', **ARROW_BTN, text_color=self.header_text_color, hover_color=self.header_hover_color,
                                      command=lambda: self._change_year(1))
        self.add_year.grid(row=0, column=2, padx=(5, 0))
    

    def _days_frame(self):
        """Función que retorna el frame de los días, compuesto por los nombres abreviados de los días junto con los 42 frames donde
        irán las fechas, llama a _fill_calendar para rellenar las celdas.
        """
        self.days_frame = ctk.CTkFrame(master=self, fg_color=self.fg_color, corner_radius=0)
        self.days_frame.grid(row=1, column=0, sticky='nsew')

        self.day_nums = []
        self.day_frames = []

        # --- Configurar columnas con uniformidad ---
        for j in range(7):
            # El parámetro 'uniform' garantiza que todas las columnas tengan exactamente el mismo ancho relativo
            self.days_frame.columnconfigure(index=j, weight=1, uniform="col")

        # --- Day Names ---
        for j in range(7):
            day_name = ctk.CTkLabel(master=self.days_frame, text=self.days_name_abbr[j].title(), font=self.days_font, text_color=self.days_label_text_color,
                                    height=0, width=0)
            # Fila 0 para los nombres de los días
            day_name.grid(row=0, column=j, sticky='ew', padx=1 if j == 0 else (0, 1), pady=2)

        # --- Configurar 6 filas para los días (filas 1 a 6) ---
        # uniform="row" fuerza que todas tengan igual altura incluso si un mes usa solo 5 filas
        for i in range(1, 7):
            self.days_frame.rowconfigure(index=i, weight=1, uniform="row")

            for j in range(7):
                padx = 1 if j == 0 else (0, 1)
                pady = (0, 1)

                # Celda de día
                day_frame = ctk.CTkFrame(master=self.days_frame, corner_radius=0, fg_color=self.days_fg_color, cursor='hand2', border_width=0,
                                         border_color=self.selected_day_border_color)
                day_frame.grid(row=i, column=j, padx=padx, pady=pady, sticky='nsew')
                day_frame.columnconfigure(index=0, weight=1)
                day_frame.rowconfigure(index=1, weight=1)

                # Número del día
                day_number = ctk.CTkLabel(master=day_frame, text='', font=self.day_number_font, cursor='hand2', height=0, width=0)
                day_number.grid(row=0, column=0, sticky='ew', padx=10, pady=(3, 0))

                # Bindings
                day_frame.bind('<Button-1>', self.selection_manager.handle_click)
                day_number.bind('<Button-1>', self.selection_manager.handle_click)

                # Atributos personalizados
                day_frame.date = None
                day_number.date = None
                day_frame.is_selected = False
                day_number.is_selected = False

                # Guardar referencias
                self.day_nums.append(day_number)
                self.day_frames.append(day_frame)


    # --------------------------------------------------
    # --------------- [FUNCIONAMIENTO] -----------------
    # --------------------------------------------------
    def _change_month(self, delta):
        self.calendar_view.change_month(delta)


    def _change_year(self, delta):
        self.calendar_view.change_year(delta)


    # --- Eventos ---
    def add_event(self, date_obj: datetime.date, name: str, desc: str, color: str):
        return self.event_manager.add_event(date_obj, name, desc, color)

    def add_event_range(self, start_date: datetime.date, end_date: datetime.date, name: str, desc: str, color: str):
        return self.event_manager.add_event_range(start_date, end_date, name, desc, color)

    def remove_event(self, date_obj: datetime.date, name: str):
        return self.event_manager.remove_event(date_obj, name)
    
    def get_events(self, date_obj: datetime.date):
        return self.event_manager.get_events(date_obj)

    # --- Visuales ---
    def _suspend_redraw(self):
        """Congela los repintados de widgets del calendario y header."""
        self.winfo_toplevel().tk.call('update', 'idletasks')
        self.header_frame.grid_propagate(False)
        self.days_frame.grid_propagate(False)


    def _resume_redraw(self):
        """Reanuda los repintados."""
        self.header_frame.grid_propagate(True)
        self.days_frame.grid_propagate(True)
        self.update_idletasks()


if __name__ == '__main__':
    import datetime
    ctk.set_appearance_mode('light')
    app=ctk.CTk()
    app.geometry('800x600')

    cal = CTkCalendar(
        master=app,
        # header_color='#2D66CA',
        # fg_color='#407EE4',
        # header_hover_color='#214C97',
        locale='es',
        #selected_day_border_color='#407EE4'
    )
    cal.pack(expand=True, fill='both')

    cal.add_event(date_obj=datetime.date(2025, 10, 28), name='Coco - Gustavo', desc='depto ocupado',color='red2')
    cal.add_event(date_obj=datetime.date(2025, 10, 28), name='Pepe - Andrea', desc='depto ocupado',color='green3')

    cal.add_event_range(start_date=datetime.date(2025, 11, 1), end_date=datetime.date(2025, 11, 7), name='Eco - Pepito', color='violet', desc='')


    app.mainloop()