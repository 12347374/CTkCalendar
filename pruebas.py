import tkinter as tk
from tkcalendar import Calendar
import datetime

root = tk.Tk()
cal = Calendar(root, selectmode='day', showweeks=None)
cal.pack(expand=True, fill='both')

d = datetime.date(2025, 11, 1)

# crear dos eventos en la misma fecha
id1 = cal.calevent_create(d, 'Evento A', tags='tag_a')
id2 = cal.calevent_create(d, 'Evento B', tags='tag_b')

# configurar colores por tag
cal.tag_config('tag_a', background='red', foreground='white')
cal.tag_config('tag_b', background='blue', foreground='white')

# obtener eventos de una fecha
events_ids = cal.get_calevents(date=d)
print(events_ids)  # mostrará [id1, id2]

root.mainloop()