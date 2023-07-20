import customtkinter as ct
import json, requests, os, ctypes, tkinter, webbrowser
from PIL import ImageTk, Image


notes = []
buttons = []
mode = 0

class WarningWindow(ct.CTkToplevel):
    def __init__(self, *args):
        super().__init__(*args)
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.geometry(f'300x200+{round(screensize[0] / 2) - 150}+{round(screensize[1] / 2) - 100}')
        self.title('Warning')
        self.resizable(False, False)
        self.focus()

        self.lbl = ct.CTkLabel(self, text='Необходим заголовок', width=250, height=100, font=ct.CTkFont(family='Time New Roman', size=24))
        self.lbl.grid(row=0, column=0, sticky='news', padx=25)

        self.ok_btn = ct.CTkButton(self, text='Ok!', width=76, height=35, command=self.close)
        self.ok_btn.grid(row=1, column=0, sticky='news', pady=(10, 0), padx=112)

    def close(self):
        self.destroy()


class Button():
    def __init__(self, *args, target, text, index):
        self.target = target
        self.text = text
        self.index = index
        self.btn = ct.CTkButton(self.target, text=self.text, command=self.open_note, width=365, height=50, anchor='center')

    def update_btn(self):
        self.btn.grid(row=self.index, column=0, pady=5, padx=(5, 10))

    def open_note(self):
        NoteWindow(open=True, index=self.index, type_command=1)


class NoteWindow(ct.CTkToplevel):
    def __init__(self, *args, open, index, type_command):
        super().__init__(*args)
        self.geometry('400x400')
        self.title('Note')
        self.attributes("-alpha", 0.95)
        self.wm_iconbitmap(f'{os.getcwd()}/notes/source/note.ico')
        self.bind('<Escape>', lambda x: self.destroy())
        self.resizable(False, False)
        self.focus()

        self.index = index

        self.note_title = ct.CTkEntry(self, width=380, height=35, placeholder_text='Note Title', justify='center', font=ct.CTkFont(family='Time New Roman', size=20))
        self.note_title.grid(row=0, column=0, padx=(5, 10))

        self.text = ct.CTkTextbox(self, width=380, height=315)
        self.text.grid(row=1, column=0, padx=(5, 10))

        self.frame = ct.CTkFrame(self, width=380, height=35)
        self.frame.grid(row=2, column=0, padx=(10, 10), pady=10)

        if (type_command == 0):
            self.save_btn = ct.CTkButton(self.frame, text='Save Note', width=380, height=35, command=self.save)
            self.text.insert('0.0', 'Note Text')
        else:
            self.save_btn = ct.CTkButton(self.frame, text='Edit Note', width=335, height=35, command=self.edit)
            self.del_btn = ct.CTkButton(self.frame, text='', command=self.delete_note, width=35, height=35, anchor='center', image=ImageTk.PhotoImage((Image.open(f"{os.getcwd()}/notes/source/delete.png")).resize((20, 20))))
            self.del_btn.grid(row=0, column=1)
        self.save_btn.grid(row=0, column=0, padx=(0, 10))

        if (open):
            title_to_insert = notes[self.index]['title']
            text_to_insert = notes[self.index]['description']
            self.note_title.insert('0', title_to_insert)
            self.text.insert('0.0', text_to_insert)

    def delete_note(self):
        global notes, app
        notes.pop(self.index)
        result = {'note': notes}
        with open(f"{os.getcwd()}/notes/note/note.json", 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False)
        app.update_note()
        self.destroy()

    def save(self):
        global notes, app
        if (self.note_title.get() != ''):
            note = {'title': self.note_title.get(), 'description': self.text.get("0.0", "end")}
            notes.append(note)
            result = {'note': notes}
            with open(f"{os.getcwd()}/notes/note/note.json", 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False)
            app.update_note()
            self.destroy()
        else:
            WarningWindow()
    
    def edit(self):
        global notes
        if (self.note_title.get() != ''):
            note = {'title': self.note_title.get(), 'description': self.text.get("0.0", "end")}
            notes[self.index] = note
            result = {'note': notes}
            with open(f"{os.getcwd()}/notes/note/note.json", 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False)
            app.update_note()
            self.destroy()
        else:
            WarningWindow()


class MainApp(ct.CTk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)
        self.geometry('400x600')
        self.attributes("-alpha", 0.95)
        self.wm_iconbitmap(f'{os.getcwd()}/notes/source/notes.ico')
        ct.set_default_color_theme(f'{os.getcwd()}/notes/source/settings/theme.json')
        self.bind('<Escape>', lambda x: self.destroy())

        self.main_page_func()
        self.update_note()
        self.update()

    def main_page_func(self):
        self.title('Notes')
        global notes

        self.main_page = ct.CTkFrame(self, width=400, height=600)
        self.main_page.grid(row=0, column=0)

        self.main_page.grid_rowconfigure(1, weight=1)
        self.main_page.grid_columnconfigure(0, weight=1)

        # up panel
        self.up_panel = ct.CTkFrame(self.main_page, width=400, height=35, fg_color='transparent')
        self.up_panel.grid(row=0, column=0, padx=10, pady=10, sticky="news")

        # plus btn
        self.plus = ct.CTkButton(self.up_panel, width=35, height=35, text='+', command=self.add_note)
        self.plus.grid(row=0, column=0, sticky="nes")
        # settings btn
        self.sett_image = ImageTk.PhotoImage((Image.open(f"{os.getcwd()}/notes/source/setting.png")).resize((20, 20)))
        self.settings_btn = ct.CTkButton(self.up_panel, width=35, height=35, text='', command=self.settings, image=self.sett_image)
        self.settings_btn.grid(row=0, column=2, sticky="nws")
        # search entry
        self.search_field = ct.CTkEntry(self.up_panel, placeholder_text='Search...', width=290, height=35)
        self.search_field.grid(row=0, column=1, sticky="ns", padx=10)

        self.search_btn = ct.CTkButton(self.search_field, width=27, height=27, text='', command=self.search, image=ImageTk.PhotoImage((Image.open(f"{os.getcwd()}/notes/source/search.png")).resize((20, 20))), bg_color='transparent')
        self.search_btn.grid(row=0, column=0, sticky='nse', padx=(4, 4), pady=(4, 4))

        # notes panel
        self.down_panel = ct.CTkScrollableFrame(self.main_page, width=400, height=545, fg_color='transparent')
        self.down_panel.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="news")

        with open(f"{os.getcwd()}/notes/note/note.json", 'r', encoding='utf-8') as file:
            notes = (json.load(file))['note']

    def add_note(self):
        self.new_note = NoteWindow(self, open=False, index=None, type_command=0)
    
    def update_note(self):
        global notes, buttons
        for i in range(len(buttons)):
            try:
                buttons[i].btn.destroy()
            except Exception:
                pass
        buttons.clear()
        for i in range(len(notes)):
            btn = Button(self, target=self.down_panel, text=notes[i]['title'], index=i)
            buttons.append(btn)
            btn.update_btn()

    def search(self):
        global notes, buttons
        for i in range(len(buttons)):
            buttons[i].btn.destroy()
        buttons.clear()
        for i in range(len(notes)):
            if (self.search_field.get()).lower() in (notes[i]['title']).lower():
                btn = Button(self, target=self.down_panel, text=notes[i]['title'], index=i)
                buttons.append(btn)
                btn.update_btn()
            elif self.search_field.get() == '':
                self.update_note()

    def settings(self):
        self.main_page.destroy()
        self.title('Settings')

        self.settings_page = ct.CTkFrame(self, width=400, height=600, fg_color='transparent')
        self.settings_page.grid(row=0, column=0)

        def ok():
            self.settings_page.destroy()
            self.main_page_func()
            self.update_note()
            self.update()
        def line_el(num_row):
            line = ct.CTkProgressBar(self.settings_page, width=380, height=2, orientation='horizontal')
            line.grid(row=num_row, column=0, sticky='news', padx=(10, 10), pady=(5, 10))
            line.set(0)
        def big_lbl(num_row, text, size):
            settings_general_lbl = ct.CTkLabel(self.settings_page, text=text, font=ct.CTkFont(family='Time New Roman', size=size), width=360, anchor='w')
            settings_general_lbl.grid(row=num_row, column=0, sticky='w', padx=(40, 0), pady=(5, 10))
        def switch(num_row):
            def switch_event():
                if (switch.get()):
                    switch.configure(text='On')
                else:
                    switch.configure(text='Off')
            switch = ct.CTkSwitch(self.settings_page, text='Off', command=switch_event, width=45, height=30)
            switch.grid(row=num_row, column=0, sticky='w', padx=(40, 0))
        def radios(num_row):
            global mode
            def radiobutton_event():
                global mode
                if (radio_var.get() == 0):
                    ct.set_appearance_mode("dark")
                    mode = 0
                elif (radio_var.get() == 1):
                    ct.set_appearance_mode("light")
                    mode = 1
                elif (radio_var.get() == 2):
                    ct.set_appearance_mode("system")
                    mode = 2
                self.update()
            radio_var = tkinter.IntVar(value=mode)
            radio_button_1 = ct.CTkRadioButton(master=self.settings_page, variable=radio_var, value=0, text='Dark', command=radiobutton_event)
            radio_button_1.grid(row=num_row, column=0, pady=5, padx=(40, 0), sticky='w')
            radio_button_2 = ct.CTkRadioButton(master=self.settings_page, variable=radio_var, value=1, text='Light', command=radiobutton_event)
            radio_button_2.grid(row=num_row + 1, column=0, pady=5, padx=(40, 0), sticky='w')
            radio_button_5 = ct.CTkRadioButton(master=self.settings_page, variable=radio_var, value=2, text='System', command=radiobutton_event)
            radio_button_5.grid(row=num_row + 4, column=0, pady=5, padx=(40, 0), sticky='w')
        def redirect():
            webbrowser.open('https://github.com/DkFighT', new = 2)
        big_lbl(0, 'General', 20)
        big_lbl(1, 'Синхронизация (в разработке)', 16)
        switch(2)
        line_el(3)
        big_lbl(4, 'Color Themes', 20)
        radios(5)
        line_el(10)
        big_lbl(11, 'Creators', 20)
        big_lbl(12, 'DkFight', 16)
        line_el(13)
        big_lbl(14, 'About', 20)
        git_btn = ct.CTkButton(self.settings_page, text='GitHub: https://github.com/DkFighT', command=redirect, width=360, height=35, bg_color='transparent', fg_color='transparent', anchor='w', hover='diable', text_color='#029cff')
        git_btn.grid(row=15, column=0, padx=(40, 0), pady=(5, 10))

        self.close_btn = ct.CTkButton(self.settings_page, text='Apply', command=ok, width=100, height=35)
        self.close_btn.grid(row=16, column=0, pady=10, sticky='s')


def main():
    global app
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()


# Добавить настройку включения и отключения прозрачности