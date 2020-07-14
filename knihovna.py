from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Notebook, Treeview
import atexit
from database import Database
import re
# vytvoření pozadí + názvu aplikace
root = Tk()

class Library:
    """ Main class. Combines GUI, functionality and Database.

    Args:
        root (instance): tkinter's root instance.

    """
    appName = "Knihovna"
    appVersion = "0.2"

    tabList = [["Knihy", ["ID", "Název knihy", "Autor", "Ilustrátor", "Rok"]]]

    def __init__(self, root):
        """Initialises Library class.

        Args:
            root (instance): tkinter's root instance.

        """
        self.root = root
        self.root.geometry('1000x500')
        self.root.configure(background='#bdc3c7')
        self.root.minsize(1000, 500)
        self.root.title(Library.appName+" v"+Library.appVersion)

        self.toplevel = None

        self.notebook = Autoresized_Notebook(self.root)

        self.tables = []
        self.tabs = []
        i = 0
        for tab in Library.tabList:
            tabframe = Frame(self.notebook)
            self.notebook.add(tabframe, text=f"{tab[0]}")

            # zjistí, který tab je právě otevřený a zavolá funkci windowCreate, které předá název tabu
            Button(tabframe, text='+', command=lambda: self.windowCreate(), height=1).pack(fill=X)

            if len(tab) >= 2:
                columnList = ""
                e = 0
                for columnName in tab[1]:
                    if e != 0:
                        columnList += ", "
                    columnList += f"{e}"
                    e = e + 1

                # + editovací tlačítko
                columnList += ", "+str((int(e)+1))

                self.treeview = Treeview(tabframe, columns=(columnList), show="headings", height=10)
                self.treeview.bind("<ButtonRelease-1>", self.bookEditBind)
                f = 0
                for columnName in tab[1]:
                    self.treeview.column(f, minwidth=0, width=150, anchor=N, stretch=TRUE)
                    self.treeview.heading(f, text=f"{columnName}", anchor=W)
                    f = f + 1
                i = i + 1

                self.treeview.column(f+1, minwidth=0, width=150, anchor=N, stretch=TRUE)
                self.treeview.heading(f+1, text="jiné", anchor=W)

                self.updateTable()

                self.tables.append(self.treeview.pack(fill=X, side=TOP, expand=1))

            Button(tabframe, text='Exit', command=root.destroy).pack(padx=100, pady=100)

        self.notebook.pack(fill=BOTH, expand=1)

    def windowCreate(self, id = None, deleteCallback = None):
        """Creates another window.

        Args:
            id (int): id of selected book (default None).
            deleteCallback (function): callback of inserted function.

        """
        if (self.toplevel is not None) and self.toplevel.exists == True:
            return

        self.toplevel = Window(self.root, id, saveNewBook = self.save, deleteBook = deleteCallback)

    def bookEditBind(self, event):
        """Binds event when clicking to 'edit' book info.

        Args:
            event (instance): event.

        """
        button = self.treeview.identify_column(event.x)
        region = self.treeview.identify_region(event.x, event.y)

        if button != '#6' or region != 'cell':
            return
        item = self.treeview.focus()
        id = self.treeview.item(item)['values'][0]
        self.windowCreate(id, self.delete)

    def getBooks(self):
        """Clears self.books, reselects book info and its metadata and reinserts itself to self.books."""
        self.books = []
        booksInfo = Database.select("SELECT * FROM books")
        for book in booksInfo:
            info = {
                    "ID": book[0],
                    "authors": [],
                    "illustrators": [],
                    "title": book[1],
                    "year": book[2]
            }
            meta = Database.select(f"SELECT meta.role, meta.name  FROM bookWorkers LEFT JOIN (SELECT workers.ID, (people.forename || ' ' || people.surname) as name, roles.name as role FROM workers LEFT JOIN people ON people.ID = workers.peopleID LEFT JOIN roles ON workers.roleID = roles.ID) meta ON bookWorkers.workersID = meta.ID WHERE bookID = {book[0]}")
            for person in meta:
                info[person[0]+"s"].append(person[1])

            self.books.append(info)

    def updateTable(self):
        """Deletes data from table and calls getBooks to reinsert data."""
        self.getBooks()
        self.treeview.delete(*self.treeview.get_children())

        for book in self.books:
            if (len(book["authors"]) >= 2):
                authors = ", ".join(book["authors"])
            else:
                authors = book["authors"][0]

            if (len(book["illustrators"]) >= 2):
                illustrators = ", ".join(book["illustrators"])
            elif not book["illustrators"]:
                illustrators = ""
            else:
                illustrators = book["illustrators"][0]
            self.treeview.insert("", END, values=(book["ID"], book["title"], authors, illustrators, book["year"], "upravit"))

    def delete(self, id):
        """Deletes selected book and updates table immediately after.

        Args:
            id (int): id of selected (edited) book.

        """
        Database.execute(f"DELETE FROM books WHERE ID = {id}")
        Database.execute(f"DELETE FROM bookWorkers WHERE bookID = {id}")
        self.updateTable()

    def save(self, data, id):
        """Saves data to Database using class of the same name.

        Args:
            data (array): example: [{'forename': 'dd', 'surname': 'dd'}], 'illustrators': [{'forename': 'dd', 'surname': 'dd'}], 'title': None, 'year': None}
            id (integer): id of selected book.

        """

        bookID = Database.execute(f"INSERT INTO books (title, year) VALUES ('{data['title']}', '{data['year']}')")

        for role in data["roles"]:
            for person in data["roles"][role]:
                personID = Database.select(f"SELECT ID FROM people WHERE forename = '{person['forename']}' AND surname = '{person['surname']}'")
                if not personID:
                    personID = Database.execute(f"INSERT INTO people (forename, surname) VALUES ('{person['forename']}', '{person['surname']}')")
                else:
                    personID = personID[0][0]

                workerID = Database.select(f"SELECT ID FROM workers WHERE peopleID = '{personID}' AND roleID = (SELECT ID FROM roles WHERE name = '{role}')")
                if not workerID:
                    workerID = Database.execute(f"INSERT INTO workers (peopleID, roleID) VALUES ({personID}, (SELECT ID FROM roles WHERE name = '{role}'))")
                else:
                    workerID = workerID[0][0]

                bookWorkerID = Database.select(f"SELECT ID FROM bookWorkers WHERE workersID = '{workerID}' AND roleID = (SELECT ID FROM roles WHERE name = '{role}')")
                if not bookWorkerID:
                    bookWorkerID = Database.execute(f"INSERT INTO bookWorkers (bookID, workersID) VALUES ('{bookID}', '{workerID}')")
                else:
                    bookWorkerID = bookWorkerID[0][0]
        self.updateTable()

class Window:
    """User interface of popup window (when editing, deleting,..).

    Args:
        root (instance): tkinter's root instance.
        id (int): id of selected book.
        saveNewBook (function): saves new books.
        deleteBook (function): deletes selected book.

    """
    def __init__(self, root, id, saveNewBook = None, deleteBook = None):
        """Initialises Window class.

        Args:
            root (instance): tkinter's root instance.
            id (int): id of selected book.
            saveNewBook (function): saves new books.
            deleteBook (function): deletes selected book.

        """

        self.saveData = {
                "authors": [],
                "illustrators": [],
                "title": None,
                "year": None
            }
        self.deleteBook = deleteBook
        self.saveNewBook = saveNewBook
        self.toplevel = Toplevel(root)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.windowClose)

        self.toplevel.configure(background='#bdc3c7')
        self.toplevel.geometry('1000x500')
        self.toplevel.minsize(1000, 500)
        self.toplevel.title(Library.appName+" v"+Library.appVersion+" - vkládání")

        self.exists = True

        self.windowFrame = Frame(self.toplevel)
        self.windowFrame.pack(fill=BOTH, expand=1)

        self.chooseFrame = Frame(self.toplevel)

        self.peopleNumber = 0
        self.forenameLabel = Label(self.chooseFrame, text='Jméno')
        self.forenameLabel.pack()
        self.forename = Entry(self.chooseFrame)
        self.forename.pack()

        self.surnameLabel = Label(self.chooseFrame, text='Příjmení')
        self.surnameLabel.pack()
        self.surname = Entry(self.chooseFrame)
        self.surname.pack()


        self.stringVar = StringVar(self.toplevel)

        options = ["autor", "ilustrátor"]

        self.optionmenu = OptionMenu(self.chooseFrame, self.stringVar, *options)
        self.optionmenu.pack()

        self.buttonBack = Button(self.chooseFrame, text="přidat", command=lambda: self.windowChooseInsert())
        self.buttonBack.pack()

        self.chooseList = Treeview(self.chooseFrame, columns=(1, 2, 3, 4, 5), show="headings", height=10)
        self.chooseList.pack()

        self.chooseList.column(1, minwidth=50, stretch=TRUE)
        self.chooseList.heading(1, text="ID", anchor=W)
        self.chooseList.column(2, minwidth=50, stretch=TRUE)
        self.chooseList.heading(2, text="Jméno", anchor=W)
        self.chooseList.column(3, minwidth=50, stretch=TRUE)
        self.chooseList.heading(3, text="Příjmení", anchor=W)
        self.chooseList.column(4, minwidth=50, stretch=TRUE)
        self.chooseList.heading(4, text="role", anchor=W)
        self.chooseList.column(5, minwidth=50, stretch=TRUE)
        self.chooseList.heading(5, text="edit", anchor=W)


        self.buttonBack = Button(self.chooseFrame, text="zpět", command=self.windowChooseClose)
        self.buttonBack.pack()

        self.windowContent()
        if id != None:
            book = Database.select(f"SELECT * FROM books WHERE ID = {id}")[0]
            self.titleEntry.insert(0, book[1])
            self.yearEntry.insert(0, book[2])


        self.buttonSave = Button(self.windowFrame, text="uložit", command=lambda: self.save(id))
        self.buttonSave.pack()

        self.buttonSave = Button(self.windowFrame, text="smazat", command=lambda: self.delete(id))
        self.buttonSave.pack()

    def windowContent(self):
        """Content of first popup window."""
        self.titleLabel = Label(self.windowFrame, text='název')
        self.titleLabel.pack()

        self.titleEntry = Entry(self.windowFrame)
        self.titleEntry.pack()

        self.yearLabel = Label(self.windowFrame, text='rok')
        self.yearLabel.pack()

        self.yearEntry = Entry(self.windowFrame)
        self.yearEntry.pack()

        self.workersButton = Button(self.windowFrame, text="Pracovníci", command=lambda: self.windowChooseOpen())
        self.workersButton.pack()

    def windowClose(self):
        """Closes popup window."""
        self.toplevel.destroy()
        self.exists = False

    def windowChooseOpen(self):
        """Opens new popup window if one doesnt exist when called."""
        if self.chooseFrame.winfo_ismapped():
            return
        else:
            if self.windowFrame.winfo_ismapped():
                self.windowFrame.pack_forget()
                self.chooseFrame.pack()

    def windowChooseClose(self):
        """Closes second popup window and opens the first one."""
        if self.chooseFrame.winfo_ismapped():
                self.chooseFrame.pack_forget()
                self.windowFrame.pack(fill=BOTH, expand=1)
        else:
            return

    def windowChooseInsert(self):
        """Gets data from inputs (authors, illustrators) and saves them to the 'people' table."""
        worker = self.stringVar.get()
        if not worker or not self.forename.get() or not self.surname.get():
            return
        if worker == "autor":
            arg = "authors"
        else:
            arg = "illustrators"
        for person in self.saveData[arg]:
            if person["forename"] == self.forename.get() and person["surname"] == self.surname.get():
                return
        self.saveData[arg].append({"forename": self.forename.get(), "surname": self.surname.get()})
        self.chooseList.insert("", END, values=(self.peopleNumber, self.forename.get(), self.surname.get(), worker, 'upravit'))

        self.forename.delete(0, END)
        self.surname.delete(0, END)

        self.peopleNumber += 1

    def delete(self, id):
        """Deletes selected book.

        Args:
            id (int): id of selected book.

        """
        if self.deleteBook != None:
            self.deleteBook(id)
        self.windowClose()

    def save(self, id):
        """Checks if inputs are filled with valid data and afterwards saves books and its metadata.

        Args:
            id (int): id of selected book.

        """
        authors = self.saveData["authors"]
        illustrators = self.saveData["illustrators"]
        title = self.titleEntry.get()
        year = self.yearEntry.get()

        data = {
            "title": title,
            "year": year,
            "roles": {
                "author": authors,
                "illustrator": illustrators
            }
        }

        # kniha nemusí mít ilustrátora
        if data["title"] == None or len(data["roles"]["author"]) == 0:
            messagebox.showerror("ERROR", "Před uložením je nutné vyplnit veškeré položky!")
            return
        elif data["year"] == None or re.search("\d{4}", data["year"]) == None:
            messagebox.showerror("ERROR", "Rok musí být ve formátu YYYY (např. 2020)")
            return
        if self.saveNewBook != None:
            self.saveNewBook(data, id)
            self.windowClose()

# http://code.activestate.com/recipes/580726-tkinter-notebook-that-fits-to-the-height-of-every-/
class Autoresized_Notebook(Notebook):
  def __init__(self, master=None, **kw):

    Notebook.__init__(self, master, **kw)
    self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

  def _on_tab_changed(self,event):
    event.widget.update_idletasks()

    tab = event.widget.nametowidget(event.widget.select())
    event.widget.configure(height=tab.winfo_reqheight())

if __name__ == "__main__":
    library = Library(root)
    root.mainloop()
