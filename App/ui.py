import tkinter as tk

CLUTCHES = 6
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CLUTCH_SIZE = int(SCREEN_WIDTH / CLUTCHES)

class Clutch():
  def __init__(self, root, coords: tuple):
    self.clutch_value = 0
    self.clutch_state = False

    self.canvas = tk.Canvas(root, width=CLUTCH_SIZE, height=CLUTCH_SIZE, bg=root["bg"], highlightthickness=0)
    self.canvas.pack()
    self.canvas.place(x=coords[0], y=coords[1])
    self.light = self.canvas.create_oval(int(CLUTCH_SIZE * 0.1), int(CLUTCH_SIZE * 0.1), int(CLUTCH_SIZE * 0.9), int(CLUTCH_SIZE * 0.9), fill="grey", outline="")


  def updateLight(self, clutch_value):
    self.clutch_value = clutch_value
    if self.clutch_value == 0:
      self.canvas.itemconfig(self.light, fill="red")
      self.clutch_state = True
    elif self.clutch_value == 1:
      self.canvas.itemconfig(self.light, fill="green")
      self.clutch_state = False


class Ui():
  def __init__(self):
    self.root = tk.Tk()
    self.root.title("Simple GUI")
    self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    self.root.bind("<Configure>", lambda event: self.resize())

    self.label = tk.Label(self.root, text="Koppeling checker", font=("Helvetica", int(SCREEN_HEIGHT * 0.05)))
    self.label.pack(pady=int(SCREEN_HEIGHT * 0.1))
    self.label.configure(bg="lightblue")

    self.clutches = []
    for i in range(CLUTCHES):
      self.clutches.append(Clutch(self.root, (int(CLUTCH_SIZE * i), int(SCREEN_HEIGHT - CLUTCH_SIZE))))

    self.changeBackground("lightblue")


  def run(self):
    self.root.mainloop()


  def changeBackground(self, color):
    self.root.configure(bg=color)


  def resize(self):
    global SCREEN_WIDTH, SCREEN_HEIGHT, CLUTCH_SIZE
    new_width = self.root.winfo_width()
    new_height = self.root.winfo_height()

    if new_width != SCREEN_WIDTH or new_height != SCREEN_HEIGHT:
      SCREEN_WIDTH = new_width
      SCREEN_HEIGHT = new_height
      CLUTCH_SIZE = int(SCREEN_WIDTH / CLUTCHES)

      for i in range(CLUTCHES):
        clutch = self.clutches[i]
        clutch.canvas.place(x=int(CLUTCH_SIZE * i), y=int(SCREEN_HEIGHT - CLUTCH_SIZE))
        clutch.canvas.configure(width=CLUTCH_SIZE, height=CLUTCH_SIZE)
        # clutch.
      self.label.configure(font=("Helvetica", int(SCREEN_WIDTH * 0.05)))
      self.label.place(x=int((SCREEN_WIDTH - self.label.winfo_width()) / 2), y=int(SCREEN_HEIGHT * 0.1))
