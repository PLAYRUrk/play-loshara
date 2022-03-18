title = "MNEMG by NVcoder, PLAYRU"
release = "v0.666"

import plistlib
import sys
import os
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QFormLayout,
    QFileDialog,
    QPushButton,
    QSlider,
    QCheckBox,
    QMessageBox,
    QSpinBox,
    QFrame,
    QLineEdit,
    QComboBox,
)

sizes = (
    2,
    4,
    8,
    16,
    32,
    64,
    128,
)


sides = (
    "top",
    "bottom",
    "left",
    "right",
    "front",
    "back",
)

colors = (
    "white",
    "orange",
    "magenta",
    "lightBlue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "lightGray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
)

ignore_color = (0, 0, 0)

func_template = "{fname}_panel.setColorRGB({color_xy})"

code_template = """
{fname}_panel = peripheral.wrap("{side}")
{fname}_panel.fill({ignore_color})
function {fname}_on()
    {fname}_panel.fill({ignore_color})
{stuff}
end
function {fname}_off()
    {fname}_panel.fill({ignore_color})
end
"""

def get_code(img:Image, fname:str, side:str):
    img.convert('RGB')

    w, h = img.size

    pixels = []
    for x in range(w):
        for y in range(h):
            pos = (x, y)
            color = img.getpixel(pos)
            if color != ignore_color:
                pixels.append(color + pos)

    funcs = ""
    for color_xy in pixels:
        x = color_xy[3]
        y = color_xy[4]
        if len(color_xy) == 6:
            x = color_xy[4]
            y = color_xy[5]
        funcs += "    " + func_template.format(fname=fname, color_xy=f"{color_xy[0]}, {color_xy[1]}, {color_xy[2]}, {x}, {y}") + "\n"

    return code_template.format(fname=fname, side=side, ignore_color=f"{ignore_color[0]}, {ignore_color[1]}, {ignore_color[2]}", stuff=funcs)

def save_code(path:str, code:str):
    with open(path, "w") as file_save:
        file_save.writelines(code)

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class FileDialog(QFileDialog):
    def __init__(self, title:str, type_name:str ,types:tuple) -> None:
        super().__init__()
        filter = f"{type_name} ({' '.join(['*.' + s for s in types])})"
        self.path = self.getOpenFileName(self, title, "C:/", filter)
    
    def __str__(self) -> str:
        return self.path[0]
    
    def get_tuple(self) -> tuple:
        return self.path

class Info(QMessageBox):
    def __init__(self, title:str, text:str, info:str):
        super().__init__()

        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)

        self.setText(text)
        self.setInformativeText(info)

        self.show()

        self.exec_()

class Error(QMessageBox):
    def __init__(self, title:str, text:str, info:str):
        super().__init__()

        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(title)

        self.setText(text)
        self.setInformativeText(info)

        self.show()

        self.exec_()

i = 0

class ImageModulator():
    def __init__(self) -> None:
        self.image = None
        self.mod_x = 0
        self.mod_y = 0
        self.panel_size = 2
        self.image_size = (0, 0)
        self.compiled_image = None
        self.new_img = None
        self.auto_scale = False

    def validate_image(self, image_path) -> tuple:
        try:
            Image.open(image_path)
            return (True)
        except Exception as e:
            return (False, e)

    def import_image(self, image_path) -> tuple:
        check = self.validate_image(image_path)
        if check:
            self.image = Image.open(image_path)
            return (True)
        else:
            return (False, check[1])

    def update_vars(self, mod_x:int, mod_y:int, panel_size:int, image_size:tuple, auto_scale:bool) -> None:
        self.mod_x = mod_x
        self.mod_y = mod_y
        self.panel_size = panel_size
        self.image_size = image_size
        self.auto_scale = auto_scale
    
    def get_image_info(self) -> tuple:
        if self.image is not None:
            return (True, self.image.size)
        else:
            return (False)
    
    def compile_image(self) -> bool:
        global i
        print("shit" + str(i))
        i += 1
        print(self.image)
        if self.image is not None:
            try:
                print(1)
                new_img_size = (self.panel_size, self.panel_size)
                print(new_img_size)
                print(2)
                self.new_img = Image.new(mode="RGB", size=new_img_size, color=ignore_color)
                print(self.new_img)
                print(3)
                resized_image = self.image.resize(self.image_size)
                print(self.new_img)
                print(4)
                self.new_img.paste(resized_image, (self.mod_x, self.mod_y))
                print(self.new_img)
                print(5)
                if self.auto_scale:
                    self.new_img = self.new_img.resize((200, 200))
                print(self.new_img)
                if type(self.new_img) == Image.Image:
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
        else:
            return False
    
    def get_img(self):
        if self.new_img is not None:
            return self.new_img
        else:
            return False

    def get_pyqt5_img(self, image:Image):
        return QPixmap.fromImage(ImageQt(image))
    
    def get_ready_image(self):
        return self.get_img() if self.get_img() is not None else False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{title} | {release}")

        self.image_modulator = ImageModulator()

        Info("Внимание!", "Прога очень свежая, может вылетать!\nНа визуальные глюки внимание не обращайте...", "")

        self.img_size = None
        self.img_valid = False
        self.auto_scale = False
        self.panel_size = 2
        self.mod_x = 0
        self.mod_y = 0
        self.file = None

        # Левая сторон
        self.img_prew = QGridLayout()
        self.img_prew_label = QLabel("Выберите файл картинки!")
        self.img_prew_label.setMinimumSize(300, 300)
        self.img_prew_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.img_prew.addWidget(self.img_prew_label)

        # Справа сторон
        self.options = QFormLayout()

        self.options_import_img_label = QLabel("*файл не выбран*")
        self.options_import_img_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.options_import_img_button = QPushButton("Выбрать файл")

        self.options_import_img_button.clicked.connect(self.import_img)

        self.options_import_img = QHBoxLayout()
        self.options_import_img.addWidget(self.options_import_img_button)
        self.options_import_img.addWidget(self.options_import_img_label)

        self.options_panel_size_slider = QSlider()
        self.options_panel_size_slider.setOrientation(Qt.Horizontal)
        self.options_panel_size_slider.setTickPosition(1)
        self.options_panel_size_slider.setTickInterval(0)
        self.options_panel_size_slider.setMinimum(0)
        self.options_panel_size_slider.setMaximum(6)
        self.options_panel_size_slider.valueChanged.connect(self.panel_size_changed)

        self.options_panel_size_label = QLabel("2")
        self.options_panel_size_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.options_panel_size = QVBoxLayout()
        self.options_panel_size.addWidget(self.options_panel_size_slider)
        self.options_panel_size.addWidget(self.options_panel_size_label)

        self.options_resize_image_check = QCheckBox("Подогнать размер картинки к размеру\nпанели")
        self.options_resize_image_check.stateChanged.connect(self.auto_size_changed)

        self.options_size_x_spin_box = QSpinBox()
        self.options_size_x_spin_box.setMinimum(1)
        self.options_size_x_spin_box.setMaximum(999)
        self.options_size_x_spin_box.valueChanged.connect(self.auto_size_changed)
        self.options_size_x_label = QLabel("X: ")

        self.options_size_x = QHBoxLayout()
        self.options_size_x.addWidget(self.options_size_x_label)
        self.options_size_x.addWidget(self.options_size_x_spin_box)

        self.options_size_y_spin_box = QSpinBox()
        self.options_size_y_spin_box.setMinimum(1)
        self.options_size_y_spin_box.setMaximum(999)
        self.options_size_y_spin_box.valueChanged.connect(self.auto_size_changed)
        self.options_size_y_label = QLabel("Y: ")

        self.options_size_y = QHBoxLayout()
        self.options_size_y.addWidget(self.options_size_y_label)
        self.options_size_y.addWidget(self.options_size_y_spin_box)

        self.options_size = QVBoxLayout()
        self.options_size.addLayout(self.options_size_x)
        self.options_size.addLayout(self.options_size_y)

        self.options_auto_scale_check = QCheckBox("Авто масштаб")
        self.options_auto_scale_check.stateChanged.connect(self.auto_size_changed)

        self.options_mod_x_spin_box = QSpinBox()
        self.options_mod_x_spin_box.setMinimum(0)
        self.options_mod_x_spin_box.setMaximum(999)
        self.options_mod_x_spin_box.valueChanged.connect(self.auto_size_changed)
        self.options_mod_x_label = QLabel("X: ")

        self.options_mod_x = QHBoxLayout()
        self.options_mod_x.addWidget(self.options_mod_x_label)
        self.options_mod_x.addWidget(self.options_mod_x_spin_box)

        self.options_mod_y_spin_box = QSpinBox()
        self.options_mod_y_spin_box.setMinimum(0)
        self.options_mod_y_spin_box.setMaximum(999)
        self.options_mod_y_spin_box.valueChanged.connect(self.auto_size_changed)
        self.options_mod_y_label = QLabel("Y: ")

        self.options_mod_y = QHBoxLayout()
        self.options_mod_y.addWidget(self.options_mod_y_label)
        self.options_mod_y.addWidget(self.options_mod_y_spin_box)

        self.options_mod = QVBoxLayout()
        self.options_mod.addLayout(self.options_mod_x)
        self.options_mod.addLayout(self.options_mod_y)

        self.options_fname_line_edit = QLineEdit()

        self.options_side_combo = QComboBox()
        self.options_side_combo.addItems(sides)

        self.options_colors_combo = QComboBox()
        self.options_colors_combo.addItems(colors)

        self.options.addRow(self.options_import_img_button, self.options_import_img_label)
        self.options.addRow("Размер панели: ", self.options_panel_size)
        self.options.addRow(self.options_resize_image_check)
        self.options.addRow("Размер картинки: ", self.options_size)
        self.options.addRow("Смещение картинки: ", self.options_mod)
        self.options.addRow(self.options_auto_scale_check)
        self.options.addRow(self.options_auto_scale_check)
        self.options.addRow(QHLine())
        self.options.addRow("Название панели: ", self.options_fname_line_edit)
        self.options.addRow("Side: ", self.options_side_combo)
        self.options.addRow("Color: ", self.options_colors_combo)
        self.options.addRow(QHLine())

        self.options.addRow(QLabel("Файл кода"))
        
        self.options_code_file_label = QLabel("*файл не выбран*")
        self.options_code_file_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.options_code_file_button = QPushButton("Выбрать файл")
        self.options_code_file_button.clicked.connect(self.get_code_file)

        self.options.addRow(self.options_code_file_button, self.options_code_file_label)
        
        self.options_widget = QWidget()
        self.options_widget.setFixedWidth(250)
        self.options_widget.setLayout(self.options)

        self.options.addRow(QHLine())

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setFont(QFont("Arial", 20))
        self.save_btn.clicked.connect(self.save_file)

        self.options.addRow(self.save_btn)

        # Виджэтс
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.img_prew)
        self.layout.addWidget(QVLine())
        self.layout.addWidget(self.options_widget)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def get_code_file(self):
        try:
            file_path = FileDialog("Выберите файл", "Files", ("lua", "txt"))
            self.file = str(file_path)
            self.options_code_file_label.setText(os.path.basename(str(file_path)))
        except:
            Error("Ошибка", "Не удалось выбрать файл!", "")
            return False
        self.update_image()

    def save_file(self):
        fname = self.options_fname_line_edit.text()

        if self.file is None:
            Error("Ошибка", "Выберите файл для сохранения кода!", "")
            return False
        
        if fname == "":
            Error("Ошибка", "Введите название панели!", "")
            return False

        img = self.image_modulator.get_ready_image()

        if img == False:
            Error("Ошибка", "Нет изображения!", "")
            return False
        
        self.update_image()

        side = f"{self.options_side_combo.currentText()}|{self.options_colors_combo.currentText()}"

        code = get_code(img, fname, side)

        path = self.file

        save_code(path, code)

        self.update_image()

        Info("Ура, победа!", "Всё готово\nРадуйся!", "")

    def auto_size_changed(self):
        value = self.options_resize_image_check.isChecked()
        auto_scale = self.options_auto_scale_check.isChecked()
        self.auto_scale = auto_scale

        self.mod_x = self.options_mod_x_spin_box.value()
        self.mod_y = self.options_mod_y_spin_box.value()

        if value:
            img_info = (self.panel_size, self.panel_size)
            self.options_size_x_spin_box.setValue(img_info[0])
            self.options_size_y_spin_box.setValue(img_info[1])
            self.options_size_x_spin_box.setEnabled(False)
            self.options_size_y_spin_box.setEnabled(False)
        else:
            self.options_size_x_spin_box.setEnabled(True)
            self.options_size_y_spin_box.setEnabled(True)

        if value:
            self.img_size = (self.panel_size, self.panel_size)
        else:
            self.img_size = (self.options_size_x_spin_box.value(), self.options_size_y_spin_box.value())
        self.update_image()

    def import_img(self):
        try:
            img_path = FileDialog("Выберите файл картинки", "Images", ("png", "jpg"))
            result = self.image_modulator.import_image(str(img_path))
        except:
            Error("Ошибка", "Не удалось импортировать картинку!", "")
            return False
        if result:
            self.auto_size_changed()
            img_info = self.image_modulator.get_image_info()[1]
            self.options_size_x_spin_box.setValue(img_info[0])
            self.options_size_y_spin_box.setValue(img_info[1])
            self.img_valid = True
            self.options_import_img_label.setText(os.path.basename(str(img_path)))
            self.update_image()
        else:
            self.img_valid = False
            Error("Ошибка", "Не удалось импортировать картинку!")
            return False
        self.update_image()
    
    def panel_size_changed(self):
        self.panel_size = sizes[int(self.options_panel_size_slider.value())]
        self.options_panel_size_label.setText(str(self.panel_size))
        self.auto_size_changed()
        self.update_image()
    
    def is_img_valid(self):
        return self.img_size is not None and self.img_valid

    def update_vars(self):
        self.image_modulator.update_vars(self.mod_x, self.mod_y, self.panel_size, self.img_size, self.auto_scale)

    def update_image(self):
        if self.is_img_valid():
            self.update_vars()
        if self.is_img_valid():
            self.update_vars()
            result = self.image_modulator.compile_image()
            if result:
                try:
                    self.img_prew_label.setPixmap(self.image_modulator.get_pyqt5_img(self.image_modulator.get_img()))
                except Exception as e:
                    Error("Пиздец, размером с Генерала Анала", "Не удалось конвертировать Image в PyQt5 Pixmap", str(e))
            else:
                Error("Пиздец", "Не удалось выполнить compile_image()", "")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

"""
Энкрай пидор
"""