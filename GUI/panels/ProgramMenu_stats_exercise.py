from GUI.Table import Table
from GUI.elements.Button import Button
from GUI.elements.ValueDisplay import ValueDisplay
from workout_db.exercises import Exercises
from GUI.style import StyleManager
from workout_db.sessions_db import SessionsDB

class ExerciseStatsPanel(Table):
    def __init__(self, x, y, width, height, queriedExercise, manager):
        self.queriedExercise = queriedExercise
        cols = 2
        rows = 2

        super().__init__(x, y, width, height, manager, rows=rows, cols=cols, padding=10)

        # Create ValueDisplay elements for stats
        # Retrive stats from database
        sessions = SessionsDB()
        lastPerformance = sessions.get_last_performance(self.queriedExercise)
        peakPerformance = sessions.get_peak_performance(self.queriedExercise)
        totalSets = sessions.get_total_sets_performed(self.queriedExercise)
        volumeChange = sessions.get_volume_change_percentage(self.queriedExercise)

        prompt_color =  StyleManager.get_muscle_group_color( Exercises.get_target_muscle(self.queriedExercise) )["bg_color"] 
        self.lastPerformanceDisplay = ValueDisplay(prompt="Last Performance", value=f"date: {lastPerformance["date"]}\nsets: {lastPerformance["sets"]}\nreps: {lastPerformance["reps"]}\nweight: {lastPerformance["weight"]}",width=width//cols,height=height//rows, manager=self.manager, bg_color_prompt=prompt_color)
        self.add_element(self.lastPerformanceDisplay,0,0)
        self.peakPerformanceDisplay = ValueDisplay(prompt="Peak Performance", value=f"date: {peakPerformance["date"]}\nsets: {peakPerformance["sets"]}\nreps: {peakPerformance["reps"]}\nweight: {peakPerformance["weight"]}",width=width//cols,height=height//rows, manager=self.manager, bg_color_prompt=prompt_color)
        self.add_element(self.peakPerformanceDisplay,1,0)
        self.totalSetsDisplay = ValueDisplay(prompt="Total Sets", value=f"{totalSets} sets performed\nin last month",width=width//cols,height=height//rows, manager=self.manager, bg_color_prompt=prompt_color)
        self.add_element(self.totalSetsDisplay,0,1)
        volumeChangeString = ""
        arrowFlag = ""
        if volumeChange < 0:
            volumeChangeString = f"{volumeChange}% decrease\nin last month"
            arrowFlag = "down"
        else:
            volumeChangeString = f"{volumeChange}% increase\nin last month"
            arrowFlag = "up"
        self.volumeChangeDisplay = ValueDisplay(prompt="Volume Change", value=volumeChangeString,width=width//cols,height=height//rows,arrow_indicator=arrowFlag, manager=self.manager, bg_color_prompt=prompt_color)
        self.add_element(self.volumeChangeDisplay,1,1)

        # # Fill the grid with muscle buttons
        # for idx, muscle in enumerate(target_muscles):
        #     row = idx // cols
        #     col = idx % cols
        #     btn = Button(
        #         text=muscle,
        #         x=0, y=0,  # Will be positioned by Table
        #         width=width // cols,
        #         height=height // rows,
        #         manager=manager
        #     )
        #     self.add_element(btn, row, col)
        #     btn.on_press = self.on_button_press

        self.setNeighbors()
        self.enforceElementsSize()

    def update(self):
        sessions = SessionsDB()
        lastPerformance = sessions.get_last_performance(self.queriedExercise)
        peakPerformance = sessions.get_peak_performance(self.queriedExercise)
        totalSets = sessions.get_total_sets_performed(self.queriedExercise)
        volumeChange = sessions.get_volume_change_percentage(self.queriedExercise)

        prompt_color =  StyleManager.get_muscle_group_color( Exercises.get_target_muscle(self.queriedExercise) )["bg_color"]
        for element in self.getElements():
            element.bg_color_prompt = prompt_color
        if lastPerformance is not None:
            self.lastPerformanceDisplay.value=f"date: {lastPerformance["date"]}\nsets: {lastPerformance["sets"]}\nreps: {lastPerformance["reps"]}\nweight: {lastPerformance["weight"]}"
        else:
            self.lastPerformanceDisplay.value="No data available"
        if peakPerformance is not None:
            self.peakPerformanceDisplay.value=f"date: {peakPerformance["date"]}\nsets: {peakPerformance["sets"]}\nreps: {peakPerformance["reps"]}\nweight: {peakPerformance["weight"]}"
        else:
            self.peakPerformanceDisplay.value="No data available"
        if totalSets is not None:
            self.totalSetsDisplay.value=f"{totalSets} sets performed\nin last month"
        else:
            self.totalSetsDisplay.value="No data available"
        volumeChangeString = ""
        arrowFlag = ""
        if volumeChange is not None:
            if volumeChange < 0:
                volumeChangeString = f"{volumeChange}% decrease\nin last month"
                arrowFlag = "down"
            else:
                volumeChangeString = f"{volumeChange}% increase\nin last month"
                arrowFlag = "up"
            self.volumeChangeDisplay.value=volumeChangeString 
            self.volumeChangeDisplay.arrow_indicator=arrowFlag
        else:
            self.volumeChangeDisplay.value="No data available"
        
