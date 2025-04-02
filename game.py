import random

from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties, Vec3, loadPrcFile, AmbientLight, NodePath, AntialiasAttrib
from panda3d.bullet import BulletWorld, BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode, \
    BulletDebugNode
from Viewing import CameraControl, MouseControl
from Tank import Tank

loadPrcFile("cfg.prc")
# base - встроенный указатель Panda3D на класс игры (у нас Game) (__builtins__.base)


class GameSettings:
    def __init__(self):
        self.fullscreen = False
        self.sensitivity = 5
        self.fov = 80
        self.winproperties = WindowProperties()
        self.winproperties.setFullscreen(self.fullscreen)
        self.winproperties.setTitle("Demo")
        base.disableMouse()

    def apply_settings(self):
        base.win.requestProperties(self.winproperties)

class GameWorld:
    def __init__(self):
        self.main_world_node = NodePath("world node")
        self.main_world_node.reparentTo(render)
        self.world = loader.loadModel("./map/map.bam")
        self.world.reparentTo(self.main_world_node)
        render.setShaderAuto()
        self.alight = AmbientLight("alight")
        self.alight.setColor((1.8, 1.8, 1.8, 1))
        self.alight_node = self.main_world_node.attachNewNode(self.alight)
        self.world.setLight(self.alight_node)


        self.world.flattenStrong()
        self.bullet_world = BulletWorld()
        self.bullet_world.setGravity(Vec3(0, 0, -9.81))

        mesh = BulletTriangleMesh()
        for geom_node in self.world.findAllMatches("**/+GeomNode"):
            for i in range(geom_node.node().getNumGeoms()):
                mesh.addGeom(geom_node.node().getGeom(i))

        shape = BulletTriangleMeshShape(mesh, dynamic=False) # собираем коллизию из геометрии

        self.world_body = BulletRigidBodyNode("world")
        self.world_body.setMass(0)
        self.world_body.setStatic(True) # статичный объект
        self.world_body.addShape(shape)
        self.world_body.setFriction(0.5) # трение

        self.main_world_node.attachNewNode(self.world_body)
        self.bullet_world.attachRigidBody(self.world_body)

class GameControls(DirectObject):
    def __init__(self):
        super().__init__()
        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "shoot": False,
        }

    def update_key_map(self, controlName, controlState):
        self.key_map[controlName] = controlState

    def setup_controls(self):
        self.accept("w", self.update_key_map, ["forward", True])
        self.accept("w-up", self.update_key_map, ["forward", False])
        self.accept("s", self.update_key_map, ["backward", True])
        self.accept("s-up", self.update_key_map, ["backward", False])
        self.accept("a", self.update_key_map, ["left", True])
        self.accept("a-up", self.update_key_map, ["left", False])
        self.accept("d", self.update_key_map, ["right", True])
        self.accept("d-up", self.update_key_map, ["right", False])
        self.accept("space", self.update_key_map, ["up", True])
        self.accept("space-up", self.update_key_map, ["up", False])
        self.accept("shift", self.update_key_map, ["down", True])
        self.accept("shift-up", self.update_key_map, ["down", False])
        self.accept("mouse1", self.update_key_map, ["shoot", True])
        self.accept("mouse1-up", self.update_key_map, ["shoot", False])
        self.accept("lshift", base.camera_controls.scope)
        self.accept("escape", base.mouse_controls.switch_state)

class Game(ShowBase):
    def __init__(self):
        super().__init__(self)
        self.settings = GameSettings()
        self.settings.apply_settings()
        self.world = GameWorld()
        self.controls = GameControls()
        self.mouse_controls = MouseControl()
        self.camera_controls = CameraControl()
        self.controls.setup_controls()
        self.updateTask = self.taskMgr.add(self.update, "update")
        self.mouse_controls.capture()
        self.allTanks = NodePath("Tanks")
        self.allTanks.reparentTo(render)
        self.localPlayer = Tank("localPlayer", Vec3(-30, -15, 0), False, self.allTanks)
        self.render.setAntialias(AntialiasAttrib.MAuto)
        self.enable_debug()
        self.display_scene_graph(render)

    def update(self, task):
        dt = globalClock.getDt()

        self.camera_controls.update_camera_rotation(dt)
        self.camera_controls.update_camera_position(dt)
        self.world.bullet_world.doPhysics(dt)

        return task.cont

    def enable_debug(self):
        debug_node = BulletDebugNode("debug")
        debug_node.showWireframe(True)
        debug_node.showNormals(True)
        debug_node.showBoundingBoxes(True)
        debugNP = self.render.attachNewNode(debug_node)
        self.world.bullet_world.setDebugNode(debug_node)
        debugNP.show()

    def display_scene_graph(self, node):
        def dfs(node, tabs=1):
            print("   " * (tabs-1) + "╰--" + node.getName())
            for neighbour in node.getChildren():
                dfs(neighbour, tabs=tabs+1)

        for nd in render.getChildren():
            print(render)
            dfs(nd)