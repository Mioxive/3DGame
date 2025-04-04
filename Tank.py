from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode, BulletVehicle, ZUp, \
    BulletHingeConstraint
from panda3d.core import NodePath, Vec3, Point3, AlphaTestAttrib, RenderAttrib
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import BitMask32
from math import sin, cos, radians


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
        self.angle = self.model.getH()
        self.gun_angle = 0
        self.start_pos = pos

        # разделение на составляющие для управления частями танка
        self.gun = self.model.find("**/gun")
        self.hull = self.model.find("**/hull")
        self.turret = self.model.find("**/turret")

        self.hull.flattenStrong()
        self.gun.flattenStrong()
        self.turret.flattenStrong()

        self.hull_body_node = None
        self.turret_body_node = None

        self.setup_tank_collision()

        taskMgr.add(self.update, "tank_update")

    def setup_tank_collision(self):
        hull_mesh = BulletTriangleMesh()
        for geom_node in self.hull.findAllMatches("**/+GeomNode"):
            for i in range(geom_node.node().getNumGeoms()):
                hull_mesh.addGeom(geom_node.node().getGeom(i))

        hull_shape = BulletTriangleMeshShape(hull_mesh, dynamic=True)
        hull_body = BulletRigidBodyNode("hull")
        hull_body.setMass(40000)
        hull_body.setFriction(0.3)
        hull_body.addShape(hull_shape)

        self.hull_body_node = self.main_tank_node.attachNewNode(hull_body)
        base.world.bullet_world.attachRigidBody(hull_body)


        turret_mesh = BulletTriangleMesh()
        for geom_node in self.turret.findAllMatches("**/+GeomNode"):
            for i in range(geom_node.node().getNumGeoms()):
                turret_mesh.addGeom(geom_node.node().getGeom(i))

        turret_shape = BulletTriangleMeshShape(turret_mesh, dynamic=True)
        turret_body = BulletRigidBodyNode("turret")
        turret_body.setMass(15000)
        turret_body.setFriction(0.3)
        turret_body.addShape(turret_shape)
        self.turret_body_node = self.main_tank_node.attachNewNode(turret_body)

        base.world.bullet_world.attachRigidBody(turret_body)


        cs = BulletHingeConstraint(turret_body, hull_body, Point3(0, 0, -0.1), Point3(0, 0, 0), Vec3(0, 0, 1), Vec3(0, 0, 1))
        cs.setDebugDrawSize(2.0)

        base.world.bullet_world.attachConstraint(cs)

        self.hull_body_node.setCollideMask(BitMask32.allOff())
        self.turret_body_node.setCollideMask(BitMask32.allOff())


    def update(self, task):
        dt = globalClock.getDt()

        if self.hp <= 0:
            self.model.hide()

        self.update_position(dt)
        self.update_model()

        return task.cont

    def update_model(self):

        self.hull_body_node.setH(self.angle)


        self.hull.setHpr(self.hull_body_node.getHpr())
        self.turret.setHpr(self.turret_body_node.getHpr())
        self.gun.setHpr(self.turret.getHpr())
        self.model.setPos(self.hull_body_node.getPos())


    def update_position(self, dt):
        if self.has_camera:
            if base.controls.key_map["left"]:
                self.angle += 40 * dt
            if base.controls.key_map["right"]:
                self.angle -= 40 * dt
            if base.controls.key_map["forward"]:
                self.hull_body_node.node().applyCentralForce(Vec3(10 * sin(radians(-self.angle)), 10 * cos(radians(-self.angle)), 0))
            if base.controls.key_map["backward"]:
                self.hull_body_node.node().applyCentralForce(Vec3(-10 * sin(radians(-self.angle)), -10 * cos(radians(-self.angle)), 0))
            


    def getPos(self):
        return self.hull_body_node.getPos() + self.start_pos
        

    def getHpr(self):
        return self.model.getHpr()