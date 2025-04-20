from panda3d.bullet import BulletSphereShape, BulletCharacterControllerNode
from panda3d.core import Vec3, WindowProperties, NodePath, BitMask32
from math import radians, cos, sin


class CameraControl:
    def __init__(self):
        self.camera_speed = 25
        self.max_ray_len = 500
        self.is_spectating = True
        base.camLens.setFov(base.settings.fov)

        self.main_cam_node = NodePath("camera stuff")
        self.main_cam_node.reparentTo(render)
        self.local_player = None

        self.cam_obj = BulletCharacterControllerNode(BulletSphereShape(1.1), 0.2, "camera collision")
        self.cam_obj.setGravity(0.0)

        self.camera_control_node = self.main_cam_node.attachNewNode(self.cam_obj)
        self.camera_control_node.setCollideMask(BitMask32.allOn())
        base.world.bullet_world.attachCharacter(self.camera_control_node.node())

        self.camera_control_node.setPos(Vec3(10, 10, 20))
        camera.reparentTo(self.main_cam_node)

        self.moving_vec = Vec3(0, 0, 0)
        self.target_vec = Vec3(0, 0, 0)
        self.acceleration = 16  # ускорение

        self.smooth_factor = 0.2
        self.last_slide_direction = Vec3(0, 0, 0)

    def check_collision(self, start_pos, end_pos):
        result = base.world.bullet_world.rayTestClosest(start_pos, end_pos)
        if result.hasHit():
            hit_pos = result.getHitPos()
            return hit_pos + (start_pos - end_pos).normalized()
        return end_pos

    def check_collision2(self, start_pos, end_pos):
        result = base.world.bullet_world.rayTestClosest(start_pos, end_pos)
        if result.hasHit():
            hit_pos = result.getHitPos()
            return hit_pos
        return end_pos

    def shoot_collision_ray(self):
        start_pos = self.camera_control_node.getPos()

        end_pos = start_pos + Vec3(
            -sin(radians(camera.getH())),
            cos(radians(camera.getH())),
            sin(radians(camera.getP()))
        ) * self.max_ray_len
        result = self.check_collision2(start_pos, end_pos)
        return result

    def update_camera_position(self, dt):
        # НЕ СМОТРИТЕ СЮДА!!!!
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

            self.moving_vec += (self.target_vec - self.moving_vec) * (1 - self.smooth_factor) * self.acceleration * dt

            self.cam_obj.setLinearMovement(self.moving_vec, False)
            camera.setPos(self.camera_control_node.getPos())

        else:
            sphere_radius = 10
            target_pos = self.local_player.getPosForCamera() - Vec3(
                sin(radians(-camera.getH())) * sphere_radius,
                cos(radians(camera.getH())) * sphere_radius,
                sin(radians(camera.getP())) * sphere_radius - 6
            )
            # дальше идет сложное нечто: сглаживание движения камеры от чата гпт

            # проверяем коллизию от текущей позиции к целевой
            current_pos = self.camera_control_node.getPos()
            new_pos = self.check_collision(current_pos, target_pos)  # позиция, уменьшенная до точки столкновения

            if (
                    new_pos - target_pos).length() > 0.1:  # если позиция камеры не совпадает с целевой (то есть произошло столкновение)
                # находим направление от танка к камере
                tank_to_cam = new_pos - self.local_player.getPos()
                tank_to_cam.normalize()

                # вычисляем новое направление скольжения (перпендикулярно направлению к танку)
                slide_direction = Vec3(-tank_to_cam.y, tank_to_cam.x, 0)

                # сглаживаем изменение направления скольжения
                self.last_slide_direction = self.last_slide_direction * (
                            1 - self.smooth_factor) + slide_direction * self.smooth_factor
                self.last_slide_direction.normalize()

                # пытаемся найти новую позицию, скользя по стене
                slide_attempt = new_pos + self.last_slide_direction * sphere_radius * 0.1
                slide_pos = self.check_collision(new_pos, slide_attempt)

                # если скольжение в этом направлении невозможно, пробуем в противоположном
                if (slide_pos - new_pos).length() < 0.01:
                    slide_direction = -slide_direction
                    self.last_slide_direction = slide_direction
                    slide_attempt = new_pos + slide_direction * sphere_radius * 0.1
                    slide_pos = self.check_collision(new_pos, slide_attempt)

                new_pos = slide_pos

            # сглаживаем движение камеры
            final_pos = current_pos * (1 - self.smooth_factor) + new_pos * self.smooth_factor
            self.camera_control_node.setPos(final_pos)
            camera.setPos(self.camera_control_node.getPos())

    def update_camera_rotation(self, dt):
        if base.mouse_controls.is_captured:
            delta_x, delta_y = base.mouse_controls.get_movement()

            new_h = camera.getH() - delta_x * dt * base.mouse_controls.sensitivity  # нет ограничений: можем вертеть камерой по оси X на 360 градусов
            new_p = camera.getP() - delta_y * dt * base.mouse_controls.sensitivity
            new_p = min(90, max(-90, new_p))
            camera.setHpr(new_h, new_p, 0)
            self.camera_control_node.setHpr(new_h, new_p, 0)

    def attach_player(self, player):
        self.local_player = player
        player.has_camera = True
        self.is_spectating = False
        self.camera_control_node.setPos(self.local_player.getPos() - Vec3(0, 10, -6))

    def unattach_player(self):
        self.local_player.has_camera = False
        self.local_player = None
        self.is_spectating = True

    def scope(self):
        if self.local_player and not self.is_spectating:
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
