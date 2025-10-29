import customtkinter as ctk

root = ctk.CTk()
frame = ctk.CTkScrollableFrame(root, height=100)
# set the height of the internal scrollbar to zero
# then it will be expanded vertically to the configured height of "frame"
frame._scrollbar.configure(height=0)
frame.pack()
root.mainloop()