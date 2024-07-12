import os
import tkinter as tk
# precisei incluir esses de baixo porque importar o módulo como acima não importa TODAS as classes e métodos
from tkinter import font
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import colorchooser


global selected
selected = ""


def new_file(window, text_edit):
    text_edit.delete("1.0", tk.END)  # END é o EOF do C
    window.title("New file")


def open_file(window, text_edit):
    filepath = askopenfilename(filetypes=[("All Files", "*.*")])
    if not filepath:
        return
    text_edit.delete(1.0, tk.END)
    # arquivo sendo passado como objeto para f, como se f fosse um ponteiro para a stream do arquivo
    with open(filepath, "r") as f:
        content = f.read()
        text_edit.insert(tk.END, content)
    head, tail = os.path.split(filepath)  # para pegar só o nome do arquivo da string path
    window.title(tail)


def save_file(window, text_edit):
    filepath = asksaveasfilename(filetypes=[("Text Files", "*.txt")], defaultextension=".txt")
    if not filepath:
        return
    # arquivo sendo passado como objeto para f, como se f fosse um ponteiro para a stream do arquivo
    with open(filepath, "w") as f:
        content = text_edit.get(1.0, tk.END)
        f.write(content)
    head, tail = os.path.split(filepath)  # para pegar só o nome do arquivo da string path
    window.title(tail)


def cut_text(text_edit):
    global selected
    # copia
    if text_edit.selection_get():
        selected = text_edit.selection_get()
    # deleta
    text_edit.delete("sel.first", "sel.last")


def copy_text(text_edit):
    global selected
    if text_edit.selection_get():
        selected = text_edit.selection_get()


def paste_text(text_edit):
    global selected
    if selected:
        position = text_edit.index(tk.INSERT)
        text_edit.insert(position, selected)


def bold(text_edit):
    if text_edit.tag_ranges("sel"):  # apenas executa a função se houver algo selecionado
        # cria uma nova fonte com a fonte antiga + o negrito
        bold_font = font.Font(text_edit, text_edit.cget("font"))
        bold_font.configure(weight="bold")
        text_edit.tag_configure("bold", font=bold_font)
        current_tags = text_edit.tag_names("sel.first")
        if "bold" in current_tags:
            text_edit.tag_remove("bold", "sel.first", "sel.last")
        else:
            text_edit.tag_add("bold", "sel.first", "sel.last")


def italic(text_edit):
    if text_edit.tag_ranges("sel"):  # apenas executa a função se houver algo selecionado
        # cria uma nova fonte com a fonte antiga + o itálico
        italic_font = font.Font(text_edit, text_edit.cget("font"))
        italic_font.configure(slant="italic")
        text_edit.tag_configure("italic", font=italic_font)
        current_tags = text_edit.tag_names("sel.first")
        if "italic" in current_tags:
            text_edit.tag_remove("italic", "sel.first", "sel.last")
        else:
            text_edit.tag_add("italic", "sel.first", "sel.last")


def color(text_edit):
    my_color = colorchooser.askcolor()[1]  # a função devolve uma lista com uma tupla RGB em [0] e o valor HEX em [1]
    if my_color:
        if text_edit.tag_ranges("sel"):  # apenas executa a função se houver algo selecionado
            color_font = font.Font(text_edit, text_edit.cget("font"))
            text_edit.tag_configure("colored", font=color_font, foreground=my_color)
            current_tags = text_edit.tag_names("sel.first")
            if "colored" in current_tags:
                text_edit.tag_remove("colored", "sel.first", "sel.last")
            else:
                text_edit.tag_add("colored", "sel.first", "sel.last")


def find(text_edit, e):
    text_edit.tag_remove('found', '1.0', tk.END)
    s = e.get()
    if s:
        idx = "1.0"
        while True:
            idx = text_edit.search(s, idx, nocase=1, stopindex=tk.END)
            if not idx:
                break
            lastidx = "% s+% dc" % (idx, len(s))
            text_edit.tag_add("found", idx, lastidx)
            idx = lastidx
        text_edit.tag_config("found", foreground="red")


def main():
    window = tk.Tk()
    window.title("Text Editor")
    window.geometry('796x600')
    window.rowconfigure(1, minsize=400)
    window.columnconfigure(0, minsize=500)

    # lista com as fontes que escolhi, cada uma com um tamanho
    # porque quando troca o tamanho da fonte a janela de texto muda junto (já que é medida em linhas, não em pixels)
    font_list = [("Arial", 32), ("Calibri", 36), ("Comic Sans MS", 30), ("Times New Roman", 36), ("System", 32)]

    # criando o frame para a barra de botões (frame criado primeiro fica em cima)
    frame_bar = tk.Frame(window)
    frame_bar.pack(fill=tk.X)

    # criando o frame
    frame = tk.Frame(window)
    frame.pack(pady=5)

    # criando a barra de scroll
    text_scroll = tk.Scrollbar(frame)
    text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # criando a caixa de texto
    text_edit = tk.Text(frame, height=12, width=32, font=["Arial", 32], undo=True, yscrollcommand=text_scroll.set)
    text_edit.pack()

    # configurando o scroll
    text_scroll.config(command=text_edit.yview)

    # criar menu
    my_menu = tk.Menu(window)
    window.config(menu=my_menu)

    # file
    file_menu = tk.Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New    (Ctrl+N)", command=lambda: new_file(window, text_edit))
    file_menu.add_command(label="Open    (Ctrl+O)", command=lambda: open_file(window, text_edit))
    file_menu.add_command(label="Save    (Ctrl+S)", command=lambda: save_file(window, text_edit))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.quit)

    # edit
    edit_menu = tk.Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Cut    (Ctrl+X)", command=lambda: cut_text(text_edit))
    edit_menu.add_command(label="Copy    (Ctrl+C)", command=lambda: copy_text(text_edit))
    edit_menu.add_command(label="Paste    (Ctrl+V)", command=lambda: paste_text(text_edit))
    edit_menu.add_separator()
    edit_menu.add_command(label="Undo    (Ctrl+Z)", command=text_edit.edit_undo)
    edit_menu.add_command(label="Redo    (Ctrl+Y)", command=text_edit.edit_redo)

    # font
    font_menu = tk.Menu(my_menu, tearoff=False)
    my_menu.add_cascade(label="Fonts", menu=font_menu)
    font_menu.add_command(label=f"{font_list[0][0]}", command=lambda: text_edit.configure(font=(font_list[0])))
    font_menu.add_command(label=f"{font_list[1][0]}", command=lambda: text_edit.configure(font=(font_list[1])))
    font_menu.add_command(label=f"{font_list[2][0]}", command=lambda: text_edit.configure(font=(font_list[2])))
    font_menu.add_command(label=f"{font_list[3][0]}", command=lambda: text_edit.configure(font=(font_list[3])))
    font_menu.add_command(label=f"{font_list[4][0]}", command=lambda: text_edit.configure(font=(font_list[4])))

    # botões
    photo1 = tk.PhotoImage(file="bold.png")
    photo1 = photo1.subsample(25, 25)
    bold_button = tk.Button(frame_bar, text="Bold", image=photo1, command=lambda: bold(text_edit))
    bold_button.grid(row=0, column=0, padx=3)

    photo2 = tk.PhotoImage(file="italic.png")
    photo2 = photo2.subsample(25, 25)
    italic_button = tk.Button(frame_bar, text="Italic", image=photo2, command=lambda: italic(text_edit))
    italic_button.grid(row=0, column=1, padx=3)

    photo3 = tk.PhotoImage(file="color.png")
    photo3 = photo3.subsample(40, 40)
    color_button = tk.Button(frame_bar, text="Text Color", image=photo3, command=lambda: color(text_edit))
    color_button.grid(row=0, column=2, padx=3)

    # find
    e = tk.Entry(frame_bar, borderwidth=3)
    e.grid(row=0, column=3, padx=3)

    photo4 = tk.PhotoImage(file="lupa.png")
    photo4 = photo4.subsample(25, 25)
    find_button = tk.Button(frame_bar, text="Find", image=photo4, command=lambda: find(text_edit, e))
    find_button.grid(row=0, column=4, padx=3)

    window.bind("<Control-n>", lambda x: new_file(window, text_edit))
    window.bind("<Control-o>", lambda x: open_file(window, text_edit))
    window.bind("<Control-s>", lambda x: save_file(window, text_edit))
    window.bind("<Control-b>", lambda x: bold(text_edit))
    window.bind("<Control-i>", lambda x: italic(text_edit))
    window.bind("<Control-f>", lambda x: find(text_edit, e))
    # os comandos do "edit" não precisa bindar porque já vêm bindados automaticamente

    window.mainloop()


main()
