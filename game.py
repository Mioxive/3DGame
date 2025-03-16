from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties, Vec3, load_prc_file, ConfigVariableManager


# base - встроенный указатель Panda3D на класс игры (у нас Game) (__builtins__.base)
# print(base) - <Game object at 0x00000000>

# Some key variables used in all Panda3D scripts are actually attributes of the ShowBase instance.
# When creating an instance of this class, it will write many of these variables to the built-in scope of the Python interpreter,
# so that they are accessible to any Python module, without the need for extra imports.
# For example, the ShowBase instance itself is accessible anywhere through the base variable.
# Все встроенные указатели: https://docs.panda3d.org/1.10/python/reference/builtins#module-builtins


class GameSettings:
    def __init__(self):
        self.fullscreen = False
        self.sensitivity = 10
        self.camera_velocity = 10

    def apply_settings(self):
        load_prc_file("cfg.prc")
        ConfigVariableManager.getGlobalPtr().listVariables()
        props = WindowProperties()
        props.setFullscreen(self.fullscreen)
        props.setTitle("Demo")
        base.win.requestProperties(props)
        base.disableMouse()
        return self

class GameEnvironment:
    def __init__(self):
        self.environment = base.loader.loadModel("./map/map.obj")
        self.environment.reparentTo(base.render)
        base.render.setShaderAuto()
        self.environment.setHpr(0, 0, 0)

class GameControls:
    def __init__(self):
        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "shoot": False,
            "scope": False
        }

    def update_key_map(self, controlName, controlState):
        self.key_map[controlName] = controlState

    def setup_controls(self):
        base.accept("w", self.update_key_map, ["forward", True])
        base.accept("w-up", self.update_key_map, ["forward", False])
        base.accept("s", self.update_key_map, ["backward", True])
        base.accept("s-up", self.update_key_map, ["backward", False])
        base.accept("a", self.update_key_map, ["left", True])
        base.accept("a-up", self.update_key_map, ["left", False])
        base.accept("d", self.update_key_map, ["right", True])
        base.accept("d-up", self.update_key_map, ["right", False])
        base.accept("space", self.update_key_map, ["up", True])
        base.accept("space-up", self.update_key_map, ["up", False])
        base.accept("shift", self.update_key_map, ["down", True])
        base.accept("shift-up", self.update_key_map, ["down", False])
        base.accept("mouse1", self.update_key_map, ["shoot", True])
        base.accept("mouse1-up", self.update_key_map, ["shoot", False])
        base.accept("mouse2", self.update_key_map, ["scope", True])
        base.accept("mouse2-up", self.update_key_map, ["scope", False])

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.settings = GameSettings().apply_settings()
        self.environment = GameEnvironment()
        self.controls = GameControls()
        self.controls.setup_controls()
        self.updateTask = self.taskMgr.add(self.update, "update")

    def update(self, task):
        dt = globalClock.getDt()
        self.update_camera_position(dt)
        return task.cont

    def update_camera_position(self, dt):
        if self.controls.key_map["forward"]:
            self.camera.setPos(self.camera.getPos() + Vec3(0, self.settings.camera_velocity * dt, 0))
        if self.controls.key_map["backward"]:
            self.camera.setPos(self.camera.getPos() + Vec3(0, -self.settings.camera_velocity * dt, 0))
        if self.controls.key_map["left"]:
            self.camera.setPos(self.camera.getPos() + Vec3(-self.settings.camera_velocity * dt, 0, 0))
        if self.controls.key_map["right"]:
            self.camera.setPos(self.camera.getPos() + Vec3(self.settings.camera_velocity * dt, 0, 0))
        if self.controls.key_map["up"]:
            self.camera.setPos(self.camera.getPos() + Vec3(0, 0, self.settings.camera_velocity * dt))
        if self.controls.key_map["down"]:
            self.camera.setPos(self.camera.getPos() + Vec3(0, 0, -self.settings.camera_velocity * dt))
