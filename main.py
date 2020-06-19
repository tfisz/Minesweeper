from minesweeper import *

global root
# create Tk widget
root = Tk()
# set program title
root.title("Minesweeper")
# create game instance
minesweeper = Minesweeper(root)

# run event loop
root.mainloop()