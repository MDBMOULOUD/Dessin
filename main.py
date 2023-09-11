from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.uix.colorpicker import ColorPicker
from kivymd.uix.slider import MDSlider  # Import the MDSlider
from kivy.uix.button import Button
from kivy.config import Config

# Set Kivy configuration for automatic orientation handling
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

KV = '''
BoxLayout:
    orientation: 'vertical'

    BoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: 10

        MDIconButton:
            icon: "palette"
            on_release: app.show_color_picker_dialog()

        MDIconButton:
            icon: "eraser-variant"
            on_release: app.toggle_eraser_mode()

        MDIconButton:
            icon: "delete-sweep"
            on_release: app.delete_all_lines()

        MDIconButton:
            icon: "pencil"  # Icon for line width selection button
            on_release: app.show_line_width_dialog()  # Call the show_line_width_dialog() method

        MDIconButton:
            icon: "refresh"
            on_release: app.reset_app()

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: "48dp"

    DrawingArea:
        id: drawing_area
'''


class DrawingArea(Widget):
    lines = []
    current_line = None
    current_color = (0, 0, 0, 1)
    eraser_mode = False
    current_line_width = 2  # Default line width

    def on_touch_down(self, touch):
        if self.eraser_mode:
            self.erase_at_point(touch.x, touch.y)
        else:
            for widget in self.parent.walk(restrict=True):
                if isinstance(widget, MDIconButton) and widget.collide_point(*touch.pos):
                    return

            with self.canvas:
                Color(*self.current_color)
                # Create a Line widget with the selected line width
                self.current_line = Line(points=[touch.x, touch.y], width=self.current_line_width)
                DrawingArea.lines.append(self.current_line)

    def on_touch_move(self, touch):
        if self.eraser_mode:
            self.erase_at_point(touch.x, touch.y)
        elif self.current_line:
            self.current_line.points += [touch.x, touch.y]

    def erase_at_point(self, x, y):
        for line in DrawingArea.lines:
            new_points = []
            points = line.points
            for i in range(0, len(points), 2):
                px, py = points[i], points[i + 1]
                if abs(px - x) > 10 or abs(py - y) > 10:
                    new_points.extend([px, py])
            line.points = new_points


class DrawingApp(MDApp):
    color_picker_dialog = None
    line_width_dialog = None  # Declare line width dialog as a class attribute

    def build(self):
        from kivy.core.window import Window
        Window.orientation = 'auto'
        return Builder.load_string(KV)

    def erase_lines(self):
        drawing_area = self.root.ids.drawing_area
        if drawing_area.eraser_mode:
            drawing_area.eraser_mode = False
        else:
            drawing_area.eraser_mode = True

    def delete_all_lines(self):
        drawing_area = self.root.ids.drawing_area
        for line in DrawingArea.lines:
            drawing_area.canvas.remove(line)
        DrawingArea.lines = []

    def show_color_picker_dialog(self):
        if not self.color_picker_dialog:
            color_picker = ColorPicker(
                color=DrawingArea.current_color,
                size_hint=(None, None),
                size=("300dp", "300dp"),
            )
            color_picker.scale = 5
            self.color_picker_dialog = MDDialog(
                title="Choose Color",
                type="custom",
                content_cls=color_picker,
                buttons=[
                    MDRaisedButton(
                        text="Select",
                        on_release=self.set_color_from_picker,
                    ),
                    MDRaisedButton(
                        text="Cancel",
                        on_release=self.dismiss_color_picker_dialog,
                    ),
                ],
                size_hint=(0.5, None),
                size=("300dp", "300dp"),
            )
        self.color_picker_dialog.open()

    def set_color_from_picker(self, instance):
        drawing_area = self.root.ids.drawing_area
        color_picker = self.color_picker_dialog.content_cls
        selected_color = color_picker.color
        DrawingArea.current_color = selected_color
        self.dismiss_color_picker_dialog()

    def dismiss_color_picker_dialog(self):
        if self.color_picker_dialog:
            self.color_picker_dialog.dismiss()

    def toggle_eraser_mode(self):
        drawing_area = self.root.ids.drawing_area
        if drawing_area.eraser_mode:
            drawing_area.eraser_mode = False
        else:
            drawing_area.eraser_mode = True

    def reset_app(self):
        drawing_area = self.root.ids.drawing_area
        drawing_area.canvas.clear()
        for line in DrawingArea.lines:
            drawing_area.canvas.add(line)  # Re-add the lines
        DrawingArea.current_color = (0, 0, 0, 1)
        drawing_area.eraser_mode = False
        self.dismiss_color_picker_dialog()

    def show_line_width_dialog(self):
        if not self.line_width_dialog:
            line_width_slider = MDSlider(
                min=1,  # Minimum line width
                max=10,  # Maximum line width
                value=DrawingArea.current_line_width,  # Use the current line width as the default value
            )
            line_width_slider.bind(value=self.set_line_width)

            self.line_width_dialog = MDDialog(
                title="Select Line Width",
                type="custom",
                content_cls=line_width_slider,
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=self.dismiss_line_width_dialog,
                    ),
                ],
            )

        self.line_width_dialog.open()

    def set_line_width(self, instance, value):
        DrawingArea.current_line_width = value

    def dismiss_line_width_dialog(self, instance):
        if self.line_width_dialog:
            self.line_width_dialog.dismiss()


if __name__ == '__main__':
    DrawingApp().run()