import tkinter as tk
from tkinter import filedialog, Toplevel, simpledialog, Menu
from PIL import Image, ImageTk

def create_terminal_notepad():
    """
    Creates and runs the TerminalPad application.
    """
    # Create the main window
    root = tk.Tk()
    root.title("TerminalPad")
    root.geometry("800x600")

    # Define colors
    bg_color = "#000000"  # Black
    fg_color = "#00FF00"  # Green
    menu_bg = "#333333"  # Dark gray
    menu_fg = "#FFFFFF"  # White

    # Create a frame to hold the text area and line numbers
    text_frame = tk.Frame(root, bg=bg_color)
    text_frame.pack(expand=True, fill="both")

    # Create the line number widget
    line_numbers = tk.Text(
        text_frame,
        width=4,
        bg=bg_color,
        fg=fg_color,
        font=("Courier New", 12),
        padx=5,
        pady=5,
        takefocus=0,
        border=0,
        state="disabled",
    )
    line_numbers.pack(side="left", fill="y")

    # Create the main text widget
    text_area = tk.Text(
        text_frame,
        bg=bg_color,
        fg=fg_color,
        insertbackground=fg_color,
        font=("Courier New", 12),
        undo=True,  # Enable undo/redo
        wrap="word"  # Enable word wrapping
    )
    text_area.pack(side="right", expand=True, fill="both")

    # --- Functionality ---

    def update_line_numbers(event=None):
        """Updates the line numbers and adds the code symbol."""
        line_numbers.config(state="normal")
        line_numbers.delete("1.0", tk.END)
        num_lines = int(text_area.index("end-1c").split('.')[0])
        for i in range(1, num_lines + 1):
            line_numbers.insert(tk.END, f"{i} >\n")
        line_numbers.config(state="disabled")

    def scroll_text(event):
        """Scrolls the line numbers and text area together."""
        line_numbers.yview_moveto(text_area.yview()[0])

    def scroll_line_numbers(event):
        """Scrolls the line numbers and text area together."""
        text_area.yview_moveto(line_numbers.yview()[0])
        
    def save_file():
        """Saves the current text content to a file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        content = text_area.get(1.0, tk.END)
        with open(filepath, "w") as file:
            file.write(content)

    def open_file():
        """Opens a file and loads its content into the text area."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        text_area.delete(1.0, tk.END)
        with open(filepath, "r") as file:
            content = file.read()
        text_area.insert(1.0, content)
        update_line_numbers()

    def find_text():
        """Finds and highlights all occurrences of a string."""
        find_string = simpledialog.askstring("Find", "Enter text to find:")
        if find_string:
            start_pos = "1.0"
            text_area.tag_remove("found", "1.0", tk.END)
            while True:
                pos = text_area.search(find_string, start_pos, stopindex=tk.END)
                if not pos:
                    break
                end_pos = f"{pos}+{len(find_string)}c"
                text_area.tag_add("found", pos, end_pos)
                start_pos = end_pos
            text_area.tag_config("found", background="#FFFF00", foreground="#000000")

    def replace_text():
        """Replaces all occurrences of a string with a new string."""
        find_string = simpledialog.askstring("Replace", "Enter text to find:")
        if find_string:
            replace_string = simpledialog.askstring("Replace", "Enter replacement text:")
            if replace_string is not None:
                content = text_area.get(1.0, tk.END)
                new_content = content.replace(find_string, replace_string)
                text_area.delete(1.0, tk.END)
                text_area.insert(1.0, new_content)

    def select_all(event=None):
        """Selects all text in the text area."""
        text_area.tag_add("sel", "1.0", "end")
        return "break" # Prevents default system behavior

    def quick_copy():
        """Copies the selected text to the clipboard."""
        try:
            selected_text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            root.clipboard_clear()
            root.clipboard_append(selected_text)
        except tk.TclError:
            # Handle the case where no text is selected
            pass

    def insert_image():
        """Inserts an image into the text area."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        
        try:
            # Open and resize the image
            image = Image.open(filepath)
            image.thumbnail((200, 200)) # Resize to a max of 200x200
            
            # Keep a reference to the image to prevent it from being garbage collected
            # A dictionary on the text_area is a good place to store these references
            if not hasattr(text_area, 'image_references'):
                text_area.image_references = {}

            tk_image = ImageTk.PhotoImage(image)
            
            # Store the reference
            image_name = f"image_{len(text_area.image_references)}"
            text_area.image_references[image_name] = tk_image

            # Insert the image at the cursor's position
            text_area.image_create(tk.INSERT, image=tk_image)
            text_area.insert(tk.INSERT, "\n")
            update_line_numbers()

        except Exception as e:
            print(f"Error inserting image: {e}")
            tk.messagebox.showerror("Error", f"Failed to insert image: {e}")

    # --- Menus ---

    # Create a menu bar
    menu_bar = tk.Menu(root, bg=menu_bg, fg=menu_fg)

    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0, bg=menu_bg, fg=menu_fg)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Edit menu
    edit_menu = tk.Menu(menu_bar, tearoff=0, bg=menu_bg, fg=menu_fg)
    edit_menu.add_command(label="Undo", command=text_area.edit_undo)
    edit_menu.add_command(label="Redo", command=text_area.edit_redo)
    edit_menu.add_separator()
    edit_menu.add_command(label="Find", command=find_text)
    edit_menu.add_command(label="Replace All", command=replace_text)
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=select_all)
    edit_menu.add_command(label="Copy", command=quick_copy)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    
    # Media menu for images
    media_menu = Menu(menu_bar, tearoff=0, bg=menu_bg, fg=menu_fg)
    media_menu.add_command(label="Insert Image", command=insert_image)
    menu_bar.add_cascade(label="Media", menu=media_menu)

    # Attach the menu bar to the main window
    root.config(menu=menu_bar)

    # --- Keyboard Shortcuts ---
    root.bind("<Control-s>", lambda event: save_file())
    root.bind("<Control-o>", lambda event: open_file())
    root.bind("<Control-f>", lambda event: find_text())
    root.bind("<Control-a>", select_all)

    # Update line numbers on text change and scrolling
    text_area.bind("<Key>", update_line_numbers)
    text_area.bind("<BackSpace>", update_line_numbers)
    text_area.bind("<Return>", update_line_numbers)
    text_area.bind("<MouseWheel>", scroll_text)
    text_area.bind("<Button-4>", scroll_text)
    text_area.bind("<Button-5>", scroll_text)

    # Initial line number update
    update_line_numbers()

    # Start the application's main loop
    root.mainloop()

if __name__ == "__main__":
    create_terminal_notepad()