import numpy as np

def logit(x):
    return np.log(x / (1 - x))

def livox_mid_40(current_frame, params):

    scans = params["scans"]
    density = params["density"]
    k = params["k"]

    angle = 38.4 / 2
    radius = np.tan(np.radians(angle))
    a = radius / 2
    results = []
    start = current_frame * 2.0 * np.pi / k

    for i in range(scans):
        p = k + i
        vals = [logit(x) for x in np.linspace(0.01, 0.99, density)]
        vals -= np.min(vals)
        vals /= np.max(vals)

        for _ in range(density):
            lily_half = (np.pi / k) * 0.5 + start * (2 * np.pi / k)
            q = np.random.randint(0, 2 * k) * lily_half + lily_half * np.random.choice(vals, 1)[0]
            r = a * np.sin(start + p + q * k)
            x = r * np.cos(q)
            y = r * np.sin(q)

            results.append((1,x,y))
    return results
