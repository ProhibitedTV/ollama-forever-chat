import tkinter as tk
from tkinter import scrolledtext, ttk
from PIL import Image, ImageTk
import threading
import pyttsx3
import ollama_api
from queue import Queue

class ChatApp:
    """
    A class to represent an AI chat application.

    Attributes
    ----------
    root : tk.Tk
        The root window of the application.
    available_models : list
        A list of available AI models.
    model_a_var : tk.StringVar
        A StringVar to store the selected model for AI model A.
    model_b_var : tk.StringVar
        A StringVar to store the selected model for AI model B.
    engine : pyttsx3.Engine
        The text-to-speech engine.
    tts_thread : threading.Thread
        The thread for text-to-speech processing.
    tts_stop : threading.Event
        An event to signal stopping of the TTS process.
    tts_queue : queue.Queue
        A queue to manage TTS messages.
    conversation_history : list
        A list to store the history of the conversation.
    lock : threading.Lock
        A lock to manage concurrent access to shared resources.
    """

    def __init__(self, root):
        """
        Constructs all the necessary attributes for the ChatApp object.

        Parameters
        ----------
        root : tk.Tk
            The root window of the application.
        """
        self.root = root
        self.root.title("AI Chat Application")
        self.root.configure(bg='black')
        self.root.withdraw()  # Hide the main window initially

        self.available_models = self.get_available_models()

        self.model_a_var = tk.StringVar()
        self.model_b_var = tk.StringVar()

        self.model_a_var.set(self.available_models[0])
        self.model_b_var.set(self.available_models[0])

        self.create_main_ui()

        self.engine = pyttsx3.init()
        self.tts_thread = None
        self.tts_stop = threading.Event()
        self.tts_queue = Queue()

        self.conversation_history = []  # Initialize conversation history
        self.process_tts_queue()
        self.lock = threading.Lock()

        # Configure voices for the models
        voices = self.engine.getProperty('voices')
        self.model_a_voice = voices[0].id  # Use the first available voice for model A
        self.model_b_voice = voices[1].id  # Use the second available voice for model B

    def create_main_ui(self):
        """Creates the main user interface components."""
        self.avatar_frame = tk.Frame(self.root, bg='black')
        self.avatar_frame.pack(padx=10, pady=10, fill=tk.X, expand=False)

        self.avatar_label = tk.Label(self.avatar_frame, bg='black')
        self.avatar_label.pack(side=tk.TOP, pady=5)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg='black', fg='lime', font=('Courier', 12))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self.root, bg='black', fg='lime', font=('Courier', 12))
        self.entry.pack(padx=10, pady=10, fill=tk.X, expand=False)
        self.entry.bind("<Return>", self.on_enter)

        self.button_frame = tk.Frame(self.root, bg='black')
        self.button_frame.pack(padx=10, pady=10, fill=tk.X, expand=False)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_chat, bg='green', fg='white')
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_tts, bg='red', fg='white')
        self.stop_button.pack(side=tk.RIGHT, padx=5)

        self.loading_label = tk.Label(self.button_frame, text="Loading...", fg='lime', bg='black', font=('Courier', 12))
        self.loading_label.pack(side=tk.LEFT, padx=5)
        self.loading_label.pack_forget()

        self.model_selection_frame = tk.Frame(self.root, bg='black')
        self.model_selection_frame.pack(padx=10, pady=10, fill=tk.X, expand=False)

        tk.Label(self.model_selection_frame, text="Model A:", bg='black', fg='white').pack(side=tk.LEFT, padx=5)
        self.model_a_dropdown = ttk.Combobox(self.model_selection_frame, textvariable=self.model_a_var, values=self.available_models, state="readonly")
        self.model_a_dropdown.pack(side=tk.LEFT, padx=5)

        tk.Label(self.model_selection_frame, text="Model B:", bg='black', fg='white').pack(side=tk.LEFT, padx=5)
        self.model_b_dropdown = ttk.Combobox(self.model_selection_frame, textvariable=self.model_b_var, values=self.available_models, state="readonly")
        self.model_b_dropdown.pack(side=tk.LEFT, padx=5)

        self.model_a_img = self.load_image("images/model_a.png")
        self.model_b_img = self.load_image("images/model_b.png")

    def load_image(self, path, size=(50, 50)):
        """
        Loads and resizes an image from the specified path.

        Parameters
        ----------
        path : str
            The file path to the image.
        size : tuple
            The desired size of the image.

        Returns
        -------
        ImageTk.PhotoImage
            The resized image.
        """
        try:
            image = Image.open(path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def show_splash_screen(self):
        """Displays the splash screen."""
        splash = tk.Toplevel()
        splash.overrideredirect(True)
        splash.geometry("800x450")  # Adjust the size as needed

        # Center the splash screen on the screen
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        x = int((screen_width / 2) - (800 / 2))
        y = int((screen_height / 2) - (450 / 2))
        splash.geometry(f"+{x}+{y}")

        splash.configure(bg='black')

        # Load and display the splash image, or a fallback text if the image is not found
        splash_img = self.load_image("images/splash.png", size=(800, 450))
        if splash_img:
            splash_label = tk.Label(splash, image=splash_img, bg='black')
            splash_label.image = splash_img  # Keep a reference to the image to prevent garbage collection
            splash_label.pack()
        else:
            splash_label = tk.Label(splash, text="AI Chat", bg='black', fg='lime', font=('Courier', 24))
            splash_label.pack(expand=True)

        # Close the splash screen after 3 seconds and show the main window
        self.root.after(3000, lambda: self.close_splash_screen(splash))

    def close_splash_screen(self, splash):
        """
        Closes the splash screen and shows the main window.

        Parameters
        ----------
        splash : tk.Toplevel
            The splash screen window.
        """
        splash.destroy()
        self.root.deiconify()

    def get_available_models(self):
        """
        Gets the list of available models from the API.

        Returns
        -------
        list
            A list of available models.
        """
        return ollama_api.list_models()

    def display_message(self, sender, message, image=None):
        """
        Displays a message in the text area, optionally with an image.

        Parameters
        ----------
        sender : str
            The sender of the message.
        message : str
            The message content.
        image : ImageTk.PhotoImage, optional
            An optional image to display with the message.
        """
        if image:
            self.text_area.image_create(tk.END, image=image)
        self.text_area.insert(tk.END, f" {sender}: {message}\n", 'message')
        self.text_area.see(tk.END)

    def update_avatar(self, image):
        """
        Updates the avatar at the top of the UI.

        Parameters
        ----------
        image : ImageTk.PhotoImage
            The image to display as the avatar.
        """
        self.avatar_label.config(image=image)
        self.avatar_label.image = image

    def on_enter(self, event):
        """
        Handles the event when the user presses the Enter key.

        Parameters
        ----------
        event : tk.Event
            The event object.
        """
        user_input = self.entry.get()
        self.entry.delete(0, tk.END)
        self.display_message("User", user_input, image=None)
        self.conversation_history.append(f"User: {user_input}")  # Add user input to conversation history
        threading.Thread(target=self.handle_interaction, args=(user_input,)).start()

    def start_chat(self):
        """Starts the chat interaction."""
        user_input = self.entry.get()
        self.entry.delete(0, tk.END)
        self.display_message("User", user_input, image=None)
        self.conversation_history.append(f"User: {user_input}")  # Add user input to conversation history
        threading.Thread(target=self.handle_interaction, args=(user_input,)).start()

    def handle_interaction(self, user_input, from_model="User"):
        """
        Handles the interaction between the user and the models.

        Parameters
        ----------
        user_input : str
            The user's input message.
        from_model : str, optional
            The model from which the interaction is being handled (default is "User").
        """
        print(f"Handling interaction: user_input={user_input}, from_model={from_model}")
        self.tts_stop.clear()
        self.loading_label.pack(side=tk.LEFT, padx=5)
        with self.lock:
            if from_model == "User":
                model_a_response = self.generate_response_with_context(self.model_a_var.get(), user_input)
                self.loading_label.pack_forget()
                if model_a_response and not self.tts_stop.is_set():
                    print(f"Model A response: {model_a_response}")
                    self.update_avatar(self.model_a_img)  # Update avatar to Model A's image
                    self.display_message(self.model_a_var.get(), model_a_response, self.model_a_img)
                    self.conversation_history.append(f"{self.model_a_var.get()}: {model_a_response}")  # Add model A response to conversation history
                    self.tts_queue.put((model_a_response, self.model_a_voice))  # Add response and voice to TTS queue
                    self.wait_for_tts()
                    if not self.tts_stop.is_set():
                        threading.Thread(target=self.handle_interaction, args=(model_a_response, "Model A")).start()
            elif from_model == "Model A":
                model_b_response = self.generate_response_with_context(self.model_b_var.get(), user_input)
                self.loading_label.pack_forget()
                if model_b_response and not self.tts_stop.is_set():
                    print(f"Model B response: {model_b_response}")
                    self.update_avatar(self.model_b_img)  # Update avatar to Model B's image
                    self.display_message(self.model_b_var.get(), model_b_response, self.model_b_img)
                    self.conversation_history.append(f"{self.model_b_var.get()}: {model_b_response}")  # Add model B response to conversation history
                    self.tts_queue.put((model_b_response, self.model_b_voice))  # Add response and voice to TTS queue
                    self.wait_for_tts()
                    if not self.tts_stop.is_set():
                        threading.Thread(target=self.handle_interaction, args=(model_b_response, "Model B")).start()
            elif from_model == "Model B":
                model_a_response = self.generate_response_with_context(self.model_a_var.get(), user_input)
                self.loading_label.pack_forget()
                if model_a_response and not self.tts_stop.is_set():
                    print(f"Model A response: {model_a_response}")
                    self.update_avatar(self.model_a_img)  # Update avatar to Model A's image
                    self.display_message(self.model_a_var.get(), model_a_response, self.model_a_img)
                    self.conversation_history.append(f"{self.model_a_var.get()}: {model_a_response}")  # Add model A response to conversation history
                    self.tts_queue.put((model_a_response, self.model_a_voice))  # Add response and voice to TTS queue
                    self.wait_for_tts()
                    if not self.tts_stop.is_set():
                        threading.Thread(target=self.handle_interaction, args=(model_a_response, "Model A")).start()

    def generate_response_with_context(self, model, user_input):
        """
        Generates a response from the model using the context of the conversation history.

        Parameters
        ----------
        model : str
            The model to use for generating the response.
        user_input : str
            The user's input message.

        Returns
        -------
        str
            The generated response from the model.
        """
        context = "\n".join(self.conversation_history[-10:])  # Use the last 10 exchanges as context
        print(f"Generating response with context: {context}")
        return ollama_api.generate_response(model, f"{context}\n{user_input}")

    def wait_for_tts(self):
        """Waits for the text-to-speech queue to process messages."""
        while not self.tts_queue.empty():
            message, voice = self.tts_queue.get()
            self.speak_message(message, voice)
            self.tts_queue.task_done()

    def process_tts_queue(self):
        """Processes the text-to-speech queue."""
        if not self.tts_queue.empty() and not self.tts_stop.is_set():
            message, voice = self.tts_queue.get()
            self.speak_message(message, voice)
        self.root.after(1000, self.process_tts_queue)

    def speak_message(self, message, voice):
        """
        Speaks a message using the text-to-speech engine.

        Parameters
        ----------
        message : str
            The message to speak.
        voice : str
            The voice to use for speaking the message.
        """
        print(f"Speaking message: {message} with voice {voice}")
        if self.tts_thread and self.tts_thread.is_alive():
            self.tts_stop.set()
            self.tts_thread.join()

        self.tts_thread = threading.Thread(target=self._speak, args=(message, voice))
        self.tts_thread.start()
        self.tts_thread.join()  # Wait for the TTS thread to finish before proceeding

    def _speak(self, message, voice):
        """
        The internal method to speak a message using the text-to-speech engine.

        Parameters
        ----------
        message : str
            The message to speak.
        voice : str
            The voice to use for speaking the message.
        """
        self.engine.setProperty('voice', voice)
        self.engine.say(message)
        self.engine.runAndWait()
        if self.tts_stop.is_set():
            self.engine.stop()

    def stop_tts(self):
        """Stops the text-to-speech processing."""
        print("Stopping TTS")
        self.tts_stop.set()
        if self.tts_thread and self.tts_thread.is_alive():
            self.tts_thread.join()
        self.engine.stop()
        self.tts_queue.queue.clear()  # Clear the TTS queue to stop the conversation
        self.root.after(100, self.reset_stop_button)

    def reset_stop_button(self):
        """Resets the stop button to the raised state."""
        self.stop_button.config(relief=tk.RAISED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    app.show_splash_screen()
    root.mainloop()
