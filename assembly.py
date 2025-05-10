import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import subprocess

class NanoEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("PyAssembly")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.50)}x{screen_height}")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_file = None
        self.is_modified = False
        
        # Create main layout
        self.create_menu()
        self.create_text_area()
        self.create_output_area()
        self.create_status_bar()
        self.create_help_bar()
        
        # Set up keyboard shortcuts
        self.bind_shortcuts()
        
    def create_menu(self):
        # Create menu frame
        self.menu_frame = ctk.CTkFrame(self, height=40)
        self.menu_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Add buttons to menu
        self.open_btn = ctk.CTkButton(self.menu_frame, text="Open (^O)", command=self.open_file, width=100)
        self.open_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(self.menu_frame, text="Save (^S)", command=self.save_file, width=100)
        self.save_btn.pack(side="left", padx=5)
        
        self.save_as_btn = ctk.CTkButton(self.menu_frame, text="Save As (^A)", command=self.save_as_file, width=100)
        self.save_as_btn.pack(side="left", padx=5)
        
        self.exit_btn = ctk.CTkButton(self.menu_frame, text="Exit (^X)", command=self.confirm_exit, width=100)
        self.exit_btn.pack(side="left", padx=5)

        self.run_btn = ctk.CTkButton(self.menu_frame, text="Run", command=self.run_code, width=100, fg_color="green")
        self.run_btn.pack(side="right", padx=5)
        
    def create_text_area(self):
        # Create text area frame
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create text widget with line numbers
        self.line_numbers = ctk.CTkTextbox(self.text_frame, width=30, font=("Courier", 12))
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.configure(state="disabled")
        
        # Create main text area
        self.text_area = ctk.CTkTextbox(self.text_frame, font=("Courier", 12), wrap="none")
        self.text_area.pack(side="left", fill="both", expand=True)
        
        # Bind text changes to update line numbers and modified status
        self.text_area.bind("<<Modified>>", self.on_text_modified)
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        
        # Initial line numbers
        self.update_line_numbers()
    
    def create_output_area(self):
        # Create output area frame
        self.output_frame = ctk.CTkFrame(self, height=100)
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Output text area
        self.output_area = ctk.CTkTextbox(self.output_frame, font=("Courier", 12), wrap="word")
        self.output_area.pack(fill="both", expand=True)
        
        # Allow resizing of the output area
        self.output_frame.pack_propagate(False)
        self.output_area.configure(state="normal")
        self.output_area.insert("1.0", "Output will be displayed here...\n")
        self.output_area.configure(state="disabled")
        
    def create_status_bar(self):
        # Create status bar frame
        self.status_frame = ctk.CTkFrame(self, height=30)
        self.status_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        # File info label
        self.file_label = ctk.CTkLabel(self.status_frame, text="No file opened")
        self.file_label.pack(side="left", padx=10)
        
        # Position info label
        self.position_label = ctk.CTkLabel(self.status_frame, text="Ln 1, Col 1")
        self.position_label.pack(side="right", padx=10)
        
        # Bind cursor position update
        self.text_area.bind("<ButtonRelease-1>", self.update_cursor_position)
        self.text_area.bind("<KeyRelease>", self.update_cursor_position)
        
    def create_help_bar(self):
        # Create help bar frame
        self.help_frame = ctk.CTkFrame(self, height=30)
        self.help_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Add help shortcuts
        shortcuts = [
            "^O: Open", "^S: Save", "^A: Save As", 
            "^X: Exit", "^K: Cut Line", "^U: Paste Line"
        ]
        
        for shortcut in shortcuts:
            label = ctk.CTkLabel(self.help_frame, text=shortcut)
            label.pack(side="left", padx=10)
    
    def bind_shortcuts(self):
        # Bind keyboard shortcuts
        self.bind("<Control-o>", lambda event: self.open_file())
        self.bind("<Control-s>", lambda event: self.save_file())
        self.bind("<Control-a>", lambda event: self.save_as_file())
        self.bind("<Control-x>", lambda event: self.confirm_exit())
        self.bind("<Control-k>", lambda event: self.cut_line())
        self.bind("<Control-u>", lambda event: self.paste_line())
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Assembly Files", "*.asm"),("Assembly Files", "*.s")]
        )
        
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    self.text_area.delete("1.0", "end")
                    self.text_area.insert("1.0", content)
                    self.current_file = file_path
                    self.file_label.configure(text=os.path.basename(file_path))
                    self.is_modified = False
                    self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get("1.0", "end-1c")
                with open(self.current_file, "w") as file:
                    file.write(content)
                self.is_modified = False
                self.file_label.configure(text=os.path.basename(self.current_file))
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Assembly Files", "*.asm"), ("Assembly Files", "*.s")]
        )
        
        if file_path:
            self.current_file = file_path
            self.save_file()
    
    def confirm_exit(self):
        if self.is_modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save changes before exiting?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_file()
        self.quit()


    # TODO: Add functionality to run the code on various platforms with different architectures 
    def run_code(self):
        try:
            # clear output area
            self.output_area.configure(state="normal")
            self.output_area.delete("1.0", "end")
            self.output_area.insert("1.0", "Output will be displayed here...\n")
            self.output_area.configure(state="disabled")
            # delete files
            os.remove("/Users/jainambarbhaya/Desktop/hello.o")
            os.remove("/Users/jainambarbhaya/Desktop/hello.out")
        except:
            pass
        # Save the current file if it exists
        if not self.current_file:
            messagebox.showerror("Error", "No file to run. Please save your code first.")
            return
        
        output_format = "macho64"  # Change to your desired output format
        file_name = os.path.splitext(self.current_file)[0]
        entry_point = "_main"  # Change to your desired entry point
        command = f"nasm -f macho64 /Users/jainambarbhaya/Desktop/hello.asm && ld -e _main -static /Users/jainambarbhaya/Desktop/hello.o -o /Users/jainambarbhaya/Desktop/hello.out && /Users/jainambarbhaya/Desktop/hello.out"
        
        try:
            # Compile the assembly code
            subprocess.run(command, shell=True, check=True)
            
            # Run the compiled output
            result = subprocess.run(f"{file_name}.out", shell=True, check=True, capture_output=True, text=True)
            
            # Display the output in the output area
            self.output_area.configure(state="normal")
            self.output_area.delete("1.0", "end")
            self.output_area.insert("1.0", f"\n{result.stdout}\n")
            self.output_area.configure(state="disabled")

        except subprocess.CalledProcessError as e:
            # Display errors in the output area
            self.output_area.configure(state="normal")
            self.output_area.delete("1.0", "end")
            self.output_area.insert("1.0", f"Error:\n{e.stderr if e.stderr else str(e)}\n")
            self.output_area.configure(state="disabled")
    
    def cut_line(self, event=None):
        current_line = self.text_area.index("insert").split(".")[0]
        line_content = self.text_area.get(f"{current_line}.0", f"{current_line}.end")
        
        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(line_content)
    
        self.text_area.delete(f"{current_line}.0", f"{int(current_line) + 1}.0")
        self.update_line_numbers()
        return "break"
    
    def paste_line(self, event=None):
        try:
            clipboard_content = self.clipboard_get()
            current_line = self.text_area.index("insert").split(".")[0]
            self.text_area.insert(f"{current_line}.0", clipboard_content + "\n")
            self.update_line_numbers()
        except:
            pass
        return "break"
    
    def on_text_modified(self, event=None):
        self.is_modified = True
        self.text_area.edit_modified(False)  # Reset modified flag
        
        # Update file label to show modified status
        if self.current_file:
            self.file_label.configure(text=f"{os.path.basename(self.current_file)} (modified)")
        else:
            self.file_label.configure(text="New File (modified)")
    
    def update_cursor_position(self, event=None):
        try:
            cursor_pos = self.text_area.index("insert")
            line, column = cursor_pos.split(".")
            self.position_label.configure(text=f"Ln {line}, Col {int(column) + 1}")
        except:
            pass
    
    def update_line_numbers(self, event=None):
        # Get total lines
        text_content = self.text_area.get("1.0", "end-1c")
        num_lines = text_content.count("\n") + 1
        
        # Update line numbers
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        for i in range(1, num_lines + 1):
            self.line_numbers.insert("end", f"{i}\n")
        
        self.line_numbers.configure(state="disabled")

if __name__ == "__main__":
    app = NanoEditor()
    app.mainloop()