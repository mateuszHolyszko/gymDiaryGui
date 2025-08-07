import pyglet
from GUI.elements.Element import Element
from GUI.style import StyleManager

class Image2D_Graph(Element):
    def __init__(
        self,
        image_path: str = None,
        x: int = 0,
        y: int = 0,
        width: int = 100,
        height: int = 40,
        manager=None,
        parent_panel=None,
        layer: int = 0,
        specificMuscleGroup=None
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            manager=manager,
            parent_panel=parent_panel,
            selectable=False,
            neighbors=None,
            layer=layer
        )
        self.muscleGroups = []
        self.specificMuscleGroup = specificMuscleGroup
        self.style = StyleManager.current_style

        self.original_image = pyglet.image.load(image_path)
        self.processed_image = self._process_image(self.original_image)
        self.sprite = pyglet.sprite.Sprite(self.processed_image, x=self.x, y=self.y)
        self.sprite.update(scale_x=self.width/self.processed_image.width, scale_y=self.height/self.processed_image.height)

    def _get_mapped_color(self, r, g, b, a):
        color_mapping = {
            (255, 0, 0): "Chest",
            (255, 52, 0): "Back",
            (0, 0, 255): "Quads",
            (52, 52, 255): "Hamstrings",
            (0, 255, 0): "Biceps",
            (52, 255, 52): "Triceps",
            (125, 255, 125): "Shoulders",
            (255, 255, 155): "Forearms",
            (255, 125, 55): "Calves",
            (125, 52, 255): "Glutes",
            (255, 255, 125): "Abs",
        }
        rgb = (r, g, b)
        if rgb in color_mapping:
            if self.specificMuscleGroup is not None:
                if color_mapping[rgb] != self.specificMuscleGroup:
                    muscle_color = StyleManager.gray_out_color(StyleManager.get_muscle_group_color(color_mapping[rgb])["bg_color"], 0.8)
                    return (*muscle_color[:3], a)
            muscle_color = StyleManager.get_muscle_group_color(color_mapping[rgb])["bg_color"]
            return (*muscle_color[:3], a)
        if rgb == (0, 0, 0):
            return (200, 200, 200, a)
        if rgb == (160, 160, 160):
            return (160, 160, 160, a)
        return (0, 0, 0, 0)

    def _process_image(self, image):
        # Get raw RGBA data
        img_data = image.get_image_data()
        raw_data = img_data.get_data('RGBA', img_data.width * 4)
        pixels = bytearray(raw_data)
        for y in range(img_data.height):
            for x in range(img_data.width):
                idx = (y * img_data.width + x) * 4
                r, g, b, a = pixels[idx], pixels[idx+1], pixels[idx+2], pixels[idx+3]
                nr, ng, nb, na = self._get_mapped_color(r, g, b, a)
                pixels[idx] = nr
                pixels[idx+1] = ng
                pixels[idx+2] = nb
                pixels[idx+3] = na
        # Create new ImageData
        new_img = pyglet.image.ImageData(img_data.width, img_data.height, 'RGBA', bytes(pixels))
        return new_img

    def render(self, batch):
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.draw()

    def on_press(self):
        pass

    def set_position(self, x: int, y: int):
        self._explicit_x = x
        self._explicit_y = y
        if self.parent_panel:
            self.x = self.parent_panel.x + x
            self.y = self.parent_panel.y + y
        else:
            self.x = x
            self.y = y

    def update_panel_position(self):
        if self.parent_panel:
            self.x = self.parent_panel.x + self._explicit_x
            self.y = self.parent_panel.y + self._explicit_y

    def updateSpecyficMuscleGroup(self, specificMuscleGroup):
        self.specificMuscleGroup = specificMuscleGroup
        self.processed_image = self._process_image(self.original_image)
        self.sprite = pyglet.sprite.Sprite(self.processed_image, x=self.x, y=self.y)
        self.sprite.update(scale_x=self.width/self.processed_image.width, scale_y=self.height/self.processed_image.height)