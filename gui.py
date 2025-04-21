from direct.gui.DirectGui import *
from panda3d.core import *

class GUI:
    def __init__(self):

        # Основные элементы GUI
        self.setup_crosshair()
        self.setup_minimap()
        self.setup_tank_info()

    def setup_crosshair(self):
        #Прицел
        self.crosshair = OnscreenImage(
            image='textures/crosshair.png',
            pos=(0, 0, 0),
            scale=0.05
        )
        self.crosshair.setTransparency(TransparencyAttrib.MAlpha) # type: ignore
    
    def setup_minimap(self):
        # Миникарта
        self.minimap_frame = DirectFrame(
            frameSize=(-0.2, 0.2, -0.2, 0.2),
            pos=(-1.42, 0, 0.7),
            frameColor=(0, 0, 0, 0.5)
        )
        
        self.minimap = OnscreenImage(
            parent=self.minimap_frame,
            image='textures/minimap.png',
            pos=(0, 0, 0),
            scale=0.3
        )
        
        # Иконка игрока на миникарте
        #self.player_minimap_icon = OnscreenImage(
        #    parent=self.minimap_frame,
        #    image='textures/player_icon.png',
        #    pos=(0, 0, 0),
        #    scale=0.03
        #)
    
    def setup_tank_info(self):
        # Информация о танке
        self.tank_info_frame = DirectFrame(
            frameSize=(-0.4, 0.3, -0.2, 0.2),
            pos=(-1.355, 0, -0.8),
            frameColor=(0, 0, 0, 0.5)
        )
        
        self.tank_name_label = DirectLabel(
            parent=self.tank_info_frame,
            text="Tank",
            pos=(-0.1, 0, 0.1),
            scale=0.07,
            text_fg=(1, 1, 0, 1),
            frameColor=(0, 0, 0, 0)
        )
        
        self.health_label = DirectLabel(
            parent=self.tank_info_frame,
            text="Protect: 100%",
            pos=(-0.1, 0, 0),
            scale=0.05,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0)
        )
        
        self.ammo_label = DirectLabel(
            parent=self.tank_info_frame,
            text="Ammunition: 30/40",
            pos=(-0.1, 0, -0.1),
            scale=0.05,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0)
        )
    
#    def setup_bottom_panel(self):
#        # Панель внизу экрана
#        self.bottom_panel = DirectFrame(
#            frameSize=(-1, 1, -0.1, 0.1),
#            pos=(0, 0, -0.9),
#            frameColor=(0, 0, 0, 0.7)
#        )
    def setup_health_bar(self):
        #Полоса здоровья
        self.health_bar = DirectWaitBar(
            value=100,
            range=100,
            pos=(0, 0, -0.85),
            barColor=(0.8, 0.2, 0.2, 0.8),
            frameColor=(0.1, 0.1, 0.1, 0.8),
            scale=0.3
        )

    def move_tank(self, direction):
        if hasattr(self, 'tank'):
            speed = direction * 10
            self.tank.setY(self.tank, speed * globalClock.getDt())
            self.speed_label["text"] = f"Speed: {abs(speed)*3} км/ч"
    
    def rotate_tank(self, direction):
        if hasattr(self, 'tank'):
            self.tank.setH(self.tank, direction * 60 * globalClock.getDt())
    
    def fire(self):
        print("Бах!")
        # Выстрел
    
    def do_repair(self):
        self.health_bar["value"] = 100
        self.health_label["text"] = "Endurance: 100%"
        print("Танк отремонтирован")
    
    def reload_ammo(self):
        self.ammo_label["text"] = "Ammunition: 40/40"
        print("Боезапас пополнен")