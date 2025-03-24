from panda3d.bullet import BulletSphereShape, BulletCharacterControllerNode
from panda3d.core import Vec3, WindowProperties
from math import radians, cos, sin


class CameraControl:
    def __init__(self):
        self.camera_speed = 2000
        self.is_spectating = True
        base.camLens.setFov(base.settings.fov)

        self.cam_obj = BulletCharacterControllerNode(BulletSphereShape(1.1), 0.2, "camera collision")
        self.cam_obj.setGravity(0.0)
        self.camera_control_node = render.attachNewNode(self.cam_obj)

        base.world.bullet_world.attachCharacter(self.camera_control_node.node())

        self.camera_control_node.setPos(Vec3(10, 10, 20))

        self.moving_vec = Vec3(0, 0, 0)
        self.target_vec = Vec3(0, 0, 0)
        self.acceleration = 16  # ускорение

    def update_camera_position(self, dt):
        if self.is_spectating:
            self.target_vec = Vec3(0, 0, 0)
            h = camera.getH()
            p = camera.getP()
            if base.controls.key_map["forward"]:
                self.target_vec.x -= self.camera_speed * sin(radians(h))
                self.target_vec.y += self.camera_speed * cos(radians(h))
                self.target_vec.z += self.camera_speed * sin(radians(p))
            if base.controls.key_map["backward"]:
                self.target_vec.x += self.camera_speed * sin(radians(h))
                self.target_vec.y -= self.camera_speed * cos(radians(h))
                self.target_vec.z -= self.camera_speed * sin(radians(p))
            if base.controls.key_map["left"]:
                self.target_vec.x -= self.camera_speed * cos(radians(h))
                self.target_vec.y -= self.camera_speed * sin(radians(h))
            if base.controls.key_map["right"]:
                self.target_vec.x += self.camera_speed * cos(radians(h))
                self.target_vec.y += self.camera_speed * sin(radians(h))
            if base.controls.key_map["up"]:
                self.target_vec.z += self.camera_speed
            if base.controls.key_map["down"]:
                self.target_vec.z -= self.camera_speed

            self.moving_vec = self.moving_vec + (self.target_vec - self.moving_vec) * self.acceleration * dt

            self.cam_obj.setLinearMovement(self.moving_vec * dt, False)
            camera.setPos(self.camera_control_node.getPos())

        else:
            pass  # когда камера прикреплена к танку

    def update_camera_rotation(self, dt):
        if base.mouse_controls.is_captured:
            delta_x, delta_y = base.mouse_controls.get_movement()

            # Применяем поворот
            new_h = camera.getH() - delta_x * dt * base.mouse_controls.sensitivity  # нет ограничений: можем вертеть камерой по оси X на 360 градусов
            new_p = camera.getP() - delta_y * dt * base.mouse_controls.sensitivity
            new_p = min(90, max(-90, new_p))  # а тут ограничения есть:
            # мы не можем поднимать камеру выше 90 градусов и ниже -90
            # так что мы ограничиваем возможный диапазон между -90 и 90 градусов
            camera.setHpr(new_h, new_p, 0)
            self.camera_control_node.setHpr(new_h, new_p, 0)

    def scope(self):
        pass  # прицел-zoom


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
