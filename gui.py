from direct.gui.DirectGui import *
from panda3d.core import *
from direct.task.TaskManagerGlobal import taskMgr
from direct.showbase.ShowBaseGlobal import globalClock

class GUI:
    def __init__(self):

        # Основные элементы GUI
        self.setup_crosshair()
        self.setup_minimap()
        self.setup_tank_info()
        self.setup_reload_indicator()
        self.setup_aim_crosshair()

        taskMgr.add(self.update_reload_indicator, "update_reload_indicator")
        taskMgr.add(self.update_aim_crosshair, "update_aim_crosshair")

    def setup_crosshair(self):
        # Прицел
        self.crosshair = OnscreenImage(
            image='textures/crosshair_main.png',
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
            pos=(-1.35, 0, -0.8),
            frameColor=(0, 0, 0, 0.5)
        )
        
        self.tank_name_label = DirectLabel(
            parent=self.tank_info_frame,
            text=f"Tank {base.localPlayer.name}",
            pos=(-0.1, 0, 0.1),
            scale=0.07,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0)
        )
        
        self.health_label = DirectLabel(
            parent=self.tank_info_frame,
            text=f"Protect: {(base.localPlayer.hp / base.localPlayer.max_hp * 100):.2f}%",
            pos=(-0.1, 0, 0),
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

    def setup_reload_indicator(self):
        # индикатор перезарядки вонючий
        self.reload_bar_frame = DirectFrame(
            frameSize=(-0.2, 0.2, -0.03, 0.03),
            pos=(0, 0, -0.9),
            frameColor=(0.1, 0.1, 0.1, 0.8)
        )
        
        self.reload_bar = DirectWaitBar(
            parent=self.reload_bar_frame,
            range=100,
            value=100,
            barColor=(0.2, 0.7, 0.2, 0.8),
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-0.19, 0.19, -0.02, 0.02),
            pos=(0, 0, 0)
        )
        
        self.reload_label = DirectLabel(
            parent=self.reload_bar_frame,
            text="Rеady",
            scale=0.04,
            pos=(0, 0, 0.04),
            text_fg=(0.2, 1, 0.2, 1),
            frameColor=(0, 0, 0, 0)
        )

    def setup_aim_crosshair(self):

        self.aim_crosshair = OnscreenImage(
            image='textures/crosshair.png',
            pos=(0, 0, 0),
            scale=0.05
        )
        self.aim_crosshair.setTransparency(TransparencyAttrib.MAlpha)

    def world_to_screen_coords(self, pos_3d):
        point3 = base.cam.getRelativePoint(render, pos_3d)
        point2 = Point2()

        if not base.camLens.project(point3, point2):
            return None

        return point2
        
    def update_aim_crosshair(self, task):
        if not base.localPlayer.has_camera:
            self.aim_crosshair.hide()
            return task.cont

        gun_pos = base.localPlayer.get_gun_position_for_shot()
        gun_dir = base.localPlayer.get_gun_direction()

        result = base.camera_controls.check_collision2(Vec3(gun_pos), Vec3(gun_pos + gun_dir * 1000))

        screen_pos = self.world_to_screen_coords(result)
        
        if screen_pos:
            self.aim_crosshair.show()
            self.aim_crosshair.setPos(screen_pos.x, 0, screen_pos.y)

        else:
            self.aim_crosshair.hide()

        return task.cont
        

    def update_reload_indicator(self, task):

        if base.localPlayer.is_reloading:
            current_time = globalClock.getFrameTime()
            time_since_shot = current_time - base.localPlayer.last_shot_time
            reload_progress = (time_since_shot / base.localPlayer.reload_time) * 100
            
            self.reload_bar['value'] = reload_progress
            self.reload_bar['barColor'] = (1, 0.5, 0, 0.8)
            self.reload_label['text'] = f"Reloading: {reload_progress:.0f}%"
            self.reload_label['text_fg'] = (1, 0.5, 0, 1)
        else:
            self.reload_bar['value'] = 100
            self.reload_bar['barColor'] = (0.2, 0.7, 0.2, 0.8)
            self.reload_label['text'] = "Ready"
            self.reload_label['text_fg'] = (0.2, 1, 0.2, 1)
                
        return task.cont
    


