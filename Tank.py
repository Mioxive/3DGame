import math

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode, BulletVehicle, ZUp, \
    BulletHingeConstraint
from panda3d.core import NodePath, Vec3, Point3, AlphaTestAttrib, RenderAttrib, TransformState
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import BitMask32
from math import sin, cos, radians, pi, gamma


class Tank:
    def __init__(self, name="tank", pos=Vec3(0, 0, 0), hascamera=False, node=None):
        self.cs = None
        self.name = name
        self.model = loader.loadModel("./tank/tank.bam")

        self.main_tank_node = NodePath(f"tank {name}")
        self.main_tank_node.reparentTo(node)
        self.model.reparentTo(self.main_tank_node)
        self.main_tank_node.setPos(pos)
        self.has_camera = hascamera
        self.hp = 1000
        self.engine_force = 30000
        self.angle = self.model.getH()
        self.gun_angle = 0
        self.start_pos = pos
        self.max_motor_impulse = 13000
        self.gain = 200000
        self.max_turret_speed = 30.0

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

        self.vehicle = BulletVehicle(base.world.bullet_world, self.hull_body_node.node())
        base.world.bullet_world.attachVehicle(self.vehicle)

        self.add_wheel(0, Point3(-2.5, 2, 0.5))
        self.add_wheel(1, Point3(1.5, 2, 0.5))
        self.add_wheel(2, Point3(-2.5, -3, 0.5))
        self.add_wheel(3, Point3(1.5, -3, 0.5))

        self.vehicle.tuning.setSuspensionStiffness(20)
        self.vehicle.tuning.setSuspensionDamping(10)
        self.vehicle.tuning.setSuspensionCompression(4)

        taskMgr.add(self.update, "tank_update")

    def setup_tank_collision(self):
        hull_mesh = BulletTriangleMesh()
        for geom_node in self.hull.findAllMatches("**/+GeomNode"):
            for i in range(geom_node.node().getNumGeoms()):
                hull_mesh.addGeom(geom_node.node().getGeom(i))

        hull_shape = BulletTriangleMeshShape(hull_mesh, dynamic=True)
        hull_body = BulletRigidBodyNode("hull")
        hull_body.setMass(20000)
        hull_body.setFriction(0.3)
        hull_body.addShape(hull_shape)
        hull_body.setDeactivationEnabled(False)

        self.hull_body_node = self.main_tank_node.attachNewNode(hull_body)
        base.world.bullet_world.attachRigidBody(hull_body)

        turret_mesh = BulletTriangleMesh()
        for geom_node in self.turret.findAllMatches("**/+GeomNode"):
            for i in range(geom_node.node().getNumGeoms()):
                turret_mesh.addGeom(geom_node.node().getGeom(i))

        turret_shape = BulletTriangleMeshShape(turret_mesh, dynamic=True)
        turret_body = BulletRigidBodyNode("turret")
        turret_body.setMass(7500)
        turret_body.setAngularDamping(0.5)
        turret_body.setFriction(0.3)
        turret_body.addShape(turret_shape)
        turret_body.setDeactivationEnabled(False)
        self.turret_body_node = self.main_tank_node.attachNewNode(turret_body)

        base.world.bullet_world.attachRigidBody(turret_body)

        self.cs = BulletHingeConstraint(turret_body, hull_body, Point3(0, -0.4, 2.4), Point3(0, 0, 2.5), Vec3(0, 0, 1), Vec3(0, 0, 1))
        self.cs.setAxis(Vec3(0, 0, 1))
        self.cs.setDebugDrawSize(2.0)


        base.world.bullet_world.attachConstraint(self.cs, False)

        self.hull_body_node.setCollideMask(BitMask32.allOff())
        self.turret_body_node.setCollideMask(BitMask32.allOff())

    def add_wheel(self, num, pos):
        wheel_radius = 0.4
        suspension_rest_length = 0.4
        friction_slip = 20

        wheel = self.vehicle.createWheel()

        wheel.setNode(self.hull_body_node.attachNewNode(f"wheel {num}").node())
        wheel.setChassisConnectionPointCs(pos)
        wheel.setWheelDirectionCs(Vec3(0, 0, -1))
        wheel.setWheelAxleCs(Vec3(1, 0, 0))
        wheel.setWheelRadius(wheel_radius)
        wheel.setMaxSuspensionTravelCm(suspension_rest_length * 70)
        wheel.setRollInfluence(0.005)
        wheel.setFrictionSlip(friction_slip)
        wheel.setFrontWheel(False)

    def update(self, task):
        dt = globalClock.getDt()

        if self.hp <= 0:
            self.main_tank_node.hide()

        self.update_position(dt)
        self.update_model()
        self.update_turret_position(camera.getH(), dt)

        return task.cont

    def update_model(self):

        self.hull.setHpr(self.hull_body_node.getHpr())
        self.turret.setHpr(self.turret_body_node.getHpr())
        self.gun.setHpr(self.turret.getHpr())
        self.hull.setPos(self.hull_body_node.getPos())
        self.turret.setPos(self.turret_body_node.getPos())
        self.gun.setPos(self.turret_body_node.getPos())

    def update_position(self, dt):
        if self.has_camera:
            for i in range(self.vehicle.getNumWheels()):
                self.vehicle.applyEngineForce(0, i)
                self.vehicle.setBrake(0, i)

            force_move = 0.0
            force_turn = 0.0

            turn_inf = 30

            if base.controls.key_map["forward"]:
                force_move = self.engine_force
            elif base.controls.key_map["backward"]:
                force_move = -self.engine_force

            if base.controls.key_map["left"]:
                force_turn = self.engine_force * turn_inf
            elif base.controls.key_map["right"]:
                force_turn = -self.engine_force * turn_inf

            force_left = force_move - force_turn
            force_right = force_move + force_turn

            if not base.controls.key_map["forward"] and not base.controls.key_map["backward"]:
                if base.controls.key_map["left"]:
                    force_left = -self.engine_force * turn_inf
                    force_right = self.engine_force * turn_inf
                elif base.controls.key_map["right"]:
                    force_left = self.engine_force * turn_inf
                    force_right = -self.engine_force * turn_inf

            self.vehicle.applyEngineForce(force_left, 0)
            self.vehicle.applyEngineForce(force_left, 2)

            self.vehicle.applyEngineForce(force_right, 1)
            self.vehicle.applyEngineForce(force_right, 3)

    def update_turret_position(self, target_angle, dt):
        current_angle = self.cs.getHingeAngle() + self.hull_body_node.getH()
        offset = target_angle - current_angle

        if offset > 180:
            offset = 360 - offset
            if offset > self.max_turret_speed:
                offset = self.max_turret_speed
        elif offset < -180:
            offset = 360 + offset
            if offset < -self.max_turret_speed:
                offset = -self.max_turret_speed
        elif offset == 180 or offset == -180:
            offset = self.max_turret_speed

        if abs(offset) < 0.5:
            offset = 0
            self.cs.enableAngularMotor(False, 0, 0)

        offset = offset * self.gain * dt

        self.cs.enableAngularMotor(True, offset, self.max_motor_impulse)


    def getPos(self):
        return self.hull_body_node.getPos() + self.start_pos

    def getPosForCamera(self):
        return self.turret_body_node.getPos() + self.start_pos

    def getHpr(self):
        return self.model.getHpr()