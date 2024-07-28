import numpy as np

class Livox():
    def generate_scan(self, max_distance, scans, density, k, current_frame):

        angle = 38.4 / 2
        radius = np.tan(np.radians(angle))
        a = radius / 2
        results = []
        start = current_frame * 2.0 * np.pi / k

        for i in range(scans):
            p = k + i
            vals = [self.logit(x) for x in np.linspace(0.01, 0.99, density)]
            vals -= np.min(vals)
            vals /= np.max(vals)

            for _ in range(density):
                lily_half = (np.pi / k) * 0.5 + start * (2 * np.pi / k)
                q = np.random.randint(0, 2 * k) * lily_half + lily_half * np.random.choice(vals, 1)[0]
                r = a * np.sin(start + p + q * k)
                x = r * np.cos(q)
                y = r * np.sin(q)

                #pass this as res
                # this should be in the basescanner...
                direction_local = Vector((x, y, 1)).normalized()
                direction_world = rotation_matrix @ direction_local

                hit, loc, norm, idx, obj_hit, mw = scene.ray_cast(depsgraph, start_point, direction_world)

                if hit and (loc - start_point).length <= max_distance:
                    loc_relative = world_matrix.inverted() @ loc
                    results.append(Vector(loc_relative))


        return results

    @staticmethod
    def logit(x):
        return np.log(x / (1 - x))