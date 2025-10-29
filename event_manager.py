import customtkinter as ctk
import datetime
from tooltip import ToolTip

class EventManager:
    def __init__(self, calendar):
        self.calendar = calendar  # referencia al CalendarView o CTkCalendar
        self.events: dict[datetime.date, list[dict]] = {}


    def add_event(self, date_obj: datetime.date, name: str, desc: str, color: str):
        """Añade un evento a una fecha y actualiza la UI si la fecha está visible."""
        if not isinstance(date_obj, datetime.date):
            raise TypeError("date_obj debe ser datetime.date")
        if not isinstance(name, str) or not name:
            raise ValueError("name debe ser un string no vacío")
        if not isinstance(color, str) or not color:
            raise ValueError("color debe ser un string válido")

        ev = {"name": name, "desc": desc, "color": color}
        self.events.setdefault(date_obj, []).append(ev)
        self.render_visible_date(date_obj)


    def render_visible_date(self, date_obj: datetime.date):
        """Busca el frame visible que corresponde a date_obj y lo renderiza."""
        for frame in self.calendar.day_frames:
            if getattr(frame, "date", None) == date_obj:
                self.render_events_in_frame(frame)
                break


    def render_events_in_frame(self, frame: ctk.CTkFrame):
        """Renderiza los eventos dentro de un frame específico."""
        date_obj = getattr(frame, "date", None)
        if not date_obj or date_obj.month != self.calendar.current_month or date_obj.year != self.calendar.current_year:
            return

        events = self.events.get(date_obj, [])

        # Limpiar contenedor previo
        container = getattr(frame, "events_container", None)
        if container:
            container.destroy()
            frame.events_container = None

        if not events:
            return

        ev_container = ctk.CTkScrollableFrame(master=frame, corner_radius=6, height=0, fg_color="transparent")
        ev_container._scrollbar.grid_forget()
        ev_container.grid(row=1, column=0, sticky="nsew", padx=(3, 4), pady=(0, 3))
        frame.events_container = ev_container

        inner = ev_container._parent_frame 
        inner.grid_propagate(False)

        event_height = 22
        target_height = min(len(events) * event_height, 3 * event_height + 8)
        ev_container.configure(height=target_height)
        frame.grid_propagate(False)

        for ev in events:
            btn = ctk.CTkButton(
                master=ev_container,
                text=ev["name"],
                fg_color=ev["color"],
                hover_color=ev["color"],
                text_color="white" if ev["color"] != "white" else "black",
                corner_radius=4,
                height=20,
                anchor="w",
                command=lambda e=ev, d=date_obj: print(e, d)
            )
            btn.pack(fill="x", pady=1, padx=(0, 5))

            ToolTip(btn, text=ev["name"]+'\n'+ev["desc"])

    def add_event_range(self, start_date: datetime.date, end_date: datetime.date, name: str, desc: str, color: str):
        """
        Añade el mismo evento a todas las fechas en el rango [start_date, end_date].
        """
        if not isinstance(start_date, datetime.date) or not isinstance(end_date, datetime.date):
            raise TypeError("start_date y end_date deben ser objetos datetime.date")

        if end_date < start_date:
            raise ValueError("end_date no puede ser anterior a start_date")

        current_date = start_date
        while current_date <= end_date:
            self.add_event(current_date, name, desc, color)
            current_date += datetime.timedelta(days=1)

    def remove_event(self, date_obj: datetime.date, name: str) -> bool:
        """
        Elimina un evento por nombre de una fecha específica.
        Devuelve True si lo eliminó, False si no existía.
        """
        if date_obj not in self.events:
            return False

        before = len(self.events[date_obj])
        self.events[date_obj] = [ev for ev in self.events[date_obj] if ev["name"] != name]
        after = len(self.events[date_obj])

        # Si no quedaron eventos, limpiar la clave
        if not self.events[date_obj]:
            del self.events[date_obj]

        # Actualizar UI si visible
        self.render_visible_date(date_obj)

        return after < before


    def get_events(self, date_obj: datetime.date) -> list[dict]:
        """
        Retorna una lista de los eventos para la fecha indicada.
        Si no hay eventos, retorna una lista vacía.
        """
        return self.events.get(date_obj, []).copy()