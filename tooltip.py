import customtkinter as ctk
import tkinter as tk

class ToolTip:
    """
    Un tooltip reutilizable para widgets de CustomTkinter o Tkinter.

    Ejemplo:
        btn = ctk.CTkButton(master=frame, text="Evento")
        ToolTip(btn, text="Detalles del evento aquí.")
    """

    def __init__(self, widget, text: str, delay: int = 500, wraplength: int = 250):
        self.widget = widget
        self.text = text
        self.delay = delay  # en milisegundos
        self.wraplength = wraplength
        self.tooltip_window = None
        self.after_id = None

        # Eventos del mouse
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)
        widget.bind("<Motion>", self._move)

    def _schedule(self, event=None):
        """Programa la aparición del tooltip."""
        self._cancel()
        self.after_id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        """Cancela el tooltip pendiente."""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def _show(self, event=None):
        """Muestra el tooltip."""
        if self.tooltip_window or not self.text:
            return

        # Crear una nueva ventana flotante sin borde
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)

        # Posición cerca del cursor
        x, y = self.widget.winfo_pointerxy()
        tw.wm_geometry(f"+{x + 12}+{y + 12}")

        # Contenedor visual (CTkFrame para mantener estilo)
        frame = ctk.CTkFrame(master=tw, corner_radius=6, fg_color="#2b2b2b")
        frame.pack(ipadx=8, ipady=4)

        label = ctk.CTkLabel(master=frame, text=self.text, justify="left", wraplength=self.wraplength, text_color="white", anchor="center")
        label.pack(expand=True, fill='both')

    def _move(self, event):
        """Recoloca el tooltip si el mouse se mueve mientras está visible."""
        if self.tooltip_window:
            x, y = self.widget.winfo_pointerxy()
            self.tooltip_window.wm_geometry(f"+{x + 12}+{y + 12}")

    def _hide(self, event=None):
        """Oculta el tooltip cuando el mouse sale."""
        self._cancel()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
