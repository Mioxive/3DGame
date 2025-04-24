from direct.gui.DirectGui import *
from panda3d.core import *

class MainMenu:
    def __init__(self):
        self.frame = DirectFrame(
            frameSize=(-2, 2, -2, 1),
            frameColor=(0.1, 0.1, 0.1, 0.8)
        )

        # Заголовок игры
        self.title = OnscreenText(
            text="Tanks",
            pos=(0, 0.7),
            scale=0.45,
            fg=(1, 0.5, 0, 1)  # Оранжевый цвет
        )

        # Кнопки
        self.btn_play = DirectButton(
            text="Play",
            pos=(0, 0, 0.2),
            scale=0.4,
            command=self.start_game,
            frameColor=(0.3, 0.3, 0.3, 1),
            text_fg=(1, 1, 1, 1)
        )

        self.btn_exit = DirectButton(
            text="Quit",
            pos=(0, 0, -0.4),
            scale=0.4,
            command=self.exit_game,
            frameColor=(0.7, 0.1, 0.1, 1)
        )

    def start_game(self):
        self.frame.hide()
        self.title.hide()
        self.btn_play.hide()
        self.btn_exit.hide()

    def open_settings(self):
        print("Открыть настройки")
        # Можно создать отдельный класс SettingsMenu

    def exit_game(self):
        base.userExit()  # Закрыть приложение
