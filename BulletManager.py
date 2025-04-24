from panda3d.bullet import BulletSphereShape, BulletRigidBodyNode, ZUp
from panda3d.core import Vec3, NodePath

from direct.task.TaskManagerGlobal import taskMgr

class Bullet:
	def __init__(self, pos: Vec3, direction: Vec3, tank, parent):
		self.tank = tank
		self.direction = direction
		
		self.bullet_node = NodePath("bullet_node")
		self.bullet_node.reparentTo(parent)
		
		self.model = loader.loadModel("misc/sphere")
		if self.model:
			self.model.setScale(0.2)
			self.model.setColor(1, 0.7, 0, 1)
			

		self.bullet_node.setPos(pos)
		self.setup_physics()
		self.model.reparentTo(self.physmodel_node)
		self.start()
		
		
	def setup_physics(self):
		shape = BulletSphereShape(0.2)
		self.physmodel = BulletRigidBodyNode('bullet')
		self.physmodel.addShape(shape)
		
		self.physmodel.setMass(1.0)
		self.physmodel.setFriction(0.5)
		self.physmodel.setRestitution(0.5)
		self.physmodel.setLinearDamping(0.1)
		self.physmodel.setAngularDamping(0.5)
		
		self.physmodel_node = self.bullet_node.attachNewNode(self.physmodel)
		
		self.physmodel.setCcdMotionThreshold(1e-7)
		self.physmodel.setCcdSweptSphereRadius(0.3)
		
		base.world.bullet_world.attachRigidBody(self.physmodel)
		
	def start(self):
		self.physmodel.applyCentralImpulse(self.direction * 2000)

	def check_collision(self):
		pos = self.bullet_node.getPos()
		if abs(pos.x) > 1000 or abs(pos.y) > 1000 or abs(pos.z) > 1000:
			return True
		try:
			result = base.world.bullet_world.contactTest(self.physmodel)
			if result.getNumContacts() > 0:
				for contact in result.getContacts():
					if contact.getNode0() == self.physmodel:
						contact_node = contact.getNode1()
						if contact_node.getPythonTag('tank') is not None:
							tank = contact_node.getPythonTag('tank')
							tank.damage(200)
							print("Bullet hit tank")
							return True
					elif contact.getNode1() == self.physmodel:
						contact_node = contact.getNode0()
						if contact_node.getPythonTag('tank') is not None:
							tank = contact_node.getPythonTag('tank')
							tank.damage(200)
							print("Bullet hit tank")
							return True
				return True
		except Exception as e:
			print(f"Error: {e}")
			return True
		return False
	
	def destroy(self):

		if self.physmodel in base.world.bullet_world.getRigidBodies():
			base.world.bullet_world.removeRigidBody(self.physmodel)

		self.model.removeNode()
		self.bullet_node.removeNode()
	


class BulletManager:
	def __init__(self):
		self.bullets = []
		self.bullets_group_node = render.attachNewNode("bullets_group_node")
		taskMgr.add(self.update, "bullets_update")

	def add_bullet(self, tank, direction):
		gun_pos = tank.get_gun_position_for_shot()
		
		bullet = Bullet(gun_pos, direction, tank, self.bullets_group_node)
		self.bullets.append(bullet)


	def update(self, task):
		bullets_to_remove = []
		
		for bullet in self.bullets:
			if bullet.check_collision():
				bullets_to_remove.append(bullet)
		
		for bullet in bullets_to_remove:
			if bullet in self.bullets:
				self.bullets.remove(bullet)
				bullet.destroy()

		return task.cont
