import pyglet
from pyglet.window import key

from GUI.MenuManager import MenuManager
from GUI.menus.MainMenu import MainMenu
from GUI.menus.SessionMenu import SessionMenu
from GUI.menus.ProgramMenu import ProgramMenu
from GUI.menus.StatsMenu import StatsMenu
from GUI.menus.Form import Form
from GUI.Notifications import Notification
from GUI.Distortion import Distortion

window_width, window_height = 800, 480
window = pyglet.window.Window(width=window_width, height=window_height, caption="Gym Diary")

# Create notification and distortion systems
notification = Notification(font_size=24, display_time=2.5)
distortion = Distortion(window_width, window_height, intensity=0.75)

# Create menu manager
manager = MenuManager(notification)

# Instantiate all menus
main_menu = MainMenu(manager)
session_menu = SessionMenu(manager)
program_menu = ProgramMenu(manager)
stats_menu = StatsMenu(manager)
form_menu = Form(manager)

# Register all menus
manager.register_menu("MainMenu", main_menu)
manager.register_menu("SessionMenu", session_menu)
manager.register_menu("ProgramMenu", program_menu)
manager.register_menu("StatsMenu", stats_menu)
manager.register_menu("Form", form_menu)

# Start with main menu
manager.switch_to("MainMenu")

@window.event
def on_draw():
    window.clear()
    batch = pyglet.graphics.Batch() # treat like window/screen
    if manager.current_menu:
        manager.current_menu.render(batch)
    notification.render(batch)
    #distortion.render(batch)
    #print(f"main batch {batch._instance_count}")
    #batch.draw() # draw() gets called in each element
    

@window.event
def on_key_press(symbol, modifiers):
    # Map pyglet keys to your logic
    event = type('Event', (), {})()  # Dummy event object
    event.type = 'KEYDOWN'
    event.symbol = symbol
    event.modifiers = modifiers
    # You may want to map pyglet key symbols to pygame-like keys if your code expects them
    manager.handle_event(event)

@window.event
def on_close():
    pyglet.app.exit()

def update(dt):
    pass
pyglet.clock.schedule_interval(update, 1/12.0)  # 12 FPS

pyglet.app.run()

