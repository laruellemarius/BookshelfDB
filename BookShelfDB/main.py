import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import sqlite3

from db import addBook, getBooks, deleteBook, updateStatus, toggleFavorite, updateBook


# ---------------- WINDOW ----------------

window = tk.Tk()
window.title("BookShelfDB")
window.geometry("900x600")


# ---------------- STATE ----------------

darkMode = False
currentSort = "id"
sortDirection = {}
history = []


# ---------------- HELPERS ----------------

def safeFloat(v):
    try:
        return float(v)
    except:
        return 0.0


def getSelected():
    sel = table.selection()
    if not sel:
        return None
    return table.item(sel[0], "values")


def saveStateSnapshot():
    history.append(getBooks())
    if len(history) > 20:
        history.pop(0)


# ---------------- THEME ----------------

def applyTheme():
    bg = "#1e1e1e" if darkMode else "#f0f0f0"
    fg = "white" if darkMode else "black"
    tableBg = "#2e2e2e" if darkMode else "white"

    window.configure(bg=bg)
    mainFrame.configure(bg=bg)

    titleLabel.configure(bg=bg, fg=fg)
    shortcutLabel.configure(bg=bg, fg=fg)

    for w in mainFrame.winfo_children():
        if isinstance(w, tk.Label):
            w.configure(bg=bg, fg=fg)
        elif isinstance(w, tk.Entry):
            w.configure(bg=tableBg, fg=fg, insertbackground=fg)
        elif isinstance(w, tk.OptionMenu):
            w.configure(bg=bg, fg=fg)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=tableBg,
        foreground=fg,
        fieldbackground=tableBg,
        rowheight=25
    )

    style.configure(
        "Treeview.Heading",
        background=bg,
        foreground=fg
    )


def toggleDark():
    global darkMode
    darkMode = not darkMode
    applyTheme()


# ---------------- HEADER ----------------

titleLabel = tk.Label(window, text="BookShelfDB", font=("Arial", 24, "bold"))
titleLabel.pack(pady=10)

shortcutLabel = tk.Label(
    window,
    text="Ctrl+Z Undo | Ctrl+D Dark Mode | File Menu for Save/Load"
)
shortcutLabel.pack()


# ---------------- MENU ----------------

menubar = tk.Menu(window)
window.config(menu=menubar)

fileMenu = tk.Menu(menubar, tearoff=0)
editMenu = tk.Menu(menubar, tearoff=0)

menubar.add_cascade(label="File", menu=fileMenu)
menubar.add_cascade(label="Edit", menu=editMenu)



def exportCSV():
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if not file:
        return

    books = getBooks()

    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id","name","author","genre","status","price","favorite"])
        writer.writerows(books)

    messagebox.showinfo("Export", "Done")


def saveDatabase():
    file = filedialog.asksaveasfilename(defaultextension=".json")
    if not file:
        return

    data = getBooks()

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    messagebox.showinfo("Save", "Backup saved")


def loadDatabase():
    file = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
    if not file:
        return

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect("books.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM books")

    for b in data:
        cur.execute("""
        INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)
        """, b)

    conn.commit()
    conn.close()

    refresh()
    messagebox.showinfo("Load", "Backup loaded")


fileMenu.add_command(label="Export CSV", command=exportCSV)
fileMenu.add_command(label="Save Backup", command=saveDatabase)
fileMenu.add_command(label="Load Backup", command=loadDatabase)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=window.destroy)

editMenu.add_command(label="Undo", command=lambda: undo())


# ---------------- MAIN FRAME ----------------

mainFrame = tk.Frame(window)
mainFrame.pack(fill="x", padx=10, pady=10)

mainFrame.grid_columnconfigure(1, weight=1)


# ---------------- INPUTS ----------------

tk.Label(mainFrame, text="Name").grid(row=0, column=0, sticky="w")
nameEntry = tk.Entry(mainFrame)
nameEntry.grid(row=0, column=1, sticky="ew")

tk.Label(mainFrame, text="Author").grid(row=1, column=0, sticky="w")
authorEntry = tk.Entry(mainFrame)
authorEntry.grid(row=1, column=1, sticky="ew")

tk.Label(mainFrame, text="Genre").grid(row=2, column=0, sticky="w")
genreEntry = tk.Entry(mainFrame)
genreEntry.grid(row=2, column=1, sticky="ew")

tk.Label(mainFrame, text="Status").grid(row=3, column=0, sticky="w")

statusVar = tk.StringVar(value="Unread")
tk.OptionMenu(mainFrame, statusVar, "Unread","Reading","Read","Lent").grid(row=3, column=1, sticky="ew")

tk.Label(mainFrame, text="Price").grid(row=4, column=0, sticky="w")
priceEntry = tk.Entry(mainFrame)
priceEntry.grid(row=4, column=1, sticky="ew")

tk.Label(mainFrame, text="Search").grid(row=5, column=0, sticky="w")
searchEntry = tk.Entry(mainFrame)
searchEntry.grid(row=5, column=1, sticky="ew")


# ---------------- TABLE ----------------

table = ttk.Treeview(
    window,
    columns=("id","name","author","genre","status","price","favorite"),
    show="headings"
)

table.pack(fill="both", expand=True, padx=10, pady=10)

for c in ("id","name","author","genre","status","price","favorite"):
    table.heading(c, text=c.upper())
    table.column(c, stretch=True)


# ---------------- REFRESH ----------------

def refresh():
    table.delete(*table.get_children())

    query = searchEntry.get().lower()
    books = getBooks()

    for b in books:
        if query in str(b).lower():
            table.insert("", "end", values=(
                b[0], b[1], b[2], b[3], b[4],
                f"{b[5]:.2f}",
                "★" if b[6] else "☆"
            ))


refresh()


# ---------------- ACTIONS ----------------

def add():
    addBook(
        nameEntry.get(),
        authorEntry.get(),
        genreEntry.get(),
        statusVar.get(),
        safeFloat(priceEntry.get())
    )
    refresh()


def deleteSelected():
    row = getSelected()
    if row:
        deleteBook(row[0])
        refresh()


def editBook():
    row = getSelected()
    if row:
        updateBook(
            row[0],
            nameEntry.get(),
            authorEntry.get(),
            genreEntry.get(),
            statusVar.get(),
            safeFloat(priceEntry.get())
        )
        refresh()


def toggleFav():
    row = getSelected()
    if row:
        toggleFavorite(row[0])
        refresh()


def editStatus():
    row = getSelected()
    if row:
        updateStatus(row[0], statusVar.get())
        refresh()


# ---------------- BUTTONS ----------------

tk.Button(mainFrame, text="Add", command=add).grid(row=6, column=0)
tk.Button(mainFrame, text="Delete", command=deleteSelected).grid(row=6, column=1)
tk.Button(mainFrame, text="Edit", command=editBook).grid(row=6, column=2)
tk.Button(mainFrame, text="Fav", command=toggleFav).grid(row=6, column=3)
tk.Button(mainFrame, text="Status", command=editStatus).grid(row=7, column=0)
tk.Button(mainFrame, text="Dark", command=toggleDark).grid(row=7, column=1)


# ---------------- SHORTCUTS ----------------

window.bind("<Control-z>", lambda e: undo())
window.bind("<Control-d>", lambda e: toggleDark())

def resetDatabase():
    confirm = messagebox.askyesno(
        "Reset Database",
        "This will DELETE ALL books permanently.\nAre you sure?"
    )

    if not confirm:
        return

    conn = sqlite3.connect("books.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM books")

    conn.commit()
    conn.close()

    refresh()

fileMenu.add_separator()
fileMenu.add_command(label="Reset Database", command=resetDatabase)
# ---------------- UNDO ----------------

def undo():
    if not history:
        return

    last = history.pop()

    conn = sqlite3.connect("books.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM books")

    for b in last:
        cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)", b)

    conn.commit()
    conn.close()
    refresh()


applyTheme()
window.mainloop()