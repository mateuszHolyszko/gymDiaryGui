import dearpygui.dearpygui as dpg
from EditApp.exercises_tab import build_exercises_tab
from EditApp.programs_tab import build_programs_tab

dpg.create_context()

with dpg.window(label="Workout Tracker", width=800, height=600):
    with dpg.tab_bar():
        build_exercises_tab()
        build_programs_tab()

dpg.create_viewport(title="Workout Tracker", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
