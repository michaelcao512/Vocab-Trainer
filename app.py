import random
import sqlite3
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import json
import os

class Database:
    @staticmethod
    def get_connection():
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        db_path = os.path.join(base_path, 'vocabulary.db')

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # SCHEMA
    """
        CREATE TABLE vocab_sets (
        set_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    );

    CREATE TABLE vocab (
        vocab_id INTEGER PRIMARY KEY,
        set_id INTEGER NOT NULL,
        word TEXT NOT NULL,
        definition TEXT NOT NULL,
        FOREIGN KEY (set_id) REFERENCES vocab_sets(set_id) ON DELETE CASCADE
    );
    
    """


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Vocabulary App")

        create_vocab_set_button = tk.Button(
            self.root, text="Create New Vocab Set", command=self.create_vocab_set)
        create_vocab_set_button.pack()

        delete_vocab_set_button = tk.Button(
            root, text="Delete Vocab Set", command=self.delete_vocab_set)
        delete_vocab_set_button.pack()

        self.display_vocab_sets()


        start_training_button = tk.Button(
            root, text="Start Training", command=self.start_training)
        start_training_button.pack()







    # FUNCTIONS
    # vocab sets in the format {name: (id, description)}
    def get_vocab_sets(self):
        with Database.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM vocab_sets")
            vocab_sets = c.fetchall()
            vocab_sets_ret = {vs[1]: (vs[0], vs[2]) for vs in vocab_sets}
            c.close()
            return vocab_sets_ret

    def display_vocab_sets(self):
        self.vocab_sets = self.get_vocab_sets()
        # Define a function to display the description when the user hovers over a set

        def show_set_description(event):
            index = self.vocab_sets_listbox.nearest(event.y)
            name = self.vocab_sets_listbox.get(index)
            if not name:
                return
            description = self.vocab_sets[name][1]
            # Update the description label with the selected set's description
            self.description_label.config(text=description)
        # Create a label for the listbox
        listbox_label = tk.Label(root, text="Select a vocabulary set:")
        listbox_label.pack()

        # Create a Listbox widget and add it to the window
        self.vocab_sets_listbox_frame = tk.Frame(self.root)
        self.vocab_sets_listbox_frame.pack()

        self.vocab_sets_listbox = tk.Listbox(
            self.vocab_sets_listbox_frame, height=5)
        for name in self.vocab_sets:
            self.vocab_sets_listbox.insert("end", name)
        self.vocab_sets_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        # Create a Scrollbar widget and associate it with the Listbox
        scrollbar = tk.Scrollbar(self.vocab_sets_listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the Listbox and Scrollbar to work together
        self.vocab_sets_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.vocab_sets_listbox.yview)
        # Create a label for the set description
        self.description_label = tk.Label(root, text="", wraplength=300)
        self.description_label.pack()

        # Bind the show_set_description function to the listbox's Enter event
        self.vocab_sets_listbox.bind("<Motion>", show_set_description)
        # Bind the edit_vocab_set function to the listbox's double-click event
        self.vocab_sets_listbox.bind("<Double-Button-1>", self.edit_vocab_set)

    def get_vocab_list(self, set_id):
        with Database.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM vocab WHERE set_id=?", (set_id,))
            vocab_list = c.fetchall()
            vocab_list_ret = {v[2]: v[3] for v in vocab_list}
            c.close()
            return vocab_list_ret
    def get_vocab_list_by_name(self, set_name):
        set_id = self.vocab_sets[set_name][0]
        return self.get_vocab_list(set_id)

    def refresh_vocab_sets(self):
        self.vocab_sets_listbox.delete(0, tk.END)
        self.vocab_sets = self.get_vocab_sets()
        for vs in self.vocab_sets:
            self.vocab_sets_listbox.insert("end", vs)
        self.description_label.config(text="")

    def delete_vocab_set(self):
        self.root.withdraw()
        DeleteVocabSetWindow(self.root, self.get_vocab_sets(), self)

    def create_vocab_set(self):
        self.root.withdraw()
        NewVocabSetWindow(self.root, self)

    def edit_vocab_set(self, event):
        index = event.widget.curselection()
        if not index:
            return
        set_name = event.widget.get(index[0])
        self.vocab_sets = self.get_vocab_sets()
        set_id = self.vocab_sets[set_name][0]
        set_description = self.vocab_sets[set_name][1]
        vocab_list = self.get_vocab_list(set_id)
        self.root.withdraw()
        EditVocabSetWindow(self.root, set_id, set_name,
                           set_description, vocab_list, self)


    def start_training(self):
       self.root.withdraw()
       StartTrainingWindow(self.root, self)

class NewVocabSetWindow:
    def __init__(self, parent, app):
        self.app = app
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("New Vocab Set")

        # ... (Title, Word, and Definition labels and entries, Listbox, etc.) ...
        title_label = tk.Label(self.window, text="Title:")
        title_label.grid(row=0, column=0)
        self.title_entry = tk.Entry(self.window)
        self.title_entry.grid(row=0, column=1)

        set_description_label = tk.Label(self.window, text="Set Description:")
        set_description_label.grid(row=1, column=0)
        self.set_description_entry = tk.Entry(self.window)
        self.set_description_entry.grid(row=1, column=1)

        word_label = tk.Label(self.window, text="Word:")
        word_label.grid(row=2, column=0)
        self.word_entry = tk.Entry(self.window)
        self.word_entry.grid(row=2, column=1)

        def_label = tk.Label(self.window, text="Definition:")
        def_label.grid(row=3, column=0)
        self.def_entry = tk.Entry(self.window)
        self.def_entry.grid(row=3, column=1)

        # Create the Treeview and configure columns
        self.vocab_treeview = ttk.Treeview(
            self.window, columns=("Word", "Definition"), show="headings")
        self.vocab_treeview.heading("Word", text="Word")
        self.vocab_treeview.heading("Definition", text="Definition")
        self.vocab_treeview.column("Word", width=100)
        self.vocab_treeview.column("Definition", width=200)

        # Create the vertical scrollbar and associate it with the Treeview
        scrollbar = ttk.Scrollbar(
            self.window, orient="vertical", command=self.vocab_treeview.yview)
        self.vocab_treeview.configure(yscrollcommand=scrollbar.set)

        # Place the Treeview and scrollbar using grid geometry manager
        self.vocab_treeview.grid(row=4, column=0, columnspan=3, sticky='nsew')
        scrollbar.grid(row=4, column=2, sticky='nse')

        # BUTTONS
        # Add word button
        add_button = tk.Button(self.window, text="Add Word", command=lambda: self.add_vocab(
        ))
        add_button.grid(row=5, column=0)

        # Save button
        save_button = tk.Button(self.window, text="Save",
                                command=lambda: self.save_vocab())
        save_button.grid(row=5, column=1)

        # Cancel button
        cancel_button = tk.Button(
            self.window, text="Cancel", command=lambda: (self.window.destroy(), self.parent.deiconify()))
        cancel_button.grid(row=5, column=2)

    def add_vocab(self,):
        word = self.word_entry.get()
        definition = self.def_entry.get()

        # Save the word and definition to the treeview
        if not word or not definition:
            messagebox.showwarning(
                "Warning", "Please enter both a word and a definition.")
            return
        self.vocab_treeview.insert("", "end", values=(word, definition))

        # Clear the Entry widgets for the next word and definition
        self.word_entry.delete(0, tk.END)
        self.def_entry.delete(0, tk.END)

    def save_vocab(self):
        self.set_title = self.title_entry.get()
        if not self.set_title:
            messagebox.showwarning(
                "Warning", "Please enter a name for the set.")
            return
        self.set_description = self.set_description_entry.get()
        # Save the word and definition to the database
        with Database.get_connection() as conn:
            c = conn.cursor()
            vocab_set_titles = [name for name in self.app.get_vocab_sets()]
            if self.set_title in vocab_set_titles:
                messagebox.showwarning(
                    "Warning", "A set with that name already exists.")
                return
            c.execute(
                "INSERT INTO vocab_sets (name, description) VALUES (?, ?)", (self.set_title, self.set_description))
            conn.commit()
            set_id = c.lastrowid
            vocab_items = []
            for item in self.vocab_treeview.get_children():
                word = self.vocab_treeview.item(item)["values"][0]
                definition = self.vocab_treeview.item(item)["values"][1]
                vocab_items.append((set_id, word, definition))

            c.executemany(
                "INSERT INTO vocab (set_id, word, definition) VALUES (?, ?, ?)", vocab_items)
            conn.commit()
            c.close()
        self.app.refresh_vocab_sets()
        self.parent.deiconify()
        self.window.destroy()


class DeleteVocabSetWindow:
    def __init__(self, parent, vocab_sets, app):
        self.window = tk.Toplevel(parent)
        self.window.title("Delete Vocab Set")
        self.vocab_sets = vocab_sets
        self.app = app
        self.parent = parent


        self.vocab_sets_listbox = tk.Listbox(self.window, width=40)
        self.vocab_sets_listbox.grid(row=1, column=0, columnspan=2, sticky='nsew')
        scrollbar = ttk.Scrollbar(
            self.window, orient="vertical", command=self.vocab_sets_listbox.yview)
        self.vocab_sets_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='nse')

        for vocab_set in vocab_sets:
            self.vocab_sets_listbox.insert(tk.END, vocab_set)



        delete_button = tk.Button(self.window, text="Delete",
                                  command=lambda: self.delete_vocab_set())
        delete_button.grid(row=2, column=0)

        cancel_button = tk.Button(
            self.window, text="Cancel", command=lambda: (self.window.destroy(),self.parent.deiconify()))
        cancel_button.grid(row=2, column=1)

    def delete_vocab_set(self):
        index = self.vocab_sets_listbox.curselection()
        if not index:
            messagebox.showwarning(
                "Warning", "Please select a set to delete.")
            return
        set_name = self.vocab_sets_listbox.get(index)
        with Database.get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM vocab_sets WHERE name = ?", (set_name,))
            conn.commit()
            c.close()

        self.app.refresh_vocab_sets()
        self.window.destroy()


class EditVocabSetWindow:
    def __init__(self, parent, set_id, set_name, set_description, vocab_list, app):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Edit {set_name}")
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        self.set_name = set_name
        self.app = app
        self.parent = parent
        self.vocab_list = vocab_list
        self.set_id = set_id
        self.set_description = set_description

        # Rename set
        rename_label = tk.Label(self.window, text="Rename set:")
        rename_label.grid(row=0, column=0)
        self.rename_entry = tk.Entry(self.window)
        self.rename_entry.grid(row=0, column=1)
        self.rename_entry.insert(0, set_name)

        # Edit description
        description_label = tk.Label(self.window, text="Description:")
        description_label.grid(row=1, column=0)
        self.description_entry = tk.Entry(self.window)
        self.description_entry.grid(row=1, column=1)
        self.description_entry.insert(0, set_description)

        # Add vocab
        word_label = tk.Label(self.window, text="Word:")
        word_label.grid(row=2, column=0)
        self.word_entry = tk.Entry(self.window)
        self.word_entry.grid(row=2, column=1)

        def_label = tk.Label(self.window, text="Definition:")
        def_label.grid(row=3, column=0)
        self.def_entry = tk.Entry(self.window)
        self.def_entry.grid(row=3, column=1)

        # Create the Treeview 
        self.vocab_treeview = ttk.Treeview(
            self.window, columns=("Word", "Definition"), show="headings")
        self.vocab_treeview.heading("Word", text="Word")
        self.vocab_treeview.heading("Definition", text="Definition")
        self.vocab_treeview.column("Word", width=100)
        self.vocab_treeview.column("Definition", width=200)

        # Create the vertical scrollbar and associate it with the Treeview
        scrollbar = ttk.Scrollbar(
            self.window, orient="vertical", command=self.vocab_treeview.yview)
        self.vocab_treeview.configure(yscrollcommand=scrollbar.set)

        # Place the Treeview and scrollbar using grid geometry manager
        self.vocab_treeview.grid(row=4, column=0, columnspan=3, sticky='nsew')
        scrollbar.grid(row=4, column=2, sticky='nse')

        # Fill vocab_listbox with current vocab
        self.fill_vocab_treeview()

       # Delete word  (bind to right click)
        if sys.platform == "darwin":
            self.vocab_treeview.bind(
                    "<Button-2>", lambda event: self.delete_vocab_word(event))
        else:
            self.vocab_treeview.bind(
                    "<Button-3>", lambda event: self.delete_vocab_word(event))

        # Edit word  (bind to double click)
        self.vocab_treeview.bind(
            "<Double-Button-1>", lambda event: self.edit_vocab_word(event))

        # Add word button
        add_button = tk.Button(self.window, text="Add Word", command=lambda: self.add_vocab(
        ))
        add_button.grid(row=5, column=0)

        # Save button
        save_button = tk.Button(self.window, text="Save",
                                command=lambda: self.save_vocab())
        save_button.grid(row=5, column=1)

        # Cancel button
        cancel_button = tk.Button(
            self.window, text="Cancel", command=lambda: (self.window.destroy(), self.parent.deiconify()))
        cancel_button.grid(row=5, column=2)

    def rename_set(self, new_name):
        # Rename the set in the database
        with Database.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE vocab_sets SET name=? WHERE name=?",
                      (new_name, self.set_name))
            conn.commit()
            c.close()
        self.set_name = new_name
        self.window.title(f"Edit {new_name}")

    def edit_description(self, new_description):
        # Edit the description in the database
        with Database.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE vocab_sets SET description=? WHERE name=?",
                      (new_description, self.set_name))
            conn.commit()
            c.close()
        self.set_description = new_description

    def fill_vocab_treeview(self):
        for word in self.vocab_list:
            self.vocab_treeview.insert(
                "", tk.END, values=(word, self.vocab_list[word]))

    def add_vocab(self):
        # Add vocab to the set
        word = self.word_entry.get()
        definition = self.def_entry.get()
        self.vocab_treeview.insert("", tk.END, values=(word, definition))


    def edit_vocab_word(self, event):
        # Edit the selected vocab word
        row_id = self.vocab_treeview.identify_row(event.y)
        if not row_id:
            return
        
        # open a new edit window
        word = self.vocab_treeview.item(row_id)["values"][0]
        definition = self.vocab_treeview.item(row_id)["values"][1]
        editwindow = tk.Toplevel(self.window)
        editwindow.title("Edit Word")
        editwindow.grid_columnconfigure(0, weight=1)
        editwindow.grid_columnconfigure(1, weight=1)

        word_label = tk.Label(editwindow, text="Word:")
        word_label.grid(row=0, column=0)
        word_entry = tk.Entry(editwindow)
        word_entry.grid(row=0, column=1)
        word_entry.insert(0, word)

        def_label = tk.Label(editwindow, text="Definition:")
        def_label.grid(row=1, column=0)
        def_entry = tk.Entry(editwindow)
        def_entry.grid(row=1, column=1)
        def_entry.insert(0, definition)

        save_word_button = tk.Button(editwindow, text="Save", command=lambda: save_word(
            word_entry.get(), def_entry.get(), row_id))
        save_word_button.grid(row=2, column=0)

        cancel_button = tk.Button(editwindow, text="Cancel", command=editwindow.destroy)
        cancel_button.grid(row=2, column=1)
    
        def save_word(word, definition, row_id):
            self.vocab_treeview.item(row_id, values=(word, definition))
            editwindow.destroy()



    def delete_vocab_word(self, event):
        # Delete the selected vocab word
        row_id = self.vocab_treeview.identify_row(event.y)
        if not row_id:
            return
        self.vocab_treeview.delete(row_id)
        


    def save_vocab(self):
        # Save the vocab set

        vocab_items = []
        for item in self.vocab_treeview.get_children():
            word = self.vocab_treeview.item(item)["values"][0]
            definition = self.vocab_treeview.item(item)["values"][1]
            self.vocab_list[word] = definition
            vocab_items.append((self.set_id, word, definition))

        with Database.get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM vocab WHERE set_id=?", (self.set_id,))
            c.executemany(
                "INSERT INTO vocab (set_id, word, definition) VALUES (?, ?, ?)", vocab_items)
            
            c.execute("UPDATE vocab_sets SET name=?, description=? WHERE set_id=?", (self.rename_entry.get(), self.description_entry.get(), self.set_id))
            
            conn.commit()
            c.close()



        self.app.refresh_vocab_sets()
        self.parent.deiconify()
        self.window.destroy()



class StartTrainingWindow:
    def __init__(self, parent, app):
        self.settings_file_path = 'settings.json'
        self.default_settings ={
                "interval": 300,
                "number_of_words": 0,
            }
        
        self.settings = self.load_settings()
        self.app = app
        self.parent = parent

        self.window = tk.Toplevel(parent)
        self.window.title("Training")



# Settings
        self.settings_label = tk.Label(self.window, text="Settings", font=("Arial", 24))
        self.settings_label.grid(row=0, column=0)
        # create a dictionary that has reference to the setting entry
        self.entry_dict = {}
        for r, setting in enumerate(self.settings,1):
            setting_label = tk.Label(self.window, text=setting)
            setting_label.grid(row=r, column=0)
            setting_entry = tk.Entry(self.window)
            setting_entry.grid(row=r, column=1)
            setting_entry.insert(0, self.settings[setting])
            self.entry_dict[setting] = setting_entry


        self.default_settings_button = tk.Button(
            self.window, text="Default Settings", command=self.set_default_settings)
        self.default_settings_button.grid(row=r+1, column=0)

        self.save_settings_button = tk.Button(
            self.window, text="Save Settings", command=self.save_settings)
        self.save_settings_button.grid(row=r+1, column=1)


# display the vocab set
        self.vocab_label = tk.Label(self.window, text="Vocab Set", font=("Arial", 24))
        self.vocab_label.grid(row=0, column=2)
        self.vocab_set_listbox = tk.Listbox(self.window)
        self.vocab_set_listbox.grid(row=1, column=2, rowspan=r+1)
        self.display_vocab_sets()

        self.training_flag = False
        self.start_button = tk.Button(
            self.window, text="Start Training", command=self.start_training)
        self.start_button.grid(row=r+2, column=0)

        self.stop_button = tk.Button(
            self.window, text="Stop Training", command=self.stop_training,)
        self.stop_button.grid(row=r+2, column=1)

        self.cancel_button = tk.Button(
            self.window, text="Cancel", command=lambda: (self.stop_training(), self.window.destroy(), self.parent.deiconify()))
        self.cancel_button.grid(row=r+2, column=2)
        self.after_id = None


    def set_default_settings(self):
        self.reload_default_settings()
    
    def reload_default_settings(self):
        for setting in self.default_settings:
            self.entry_dict[setting].delete(0, tk.END)
            self.entry_dict[setting].insert(0, self.default_settings[setting])
    
    def reload_settings_from_file(self):
        self.settings = self.load_settings()
        for setting in self.settings:
            self.entry_dict[setting].delete(0, tk.END)
            self.entry_dict[setting].insert(0, self.settings[setting])


    def load_settings(self):
        if not os.path.exists(self.settings_file_path):
            settings = self.default_settings
            with open(self.settings_file_path, "w") as f:
                json.dump(settings, f, indent=4)
            return settings
        else:
            with open(self.settings_file_path, "r") as f:
                settings = json.load(f)
                return settings

    def save_settings(self):
        for setting in self.settings:
            self.settings[setting] = self.entry_dict[setting].get()
        with open(self.settings_file_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def display_vocab_sets(self):
        self.vocab_set_listbox.delete(0, tk.END)
        for set_title in self.app.get_vocab_sets():
            self.vocab_set_listbox.insert(tk.END, set_title)


    def schedule_next_popup(self):
        if self.training_flag:
            self.after_id = self.window.after(int(self.settings["interval"])*1000, self.show_popup)

    def show_popup(self):
        self.num_display = int(self.settings['number_of_words'])
        remaining = len(self.vocab_shuffle) - self.curr_index
        if self.num_display == 0:
            self.words_to_send = self.vocab_shuffle
            self.curr_index = 0
        elif self.num_display > remaining:
            self.words_to_send = self.vocab_shuffle[self.curr_index:]
            random.shuffle(self.vocab_shuffle)
            additoinal_words = self.num_display - remaining
            self.words_to_send.extend(self.vocab_shuffle[:additoinal_words])
            self.curr_index = additoinal_words
        else:
            self.words_to_send = self.vocab_shuffle[self.curr_index:self.curr_index+self.num_display]
            self.curr_index += self.num_display
        TestPopup(self.window, self.app, self.settings, self.set_title, self.words_to_send)
        self.schedule_next_popup()

    def start_training(self):
        if self.training_flag:
            messagebox.showwarning(
                "Warning", "Training is already in progress.")
        index = self.vocab_set_listbox.curselection()
        if not index:
            messagebox.showwarning(
                "Warning", "Please select a vocab set.")
            return
        self.set_title = self.vocab_set_listbox.get(index)
        self.window.title(f'Training - {self.set_title}')
        self.training_flag = True
        self.save_settings()
        self.vocab_shuffle = list(self.app.get_vocab_list_by_name(self.set_title).items())
        random.shuffle(self.vocab_shuffle)
        self.curr_index = 0
        self.show_popup()
        self.start_stats()
    

    def start_stats(self):
        stats_label = tk.Label(self.window, text="Stats", font=("Arial", 24))
        stats_label.grid(row=0, column=3)

        timer_frame = tk.Frame(self.window)
        timer_frame.grid(row=1, column=3)
        timer_label = tk.Label(timer_frame, text="Timer:", font=("Arial", 24))
        timer_label.grid(row=0, column=0)
        self.time_label = tk.Label(timer_frame, text="00:00:00", font=("Arial", 24))
        self.time_label.grid(row=0, column=1)
        self.update_timer()

    def update_timer(self):
        if not self.training_flag:
            return

        current_time_str = self.time_label.cget("text")
        hours, minutes, seconds = map(int, current_time_str.split(':'))
        current_time = hours * 3600 + minutes * 60 + seconds

        current_time += 1
        new_time_str = f"{current_time // 3600:02d}:{(current_time % 3600) // 60:02d}:{current_time % 60:02d}"
        self.time_label.config(text=new_time_str)
        self.time_after_id = self.window.after(1000, self.update_timer)
        
    def stop_training(self):
        if self.after_id is not None:
            self.window.after_cancel(self.after_id)
            self.after_id = None            
        self.training_flag = False
        self.window.title("Training")

class TestPopup:
    def __init__(self, parent, app, settings, set_title, words):
        self.window = tk.Toplevel(parent)
        self.window.title(F'Test Popup - {set_title}')
        self.settings = settings
        self.set_title = set_title
        self.parent = parent
        self.app = app
        self.vocab_list = words

        self.answer_entry_dict = {}
        for r, (vocab, definition) in enumerate(self.vocab_list):
            word_label = tk.Label(self.window, text=vocab)
            word_label.grid(row=r, column=0)
            word_entry = tk.Entry(self.window)
            word_entry.grid(row=r, column=1)
            self.answer_entry_dict[vocab] = word_entry

        self.check_button = tk.Button(
            self.window, text="Check", command=self.check_answer)
        self.check_button.grid(row=r+1, column=0)
    def check_answer(self):
        correct = 0
        for vocab, definition in self.vocab_list:
            if self.answer_entry_dict[vocab].get() == definition:
                correct += 1
        messagebox.showinfo("Result", f'You got {correct} out of {len(self.vocab_list)} correct.')
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
