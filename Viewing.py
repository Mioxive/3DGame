from panda3d.bullet import BulletSphereShape, BulletRigidBodyNode
from panda3d.core import Vec3, WindowProperties, BitMask32, Point3
from math import radians, cos, sin


class CameraControl:
    def __init__(self):
        self.camera_speed = 10
        self.is_spectating = True
        base.camLens.setFov(base.settings.fov)

        self.cam_obj = BulletRigidBodyNode("camera collision")

        self.cam_obj.setMass(1)
        self.cam_obj.addShape(BulletSphereShape(0.4))

        self.camera_control_node = render.attachNewNode(self.cam_obj)
        base.world.bullet_world.attachRigidBody(self.cam_obj)

        self.camera_control_node.setPos(Vec3(10, 10, 20))
        # camera.reparentTo(self.camera_control_node)


    def update_camera_position(self, dt):
        if self.is_spectating:
            x_offset = 0
            y_offset = 0
            z_offset = 0
            h = camera.getH()
            p = camera.getP()
            if base.controls.key_map["forward"]:
                x_offset -= dt * self.camera_speed * sin(radians(h)) # ниче сложного, в пеинте поигрался и понял как это работает
                y_offset += dt * self.camera_speed * cos(radians(h))
                z_offset += dt * self.camera_speed * sin(radians(p))
            if base.controls.key_map["backward"]:
                x_offset += dt * self.camera_speed * sin(radians(h))
                y_offset -= dt * self.camera_speed * cos(radians(h))
                z_offset -= dt * self.camera_speed * sin(radians(p))
            if base.controls.key_map["left"]:
                x_offset -= dt * self.camera_speed * cos(radians(h))
                y_offset -= dt * self.camera_speed * sin(radians(h))
            if base.controls.key_map["right"]:
                x_offset += dt * self.camera_speed * cos(radians(h))
                y_offset += dt * self.camera_speed * sin(radians(h))
            if base.controls.key_map["up"]:
                z_offset += dt * self.camera_speed
            if base.controls.key_map["down"]:
                z_offset -= dt * self.camera_speed

            camera.setPos(camera.getPos() + Vec3(x_offset, y_offset, z_offset))
        else:
            pass # когда камера прикреплена к танку

    def update_camera_rotation(self, dt):
        if base.mouse_controls.is_captured:
            delta_x, delta_y = base.mouse_controls.get_movement()

            # Применяем поворот
            new_h = camera.getH() - delta_x * dt * base.mouse_controls.sensitivity # нет ограничений: можем вертеть камерой по оси X на 360 градусов
            new_p = camera.getP() - delta_y * dt * base.mouse_controls.sensitivity
            new_p = min(90, max(-90, new_p))    # а тут ограничения есть:
                                                # мы не можем поднимать камеру выше 90 градусов и ниже -90 (сам попробуй сальто головой сделать)
                                                # так что мы ограничиваем возможный диапазон между -90 и 90 градусов
            camera.setHpr(new_h, new_p, 0)



    def scope(self):
        pass # прицел-zoom

class MouseControl:
    def __init__(self):
        self.sensitivity = base.settings.sensitivity

        self.center_x = base.win.getXSize() // 2
        self.center_y = base.win.getYSize() // 2
        self.last_mouse_x = self.center_x
        self.last_mouse_y = self.center_y

        self.is_captured = False

    def capture(self):
        if base.mouseWatcherNode.hasMouse():
            self.is_captured = True
            base.settings.winproperties.setCursorHidden(True)
            base.settings.winproperties.setMouseMode(WindowProperties.M_confined)
            base.settings.apply_settings()
            self.center()


    def release(self):
        self.is_captured = False
        base.settings.winproperties.setCursorHidden(False)
        base.settings.winproperties.setMouseMode(WindowProperties.M_absolute)
        base.settings.apply_settings()

    def get_movement(self):
        md = base.win.getPointer(0)
        current_x = md.getX()
        current_y = md.getY()

        delta_x = current_x - self.last_mouse_x
        delta_y = current_y - self.last_mouse_y

        if self.is_captured:
            self.center()
            delta_x += (current_x - self.center_x)
            delta_y += (current_y - self.center_y)

        return delta_x, delta_y


    def center(self):
        base.win.movePointer(0, self.center_x, self.center_y)
        self.last_mouse_x = self.center_x
        self.last_mouse_y = self.center_y

    def switch_state(self):
        if self.is_captured:
            self.release()
        else:
            self.capture()
