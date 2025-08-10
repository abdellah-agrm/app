# date_entry.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import ttkbootstrap as ttk

class SafeDateEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        self._date_format = kwargs.pop('date_pattern', '%Y-%m-%d')
        self._date_var = tk.StringVar()
        super().__init__(master, textvariable=self._date_var, **kwargs)
        self.bind('<Button-1>', self._show_date_picker)
        self.set_date(datetime.now())

    def _show_date_picker(self, event):
        from tkcalendar import Calendar
        top = tk.Toplevel(self)
        cal = Calendar(top, selectmode='day', date_pattern=self._date_format)
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="OK", command=lambda: self._set_date(cal)).pack(pady=5)

    def _set_date(self, calendar):
        self.set_date(calendar.get_date())
        calendar.master.destroy()

    def set_date(self, date):
        if isinstance(date, str):
            self._date_var.set(date)
        else:
            self._date_var.set(date.strftime(self._date_format))

    def get_date(self):
        return self._date_var.get()