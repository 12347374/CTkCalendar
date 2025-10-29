import customtkinter as ctk

from typing import Any, Union, Tuple

# --- Imports de fechas ---
import datetime
from datetime import timedelta
import calendar
from babel.dates import get_day_names, get_month_names
from dateutil.relativedelta import relativedelta


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
        header_color: Union[str, Tuple[str, str], None] = None, header_font: Union[tuple, ctk.CTkFont, None] = ('Segoe UI', 20, 'bold'),
        header_text_color: Union[str, Tuple[str, str], None] = 'white', header_hover_color: Union[str, Tuple[str, str], None] = None,
        #Parámetros para el days frame
        fg_color: Union[str, Tuple[str, str], None] = 'red',
        days_font: Union[tuple, ctk.CTkFont, None] = ('Segoe UI', 18),
        days_fg_color: Union[str, Tuple[str, str], None] = 'white',
        today_fg_color: Union[str, Tuple[str, str], None] = 'lightblue',
        days_label_text_color: Union[str, Tuple[str, str], None] = 'white',
        selected_day_fg_color: Union[str, Tuple[str, str], None] = 'cyan',
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

        # --- Header ---
        self.header_color = header_color
        self.header_font = header_font
        self.header_text_color = header_text_color
        self.header_hover_color = header_hover_color
        self._header_frame()

        # --- Days ---
        self.days_font = days_font
        self.days_fg_color = days_fg_color
        self.today_fg_color = today_fg_color
        self.days_label_text_color = days_label_text_color
        self.selected_day_fg_color = selected_day_fg_color
        self._days_frame()

        self.update_idletasks()
        self.configure(height=self.winfo_reqheight(), width=self.winfo_reqwidth())


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
        self.month_frame.pack(side='left', padx=(10, 0), pady=10)

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
        self.year_frame.pack(side='right', padx=(0, 10), pady=10)

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
            day_name = ctk.CTkLabel(master=self.days_frame, text=self.days_name_abbr[j].title(), font=self.days_font, text_color=self.days_label_text_color)
            # Fila 0 para los nombres de los días
            day_name.grid(row=0, column=j, sticky='ew', padx=2 if j == 0 else (0, 2), pady=(2, 4))

        # --- Configurar 6 filas para los días (filas 1 a 6) ---
        # uniform="row" fuerza que todas tengan igual altura incluso si un mes usa solo 5 filas
        for i in range(1, 7):
            self.days_frame.rowconfigure(index=i, weight=1, uniform="row")

            for j in range(7):
                padx = 2 if j == 0 else (0, 2)
                pady = (0, 2)

                # Celda de día
                day_frame = ctk.CTkFrame(
                    master=self.days_frame,
                    corner_radius=0,
                    fg_color=self.days_fg_color,
                    cursor='hand2',
                    border_width=0
                )
                day_frame.grid(row=i, column=j, padx=padx, pady=pady, sticky='nsew')
                day_frame.columnconfigure(index=0, weight=1)
                day_frame.rowconfigure(index=1, weight=1)

                # Número del día
                day_number = ctk.CTkLabel(
                    master=day_frame,
                    text='',
                    font=('Segoe UI', 14),
                    cursor='hand2',
                    height=0,
                    width=0
                )
                day_number.grid(row=0, column=0, sticky='ew', padx=10, pady=(3, 0))

                # Bindings
                day_frame.bind('<Button-1>', self._on_day_click)
                day_number.bind('<Button-1>', self._on_day_click)

                # Atributos personalizados
                day_frame.date = None
                day_number.date = None
                day_frame.is_selected = False
                day_number.is_selected = False

                # Guardar referencias
                self.day_nums.append(day_number)
                self.day_frames.append(day_frame)

        # Llenar el calendario inicial
        self._fill_calendar()


    # --------------------------------------------------
    # --------------- [FUNCIONAMIENTO] -----------------
    # --------------------------------------------------
    def _fill_calendar(self):
        """Función para rellenar las filas de _days_frame, calcula la info. del mes, el primer día visible y
           después muestra los 42 días, si un frame contiene la fecha de hoy, se coloreará distinto al resto
        """
        self.days_frame.grid_remove()
        self.update_idletasks()
        self.winfo_toplevel().tk.call("pack", "propagate", self._w, "0")
        # Limpiar frames previos (elimina cualquier evento o widget dentro)
        for frame in self.day_frames:
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    continue  # dejamos el número del día
                child.destroy()
            # Además, eliminamos referencia al contenedor de eventos si existía
            if hasattr(frame, "events_container") and frame.events_container is not None:
                frame.events_container.destroy()
                frame.events_container = None

        #Información del mes
        first_day_weekday, num_days = calendar.monthrange(self.current_year, self.current_month)
        first_day = datetime.date(self.current_year, self.current_month, 1)
        last_day_month = datetime.date(self.current_year, self.current_month, num_days)

        #Calcular primer día visible
        days_to_subtract = (first_day_weekday + 1) % 7
        start_date = first_day - timedelta(days=days_to_subtract)

        #Mostrar 4 semanas (42 días)
        current_date = start_date

        for i in range(len(self.day_nums)):
            self.day_nums[i].configure(text=current_date.day)

            self.day_frames[i].date = current_date
            self.day_nums[i].date = current_date

            # marcar si es hoy
            is_today = (current_date == datetime.date.today())
            self.day_frames[i].is_today = is_today
            self.day_nums[i].is_today = is_today

            if current_date < first_day or current_date > last_day_month:
                self.day_frames[i].configure(fg_color = 'gray85', cursor='arrow')
            else:
                if is_today:
                    self.day_frames[i].configure(fg_color=self.today_fg_color, cursor='hand2')
                else:
                    self.day_frames[i].configure(fg_color='white', cursor='hand2')

            self.day_frames[i].is_selected = getattr(self.day_frames[i], 'is_selected', False)

            current_date += timedelta(days=1)
            self.day_frames[i].grid_propagate(True)
            self._render_events_for_frame(self.day_frames[i])
        
        self.update_idletasks()
        self.winfo_toplevel().tk.call("pack", "propagate", self._w, "1")
        self.days_frame.grid()
        
        self.update_idletasks()
        self.after(10)


    def _change_month(self, delta_month):
        # Congelar actualizaciones visuales
        self.update_idletasks()
        self._suspend_redraw()

        # Actualizar lógica de fecha
        self.current_date += relativedelta(months=delta_month)
        self.current_month = self.current_date.month
        self.current_month_name = get_month_names('wide', locale=self.locale)[self.current_month]
        self.current_year = self.current_date.year

        # Actualizar header sin forzar repintado inmediato
        self.month_label.configure(text=self.current_month_name.title())
        self.year_label.configure(text=str(self.current_year))

        # Reactivar repintado y refrescar calendario de forma diferida
        self.after(30, self._resume_redraw)
        self.after(35, lambda: self._fill_calendar())


    def _change_year(self, delta_year):
        # Congelar actualizaciones visuales
        self.update_idletasks()
        self._suspend_redraw()

        # Actualizar lógica de fecha
        self.current_date += relativedelta(years=delta_year)
        self.current_month = self.current_date.month
        self.current_month_name = get_month_names('wide', locale=self.locale)[self.current_month]
        self.current_year = self.current_date.year

        # Actualizar header
        self.year_label.configure(text=str(self.current_year))
        self.month_label.configure(text=self.current_month_name.title())

        # Reactivar y refrescar calendario
        self.after(30, self._resume_redraw)
        self.after(35, lambda: self._fill_calendar())



    # --- Seleccionar una fecha ---
    def _select_frame(self, frame):
        frame.configure(border_width=3)
        frame.is_selected = True
        self.selected_day_frame = frame


    def _deselect_frame(self, frame):
        frame.configure(border_width=0)
        frame.is_selected = False
        if getattr(self, 'selected_day_frame', None) is frame:
            self.selected_day_frame = None

   
    def _clear_selection(self):
        if getattr(self, 'selected_day_frame', None) is not None:
            self._deselect_frame(self.selected_day_frame)
            self.selected_day_frame = None


    def _on_day_click(self, event):
        widget = event.widget.master

        clicked_frame = widget if isinstance(widget, ctk.CTkFrame) else getattr(widget, 'master', None)
        
        # intentar leer .date del widget (label) o del frame padre
        date_obj = getattr(widget, 'date', None)
        if date_obj is None and hasattr(widget, 'master'):
            date_obj = getattr(widget.master, 'date', None)

        if date_obj.month != self.current_month or date_obj.year != self.current_year:
            return
        
        if getattr(clicked_frame, 'is_selected', False):
            self._deselect_frame(clicked_frame)
        else:
            if getattr(self, 'selected_day_frame', None) is not None:
                self._deselect_frame(self.selected_day_frame)

            self._select_frame(clicked_frame)

        self.get_day_selected(date_obj)


    def get_day_selected(self, date_obj):
        print(date_obj.strftime('%Y-%m-%d'))
        return date_obj.strftime('%Y-%m-%d')


    # --- Añadir un evento ---
    def add_event(self, date_obj: datetime.date, name: str, color: str):
        """Añade un evento a una fecha y actualiza la UI si la fecha está visible."""
        if not isinstance(date_obj, datetime.date):
            raise TypeError("date_obj debe ser datetime.date")

        if not isinstance(name, str) or not name:
            raise ValueError("name debe ser un string no vacío")

        if not isinstance(color, str) or not color:
            raise ValueError("color debe ser un string con un color válido (hex o nombre)")

        ev = {"name": name, "color": color}

        self.events.setdefault(date_obj, []).append(ev)

        # Si la fecha está visible ahora, renderizamos su frame
        self._render_events_for_visible_date(date_obj)


    def _render_events_for_frame(self, frame: ctk.CTkFrame) -> None:
        """Renderiza la lista de eventos dentro del frame de un día. Si no hay eventos, elimina el contenedor."""
        date_obj = getattr(frame, "date", None)
        if date_obj is None or date_obj.month != self.current_month or date_obj.year != self.current_year:
            return
    
        events = self.events.get(date_obj, [])

        # eliminar contenedor existente si había (evita duplicados)
        container = getattr(frame, "events_container", None)
        if container is not None:
            try:
                container.destroy()
                print('hola')
            except Exception:
                print(Exception)
                pass
            frame.events_container = None

        # si no hay eventos para esa fecha, ya está
        if not events:
            return
        
        #contenedor de los eventos
        print(frame.cget('width'))
        ev_container = ctk.CTkScrollableFrame(master=frame, corner_radius=6, height=0, width=0, fg_color='transparent')
        ev_container._scrollbar.grid_forget()
        ev_container.grid(row=1, column=0, sticky='nsew', padx=3, pady=(0, 3))

        
        # Previene que el contenido redimensione el calendario
        inner = ev_container._parent_frame
        inner.grid_propagate(False)

        # Fijar altura dinámica según cantidad de eventos
        max_visible_events = 3
        event_count = len(events)  # suponiendo que la tengas
        event_height = 22
        target_height = min(event_count * event_height, max_visible_events * event_height + 8)

        ev_container.configure(height=target_height)
                
        frame.grid_propagate(False)

        #eventos del contenedor:
        for ev in events:
            # crea botón pequeño con el color del evento
            btn = ctk.CTkButton(master=ev_container,  text=ev["name"], fg_color=ev["color"], hover_color=ev["color"], text_color='white' if ev["color"] != 'white' else 'black',
                                corner_radius=4, height=20, anchor='w', command=lambda e=ev, d=date_obj: print(e, d))
            btn.pack(fill='x', pady=1, padx=(0, 5))


    def _render_events_for_visible_date(self, date_obj: datetime.date) -> None:
        """Busca el frame visible que corresponde a date_obj y lo renderiza (si está dentro de los 42 celdas visibles)."""
        for frame in self.day_frames:
            if getattr(frame, "date", None) == date_obj:
                self._render_events_for_frame(frame)
                break


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
    from datetime import date 
    ctk.set_appearance_mode('light')
    app=ctk.CTk()
    app.geometry('800x600')

    cal = CTkCalendar(
        master=app,
        header_color='#2D66CA',
        fg_color='#407EE4',
        header_hover_color='#214C97',
        locale='es',
        width=400,
        height=500
    )
    cal.pack(expand=True, fill='both')

    cal.add_event(date_obj=datetime.date(2025, 10, 28), name='Coco - Gustavo', color='pink')
    cal.add_event(date_obj=datetime.date(2025, 10, 28), name='Pepe - juanito', color='green')
    cal.add_event(date_obj=datetime.date(2025, 10, 28), name='Eco - pedrito', color='brown')
    cal.add_event(date_obj=datetime.date(2025, 10, 28), name='Evento 4', color='purple')

    cal.add_event(date_obj=datetime.date(2025, 11, 28), name='Evento 1', color='purple')


    app.mainloop()