# Import necessary modules from tkinter and chat.py
from tkinter import Tk
from chat import ChatApp

# Initialize the main Tkinter window
root = Tk()
root.withdraw()  # Hide the main window initially to show the splash screen first

# Create an instance of the ChatApp class, passing the main window (root) as an argument
app = ChatApp(root)

# Show the splash screen
app.show_splash_screen()

# Start the Tkinter main event loop
root.mainloop()
