import numpy as np

def logit(x):
    return np.log(x / (1 - x))


def rot_x(angle, vec):
    angle = np.radians(angle)
    M = np.array([[1,0,0], [0,np.cos(angle), -np.sin(angle)], [0,np.sin(angle),np.cos(angle)]])
    return M @ vec

def rot_y(angle, vec):
    angle = np.radians(angle)
    M = np.array([[np.cos(angle),0,np.sin(angle)], [0,1,0], [-np.sin(angle),0,np.cos(angle)]])
    return M @ vec

def rot_z(angle, vec):
    angle = np.radians(angle)
    M = np.array([[np.cos(angle),-np.sin(angle),0], [np.sin(angle),np.cos(angle),0],[0,0,1]])
    return M @ vec



def demo(current_frame, params):

    results = []
    results.append((1,1,1))
    return results




def velodyne_hdl64(current_frame, params):

    results = []

    v0 = np.array([1,0,0])
    v1 = rot_y(-10, np.array([1,0,0]))
    v2 = rot_y(-5, np.array([1,0,0]))
    v3 = rot_y(5, np.array([1,0,0]))
    v4 = rot_y(10, np.array([1,0,0]))
    v5 = rot_y(-20, np.array([1,0,0]))
    v6 = rot_y(20, np.array([1,0,0]))

    for i in range(360):
        results.append(rot_z(i, v0))
        results.append(rot_z(i, v1))
        results.append(rot_z(i, v2))
        results.append(rot_z(i, v3))
        results.append(rot_z(i, v4))
        results.append(rot_z(i, v5))
        results.append(rot_z(i, v6))
    return results





def livox_mid_40(current_frame, params):

    scans = params["scans"]
    density = params["density"]
    k = params["k"]

    angle = 38.4 / 2
    radius = np.tan(np.radians(angle))
    a = radius #/ 2
    results = []
    start = current_frame * 2.0 * np.pi / k

    for i in range(scans):
        p = k + i + current_frame
        vals = [logit(x) for x in np.linspace(0.01, 0.99, density)]
        vals -= np.min(vals)
        vals /= np.max(vals)

        lily_half = (np.pi / k) * 0.5 + start * (2 * np.pi / k)
        q = sorted([np.random.randint(0, 2 * k) * lily_half + lily_half * np.random.choice(vals, 1)[0] for _ in range(density)])
        
        
        for e in q:
            r = a * np.sin(start + p + e * k)
            x = r * np.cos(e)
            y = r * np.sin(e)

            results.append((1,x,y))
    return results