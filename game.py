from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties
from panda3d.core import Vec3

class GameSettings:
    def __init__(self, base):
        self.base = base
        self.fullscreen = False
        self.sensitivity = 10
        self.camera_velocity = 10

    def apply_settings(self):
        props = WindowProperties()
        props.setFullscreen(self.fullscreen)
        props.setTitle("Demo")
        self.base.win.requestProperties(props)
        self.base.disableMouse()
        return self

class GameEnvironment:
    def __init__(self, loader, render):
        self.environment = loader.loadModel("./map/map.obj")
        self.environment.reparentTo(render)
        render.setShaderAuto()
        self.environment.setHpr(0, 0, 0)

class GameControls:
    def __init__(self, base):
        self.base = base
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
        self.base.accept("w", self.update_key_map, ["forward", True])
        self.base.accept("w-up", self.update_key_map, ["forward", False])
        self.base.accept("s", self.update_key_map, ["backward", True])
        self.base.accept("s-up", self.update_key_map, ["backward", False])
        self.base.accept("a", self.update_key_map, ["left", True])
        self.base.accept("a-up", self.update_key_map, ["left", False])
        self.base.accept("d", self.update_key_map, ["right", True])
        self.base.accept("d-up", self.update_key_map, ["right", False])
        self.base.accept("space", self.update_key_map, ["up", True])
        self.base.accept("space-up", self.update_key_map, ["up", False])
        self.base.accept("shift", self.update_key_map, ["down", True])
        self.base.accept("shift-up", self.update_key_map, ["down", False])
        self.base.accept("mouse1", self.update_key_map, ["shoot", True])
        self.base.accept("mouse1-up", self.update_key_map, ["shoot", False])
        self.base.accept("mouse2", self.update_key_map, ["scope", True])
        self.base.accept("mouse2-up", self.update_key_map, ["scope", False])

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.settings = GameSettings(self).apply_settings()
        self.environment = GameEnvironment(self.loader, self.render)
        self.controls = GameControls(self)
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
