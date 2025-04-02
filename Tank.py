from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode, BulletVehicle, ZUp
from panda3d.core import NodePath, Vec3, Point3, AlphaTestAttrib, RenderAttrib
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import BitMask32

class Tank:
    def __init__(self, name="tank", pos=Vec3(0, 0, 0), hascamera=False, node=None):
        self.name = name
        self.model = loader.loadModel("./tank/tank.bam")

        self.main_tank_node = NodePath(f"tank {name}")
        self.main_tank_node.reparentTo(node)
        self.model.reparentTo(self.main_tank_node)
        self.main_tank_node.setPos(pos)
        self.has_camera = hascamera
        self.hp = 1000

        # разделение на составляющие для управления частями танка
        self.gun = self.model.find("**/gun")
        self.hull = self.model.find("**/hull")
        self.turret = self.model.find("**/turret")

        self.hull.flattenStrong()
        self.gun.flattenStrong()
        self.turret.flattenStrong()

        # коллизии
        mesh = BulletTriangleMesh()
        for geom_node in self.model.findAllMatches("**/+GeomNode"):
            for i in range(geom_node.node().getNumGeoms()):
                mesh.addGeom(geom_node.node().getGeom(i))

        shape = BulletTriangleMeshShape(mesh, dynamic=True)

        tank_body = BulletRigidBodyNode(name)
        tank_body.setMass(30000)
        tank_body.setStatic(False)
        tank_body.addShape(shape)
        tank_body.setFriction(0.3)

        self.tank_body_node = self.main_tank_node.attachNewNode(tank_body)
        base.world.bullet_world.attachRigidBody(tank_body)

        self.tank_body_node.setCollideMask(BitMask32.allOff())

        taskMgr.add(self.update, "tank_update")
    
    def update(self, task):
        dt = globalClock.getDt()

        if self.hp <= 0:
            self.model.hide()

        self.update_model()

        return task.cont

    def update_model(self):
        self.model.setPosHpr(self.tank_body_node.getPos(), self.tank_body_node.getHpr())
        self.gun.setHpr(self.turret.getHpr())