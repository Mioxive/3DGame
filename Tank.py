from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode, BulletVehicle, ZUp
from panda3d.core import NodePath, Vec3, Point3
from direct.showbase.ShowBaseGlobal import globalClock


class Tank:
    def __init__(self, name="tank", pos=Vec3(0, 0, 0), hascamera=False, node=None):
        self.name = name
        self.model = loader.loadModel("./tank/tank.bam")
        self.main_tank_node = NodePath(f"tank {name}")
        self.main_tank_node.reparentTo(node)
        self.model.reparentTo(self.main_tank_node)
        self.main_tank_node.setPos(pos)
        self.main_tank_node.setScale(0.6)
        self.has_camera = hascamera
        self.hp = 1000

        self.gun = self.model.find("**/gun/gun.001") # FIXME оно вроде разделяет, но по отдельности не вращается, вращается весь танк
        self.hull = self.model.find("**/hull/hull.001")
        self.turret = self.model.find("**/turret/turret.001")

        self.model.flattenStrong()
        # коллизии
        mesh = BulletTriangleMesh()
        for geom_node in self.model.findAllMatches("**/+GeomNode"):
            for i in range(geom_node.node().getNumGeoms()):
                mesh.addGeom(geom_node.node().getGeom(i))

        shape = BulletTriangleMeshShape(mesh, dynamic=True)

        tank_body = BulletRigidBodyNode(name)
        tank_body.setMass(1000)
        tank_body.setStatic(False)
        tank_body.addShape(shape)
        tank_body.setFriction(0.5)

        self.tank_body_node = self.main_tank_node.attachNewNode(tank_body)
        base.world.bullet_world.attachRigidBody(tank_body)

        # создание машины
        self.vehicle = BulletVehicle(base.world.bullet_world, tank_body)
        self.vehicle.setCoordinateSystem(ZUp)
        base.world.bullet_world.attachVehicle(self.vehicle)


        self.steering = 0
        self.steering_clamp = 90
        self.steering_increment = 5
        self.engine_force = 0
        self.brake_force = 0
        self.max_engine_force = 2000
        self.max_brake_force = 1000

        # колеса
        self.add_wheel(Vec3(1.3, 2.5, 0.3), True)  # переднее левое
        self.add_wheel(Vec3(-1.85, 2.5, 0.3), True)  # переднее правое
        self.add_wheel(Vec3(1.3, -2.5, 0.3), False)  # заднее левое
        self.add_wheel(Vec3(-1.85, -2.5, 0.3), False)  # заднее правое

        
        base.taskMgr.add(self.update, "updateTank")


    def add_wheel(self, pos, is_front):
        wheel = self.vehicle.createWheel()
        wheel.setChassisConnectionPointCs(Point3(pos))
        wheel.setFrontWheel(is_front)

        wheel.setWheelDirectionCs(Vec3(0, 0, -1))
        wheel.setWheelAxleCs(Vec3(1, 0, 0))
        wheel.setWheelRadius(0.2)
        wheel.setMaxSuspensionTravelCm(40.0)

        wheel.setSuspensionStiffness(40.0)
        wheel.setWheelsDampingRelaxation(2.3)
        wheel.setWheelsDampingCompression(4.4)
        wheel.setFrictionSlip(100.0)
        wheel.setRollInfluence(0.1)


    
    def update(self, task):
        dt = globalClock.getDt()

        if self.hp <= 0:
            self.model.hide()

        self.update_tank_pos(dt)
        self.model.setPosHpr(self.tank_body_node.getPos(), self.tank_body_node.getHpr())
        self.gun.setHpr(self.turret.getHpr())

        return task.cont

    def update_tank_pos(self, dt):
        if self.has_camera:
            pass

    def getPos(self):
        return self.tank_body_node.getPos()

    def getHpr(self):
        return self.tank_body_node.getHpr()