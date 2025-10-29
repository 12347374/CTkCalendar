import customtkinter as ctk
import datetime
from tooltip import ToolTip
import json


class EventManager:
    def __init__(self, calendar):
        self.calendar = calendar  # referencia al CalendarView o CTkCalendar
        self.events: dict[datetime.date, list[dict]] = {}
        self.tags: dict[str, dict] = {}  # {tag_name: {"color": str, "desc": str, "visible": bool}}

    # --------------------------------------------------
    # ----------------- [GESTIÓN DE TAGS] --------------
    # --------------------------------------------------
    def add_tag(self, tag_name: str, color: str = "#3A7FF6", desc: str = "", visible: bool = True):
        """Crea un nuevo tag con color, descripción y visibilidad inicial."""
        if not isinstance(tag_name, str) or not tag_name:
            raise ValueError("El nombre del tag debe ser un string no vacío.")
        if not isinstance(color, str) or not color:
            raise ValueError("El color debe ser un string válido (hex o nombre).")
        self.tags[tag_name] = {"color": color, "desc": desc, "visible": visible}


    def update_tag(self, tag_name: str, *, color: str | None = None, desc: str | None = None):
        """Modifica color o descripción de un tag existente."""
        if tag_name not in self.tags:
            raise KeyError(f"El tag '{tag_name}' no existe.")
        if color:
            self.tags[tag_name]["color"] = color
        if desc is not None:
            self.tags[tag_name]["desc"] = desc

        # Re-renderizar todos los eventos asociados al tag
        for date_obj, evs in self.events.items():
            if any(ev.get("tag") == tag_name for ev in evs):
                self.render_visible_date(date_obj)


    def remove_tag(self, tag_name: str, remove_events: bool = False):
        """Elimina un tag. Si remove_events=True, elimina también los eventos asociados."""
        if tag_name not in self.tags:
            return False

        del self.tags[tag_name]

        if remove_events:
            for date_obj in list(self.events.keys()):
                filtered = [ev for ev in self.events[date_obj] if ev.get("tag") != tag_name]
                if filtered:
                    self.events[date_obj] = filtered
                else:
                    del self.events[date_obj]
                self.render_visible_date(date_obj)

        return True


    # --------------------------------------------------
    # ---------------- [OCULTAR / MOSTRAR] -------------
    # --------------------------------------------------
    def hide_tag(self, tag_name: str):
        """Oculta todos los eventos del tag indicado."""
        if tag_name not in self.tags:
            raise KeyError(f"El tag '{tag_name}' no existe.")
        self.tags[tag_name]["visible"] = False
        self._rerender_tag(tag_name)


    def show_tag(self, tag_name: str):
        """Muestra todos los eventos del tag indicado."""
        if tag_name not in self.tags:
            raise KeyError(f"El tag '{tag_name}' no existe.")
        self.tags[tag_name]["visible"] = True
        self._rerender_tag(tag_name)


    def toggle_tag(self, tag_name: str):
        """Alterna la visibilidad del tag (oculto/visible)."""
        if tag_name not in self.tags:
            raise KeyError(f"El tag '{tag_name}' no existe.")
        current = self.tags[tag_name].get("visible", True)
        self.tags[tag_name]["visible"] = not current
        self._rerender_tag(tag_name)


    def _rerender_tag(self, tag_name: str):
        """Re-renderiza todas las fechas que contengan eventos del tag indicado."""
        for date_obj, evs in self.events.items():
            if any(ev.get("tag") == tag_name for ev in evs):
                self.render_visible_date(date_obj)


    # --------------------------------------------------
    # ------------------ [INSERCIÓN] -------------------
    # --------------------------------------------------
    def add_event(self, date_obj: datetime.date, name: str, desc: str, tag: str):
        """Añade un evento ligado a un tag (el color se toma del tag)."""
        if not isinstance(date_obj, datetime.date):
            raise TypeError("date_obj debe ser datetime.date")
        if not isinstance(name, str) or not name:
            raise ValueError("name debe ser un string no vacío")
        if tag not in self.tags:
            raise ValueError(f"El tag '{tag}' no existe. Debe crearse antes de usarlo.")

        ev = {"name": name, "desc": desc, "tag": tag}
        self.events.setdefault(date_obj, []).append(ev)
        self.render_visible_date(date_obj)


    def add_event_range(self, start_date: datetime.date, end_date: datetime.date, name: str, desc: str, tag: str):
        """Añade el mismo evento a todas las fechas en el rango [start_date, end_date]."""
        if not isinstance(start_date, datetime.date) or not isinstance(end_date, datetime.date):
            raise TypeError("start_date y end_date deben ser datetime.date")
        if end_date < start_date:
            raise ValueError("end_date no puede ser anterior a start_date")

        if tag not in self.tags:
            raise ValueError(f"El tag '{tag}' no existe.")

        current_date = start_date
        while current_date <= end_date:
            self.add_event(current_date, name, desc, tag)
            current_date += datetime.timedelta(days=1)


    def add_recurring_event(self, start_date: datetime.date, end_date: datetime.date, interval_days: int, name: str, desc: str, tag: str):
        """
        Crea un evento recurrente cada `interval_days` días entre start_date y end_date (inclusive).

        Ejemplo:
            add_recurring_event(2025-11-01, 2025-11-15, 3, "Ir al gimnasio", "", "salud")
            → creará eventos el 1, 4, 7, 10, 13, 15
        """
        if not all(isinstance(d, datetime.date) for d in (start_date, end_date)):
            raise TypeError("start_date y end_date deben ser datetime.date")
        if end_date < start_date:
            raise ValueError("end_date no puede ser anterior a start_date")
        if not isinstance(interval_days, int) or interval_days < 1:
            raise ValueError("interval_days debe ser un entero positivo")
        if tag not in self.tags:
            raise ValueError(f"El tag '{tag}' no existe.")

        current_date = start_date
        while current_date <= end_date:
            self.add_event(current_date, name, desc, tag)
            current_date += datetime.timedelta(days=interval_days)


    # --------------------------------------------------
    # ----------------- [ELIMINACIÓN] ------------------
    # --------------------------------------------------
    def remove_event(self, date_obj: datetime.date, name: str) -> bool:
        """Elimina un evento por nombre de una fecha específica."""
        if date_obj not in self.events:
            return False

        before = len(self.events[date_obj])
        self.events[date_obj] = [ev for ev in self.events[date_obj] if ev["name"] != name]
        after = len(self.events[date_obj])

        if not self.events[date_obj]:
            del self.events[date_obj]

        self.render_visible_date(date_obj)
        return after < before


    def clear_day(self, date_obj: datetime.date) -> bool:
        """
        Elimina todos los eventos de una fecha específica.
        Retorna True si había eventos y fueron eliminados, False si no había nada.
        """
        if not isinstance(date_obj, datetime.date):
            raise TypeError("date_obj debe ser datetime.date")

        if date_obj not in self.events:
            return False

        del self.events[date_obj]
        self.render_visible_date(date_obj)
        return True


    # --------------------------------------------------
    # ------------------ [CONSULTAS] -------------------
    # --------------------------------------------------
    def get_events(self, date_obj: datetime.date) -> list[dict]:
        """Retorna una lista de los eventos para la fecha indicada."""
        return self.events.get(date_obj, []).copy()


    def get_events_by_tag(self, tag: str) -> dict[datetime.date, list[dict]]:
        """Retorna un dict con todas las fechas que tienen eventos del tag indicado."""
        tagged = {}
        for date_obj, evs in self.events.items():
            matches = [ev for ev in evs if ev.get("tag") == tag]
            if matches:
                tagged[date_obj] = matches
        return tagged


    def get_upcoming_events(self, days_ahead: int = 7, from_date: datetime.date | None = None) -> list[tuple[datetime.date, dict]]:
        """
        Retorna una lista con los eventos que ocurren dentro de los próximos `days_ahead` días.
        
        Parámetros:
            days_ahead (int): cantidad de días hacia adelante desde `from_date` (por defecto, hoy).
            from_date (datetime.date | None): fecha base desde la cual buscar. Si no se pasa, se usa hoy.
        
        Retorna:
            list[tuple[datetime.date, dict]]: lista de tuplas (fecha, evento), ordenadas cronológicamente.
        """
        if not isinstance(days_ahead, int) or days_ahead < 1:
            raise ValueError("days_ahead debe ser un entero positivo.")
        
        if from_date is None:
            from_date = datetime.date.today()
        elif not isinstance(from_date, datetime.date):
            raise TypeError("from_date debe ser un objeto datetime.date.")
        
        end_date = from_date + datetime.timedelta(days=days_ahead)
        upcoming = []

        for date_obj, evs in self.events.items():
            if from_date <= date_obj <= end_date:
                # Filtrar eventos visibles (por tags activos)
                for ev in evs:
                    tag_info = self.tags.get(ev.get("tag"))
                    if not tag_info or tag_info.get("visible", True):
                        upcoming.append((date_obj, ev))

        # Ordenar cronológicamente
        upcoming.sort(key=lambda x: x[0])
        return upcoming
    

    def export_events(self, filepath: str) -> None:
        """
        Exporta todos los eventos y tags a un archivo JSON.
        Incluye nombre, descripción, tag, y color del tag.
        """
        data = {
            "tags": self.tags,
            "events": {
                date_obj.isoformat(): evs
                for date_obj, evs in self.events.items()
            }
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # --------------------------------------------------
    # ----------------- [RENDERIZADO] ------------------
    # --------------------------------------------------
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
        container = getattr(frame, "events_container", None)
        if container:
            container.destroy()
            frame.events_container = None

        if not events:
            return

        # Filtrar eventos visibles según su tag
        visible_events = [ev for ev in events if self.tags.get(ev["tag"], {}).get("visible", True)]
        if not visible_events:
            return

        ev_container = ctk.CTkScrollableFrame(master=frame, corner_radius=6, height=0, fg_color="transparent")
        ev_container._scrollbar.grid_forget()
        ev_container.grid(row=1, column=0, sticky="nsew", padx=(3, 4), pady=(0, 3))
        frame.events_container = ev_container

        inner = ev_container._parent_frame
        inner.grid_propagate(False)

        event_height = 22
        target_height = min(len(visible_events) * event_height, 3 * event_height + 8)
        ev_container.configure(height=target_height)
        frame.grid_propagate(False)

        for ev in visible_events:
            tag_info = self.tags.get(ev["tag"], {"color": "gray"})
            color = tag_info["color"]

            btn = ctk.CTkButton(
                master=ev_container,
                text=ev["name"],
                fg_color=color,
                hover_color=color,
                text_color="white" if color != "white" else "black",
                corner_radius=4,
                height=20,
                anchor="w",
                command=lambda e=ev, d=date_obj: print(e, d)
            )
            btn.pack(fill="x", pady=1, padx=(0, 5))
            ToolTip(btn, text=f"{ev['name']}\n{ev['desc']}\n[{ev['tag']}]")

