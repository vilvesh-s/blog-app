import tkinter as tk
from tkinter import messagebox, Menu, Text, Toplevel, simpledialog
import mysql.connector
from datetime import datetime

def connect_db():
    """Establish a connection to the MySQL database."""
    try:
        return mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="tvmarun6",  
            database="blog_db"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

class BlogApp:
    def __init__(self, root):
        """Initialize the Blog Application."""
        self.root = root
        self.root.title("Blog App")
        self.root.geometry("700x500")
        self.root.protocol("WM_DELETE_WINDOW", self.exit_confirmation)
        self.db = connect_db()

        self.user_id = None
        self.login_page()

    def exit_confirmation(self):
        """Show exit confirmation dialog."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def login_page(self):
        """Display the login page."""
        self.clear_window()

        tk.Label(self.root, text="Login", font=("Arial", 20)).pack(pady=20)
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)
        
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show='*')
        self.password_entry.pack(pady=5)
        
        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.register_page).pack()

    def clear_window(self):
        """Clear all widgets from the current window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def register_page(self):
        """Display the registration page."""
        self.clear_window()

        tk.Label(self.root, text="Register", font=("Arial", 20)).pack(pady=20)
        tk.Label(self.root, text="Username:").pack()
        self.reg_username_entry = tk.Entry(self.root)
        self.reg_username_entry.pack(pady=5)
        
        tk.Label(self.root, text="Password:").pack()
        self.reg_password_entry = tk.Entry(self.root, show='*')
        self.reg_password_entry.pack(pady=5)
        
        tk.Button(self.root, text="Register", command=self.register).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.login_page).pack()

    def register(self):
        """Handle user registration."""
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.db.commit()
            messagebox.showinfo("Success", "Registration Successful!")
            self.login_page()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def login(self):
        """Handle user login."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor = self.db.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()

        if result:
            self.user_id = result[0]
            self.main_page()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    def main_page(self):
        """Display the main application page."""
        self.clear_window()

        tk.Label(self.root, text="Welcome to Blog App", font=("Arial", 20)).pack(pady=20)

        self.post_listbox = tk.Listbox(self.root, width=50)
        self.post_listbox.pack(pady=10)
        self.post_listbox.bind("<Double-Button-1>", self.view_post)

        tk.Button(self.root, text="Create Post", command=self.create_post).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.logout).pack(pady=5)

        self.load_posts()

    def load_posts(self):
        """Load blog posts from the database."""
        cursor = self.db.cursor()
        cursor.execute("SELECT title FROM posts WHERE user_id = %s", (self.user_id,))
        posts = cursor.fetchall()
        
        self.post_listbox.delete(0, tk.END)  # Clear the listbox
        for post in posts:
            self.post_listbox.insert(tk.END, post[0])  # Insert post titles

    def create_post(self):
        """Display the create post window with a drop-down menu for text functionalities."""
        self.clear_window()

        post_window = tk.Toplevel(self.root)
        post_window.title("Create Post")
        post_window.geometry("600x400")

        tk.Label(post_window, text="Create Post", font=("Arial", 20)).pack(pady=20)
        tk.Label(post_window, text="Title:").pack()
        title_entry = tk.Entry(post_window)
        title_entry.pack(pady=5)

        tk.Label(post_window, text="Content:").pack()
        content_text = Text(post_window, height=10, width=50)
        content_text.pack(pady=5)

        self.create_menu_bar(post_window, content_text)  # Create menu for text functions

        tk.Button(post_window, text="Save", command=lambda: self.save_post(title_entry, content_text)).pack(pady=10)
        tk.Button(post_window, text="Back", command=post_window.destroy).pack()

    def save_post(self, title_entry, content_text):
        """Save the new post to the database."""
        title = title_entry.get()
        content = content_text.get("1.0", tk.END)

        if not title or not content.strip():
            messagebox.showerror("Error", "Title and Content cannot be empty")
            return

        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO posts (title, content, user_id, created_at) VALUES (%s, %s, %s, %s)", 
                           (title, content.strip(), self.user_id, datetime.now()))
            self.db.commit()
            messagebox.showinfo("Success", "Post saved successfully!")
            self.load_posts()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def view_post(self, event):
        """Display a selected post in a new window for viewing/editing with text functionalities."""
        selected_post = self.post_listbox.get(self.post_listbox.curselection())
        
        cursor = self.db.cursor()
        cursor.execute("SELECT user_id, title, content FROM posts WHERE title = %s AND user_id = %s", 
                       (selected_post, self.user_id))
        post = cursor.fetchone()

        post_window = tk.Toplevel(self.root)
        post_window.title("View Post")
        post_window.geometry("600x400")

        tk.Label(post_window, text="Edit Post", font=("Arial", 20)).pack(pady=10)

        tk.Label(post_window, text="Title:").pack()
        title_entry = tk.Entry(post_window)
        title_entry.insert(0, post[1])
        title_entry.pack(pady=5)

        tk.Label(post_window, text="Content:").pack()
        content_text = Text(post_window, height=10, width=50)
        content_text.insert("1.0", post[2])
        content_text.pack(pady=5)

        self.create_menu_bar(post_window, content_text)  # Create menu for text functions

        tk.Button(post_window, text="Update", command=lambda: self.update_post(post[0], title_entry.get(), content_text.get("1.0", tk.END))).pack(side='left', padx=5)
        tk.Button(post_window, text="Delete", command=lambda: self.delete_post(post[0], post_window)).pack(side='left', padx=5)
        tk.Button(post_window, text="Close", command=post_window.destroy).pack(side='right', padx=5)

    def update_post(self, post_id, title, content):
        """Update the selected post in the database."""
        if not title or not content.strip():
            messagebox.showerror("Error", "Title and Content cannot be empty")
            return

        cursor = self.db.cursor()
        try:
            cursor.execute("UPDATE posts SET title = %s, content = %s WHERE user_id = %s", 
                           (title, content.strip(), post_id))
            self.db.commit()
            messagebox.showinfo("Success", "Post updated successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def delete_post(self, post_id, post_window):
        """Delete the selected post from the database."""
        if messagebox.askyesno("Delete Post", "Are you sure you want to delete this post?"):
            cursor = self.db.cursor()
            try:
                cursor.execute("DELETE FROM posts WHERE user_id = %s", (post_id,))
                self.db.commit()
                post_window.destroy()
                self.load_posts()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
    """            
    def logout(self):
        #Log the user out and return to the login page.
        self.user_id = None
        self.login_page()
    """

    def logout(self):
        """Log the user out with confirmation and return to the login page."""
        if messagebox.askokcancel("Logout", "Are you sure you want to logout?"):
            self.user_id = None
            self.login_page()


    def create_menu_bar(self, window, text_widget):
        """Create a non-tearable menu bar with text functionalities for the specific window."""
        menubar = Menu(window)

        # Create 'Text' dropdown menu
        text_menu = Menu(menubar, tearoff=0)
        text_menu.add_command(label="Cut", command=lambda: self.cut_text(text_widget))
        text_menu.add_command(label="Copy", command=lambda: self.copy_text(text_widget))
        text_menu.add_command(label="Paste", command=lambda: self.paste_text(text_widget))
        text_menu.add_separator()
        text_menu.add_command(label="Find", command=lambda: self.find_text(text_widget))
        text_menu.add_command(label="Find and Replace", command=lambda: self.find_and_replace_text(text_widget))

        # Add 'Text' menu to the menubar
        menubar.add_cascade(label="Text", menu=text_menu)

        # Attach the menu to the window
        window.config(menu=menubar)

    def cut_text(self, text_widget):
        """Cut selected text."""
        text_widget.event_generate("<<Cut>>")
    
    def copy_text(self, text_widget):
        """Copy selected text."""
        text_widget.event_generate("<<Copy>>")

    def paste_text(self, text_widget):
        """Paste text from clipboard."""
        text_widget.event_generate("<<Paste>>")
    
    def find_text(self, text_widget):
        """Find text in the content."""
        # Simple find functionality (Can be expanded as per requirement)
        target = tk.simpledialog.askstring("Find", "Enter text to find:")
        content = text_widget.get("1.0", tk.END)
        idx = content.find(target)
        if idx >= 0:
            line_num = content.count("\n", 0, idx) + 1
            char_num = idx - content.rfind("\n", 0, idx)
            text_widget.mark_set("insert", f"{line_num}.{char_num}")
            text_widget.see("insert")
            text_widget.tag_add("highlight", "insert", f"insert + {len(target)}c")
            text_widget.tag_config("highlight", background="yellow")
        else:
            messagebox.showinfo("Not Found", "Text not found")

    def find_and_replace_text(self, text_widget):
        """Find and replace text in the content."""
        find_str = tk.simpledialog.askstring("Find", "Enter text to find:")
        replace_str = tk.simpledialog.askstring("Replace", "Enter replacement text:")
        content = text_widget.get("1.0", tk.END)
        new_content = content.replace(find_str, replace_str)
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", new_content)

def main():
    root = tk.Tk()
    app = BlogApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
