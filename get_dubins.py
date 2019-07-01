import numpy as np


class Target:
    def __init__(self, _coords, _direction):
        self.p = _coords
        self.theta = _direction * np.pi / 180
        self.x = np.array([np.cos(self.theta), np.sin(self.theta)])


class circle:
    def __init__(self, _c, _r, _o):
        self.center = _c
        self.radius = _r
        self.orientation = _o


def calcArcLength(p, q, radius, orientation):
    cos_gamma = np.dot(p,q) / np.linalg.norm(p) / (np.linalg.norm(q))
    theta = np.arccos(cos_gamma)
    if cos_gamma > 1:
        theta = 0
    elif cos_gamma < -1:
        theta = np.pi
    return radius * theta if np.cross(p,q) * orientation >= 0 else radius*(2 * np.pi - theta)


def calcDubinsLength(Ti, Tf, r):
    dubins_length = float('inf')
    c, d, path = [], [], []
    # Ti and Tf are points in the tangent bundle.
    # thus, they have the form (p,x) where p is a point in the plane
    # and x is a tangent vector
    # c[0] and c[1] are the centers of the circles, radius r,
    # to which Ti.x is tangent. Similarly for d[0] and d[1].
    c.append(circle(Ti.p + r * perp(Ti.x), r, 1))
    c.append(circle(Ti.p - r * perp(Ti.x), r, -1))
    d.append(circle(Tf.p + r * perp(Tf.x), r, 1))
    d.append(circle(Tf.p - r * perp(Tf.x), r, -1))
    for i in c:
        for j in d:
            if i.orientation == j.orientation:
                # if the centers are coincident, there will be just one arc.
                #  so, let the SR (or SL) components be degenerate.
                if np.linalg.norm(i.center - j.center) == 0:
                    # L, R
                    int1 = Tf.p - i.center
                    int2 = Tf.p - j.center
                    s = calcArcLength(Ti.p - i.center, Tf.p - i.center, r, i.orientation)
                    if i.orientation == 1:
                        path = [('L', s)]
                    else:
                        path = [('R', s)]
                    if s < dubins_length:
                        dubins_length = s
                        dubins_path = path
                else:
                    # RSR, LSL, S
                    int1 = i.center - i.orientation * r * perp(j.center - i.center)
                    int2 = j.center - i.orientation * r * perp(j.center - i.center)
                    s1 = calcArcLength(Ti.p - i.center, int1 - i.center, r, i.orientation)
                    if i.orientation == 1:
                        path = [('L', s1)]
                    else:
                        path = [('R', s1)]
                    s2 = np.linalg.norm(i.center - j.center)
                    path.append(('S', s2))
                    s3 = calcArcLength(int2 - j.center, Tf.p - j.center, r, j.orientation)
                    if j.orientation == 1:
                        path.append(('L', s3))
                    else:
                        path.append(('R', s3))
                    if s1 + s2 + s3 < dubins_length:
                        dubins_length = s1 + s2 + s3
                        dubins_path = path
                    #RLR, LRL
                    if np.linalg.norm(i.center - j.center) < 4 * r:
                        e = circle((i.center+j.center)/2 +  i.orientation * np.sqrt(4 * np.square(r) - np.square(np.linalg.norm((j.center-i.center)/2))) * perp(j.center-i.center), r, -1 * i.orientation)
                        int1 = (i.center + e.center)/2
                        int2 = (e.center + j.center)/2
                        s1 = calcArcLength(Ti.p - i.center, int1 - i.center, r, i.orientation)
                        if i.orientation == 1:
                            path = [('L', s1)]
                        else:
                            path = [('R', s1)]
                        s2 = calcArcLength(int1 - e.center, int2 - e.center, r, -i.orientation)
                        if j.orientation == 1:
                            path.append(('L', s2))
                        else:
                            path.append(('R', s2))
                        s3 = calcArcLength(int2 - j.center, Tf.p - j.center, r, j.orientation)
                        if j.orientation == 1:
                            path.append(('L', s3))
                        else:
                            path.append(('R', s3))
                        if s1 + s2 + s3 < dubins_length:
                            dubins_length = s1 + s2 + s3
                            dubins_path = path
            # RSL, LSR
            else:
                if np.linalg.norm(i.center - j.center) >= 2 * r:
                    c_perp = r * np.sqrt(np.square(np.linalg.norm(j.center - i.center)/2) - np.square(r)) / np.linalg.norm((j.center - i.center)/2)
                    c_parallel = np.linalg.norm((j.center - i.center)/2) - np.square(r) / np.linalg.norm((j.center - i.center)/2)
                    int1 = (i.center + j.center)/2 - i.orientation * c_perp * perp(j.center - i.center) - c_parallel * normalize(j.center - i.center)
                    int2 = (i.center + j.center)/2 + i.orientation * c_perp * perp(j.center - i.center) + c_parallel * normalize(j.center - i.center)
                    s1 = calcArcLength(Ti.p - i.center, int1 - i.center, r, i.orientation)
                    if i.orientation == 1:
                        path = [('L', s1)]
                    else:
                        path = [('R', s2)]
                    s2 = np.linalg.norm(int1 - int2)
                    path.append(('S', s2))
                    s3 = calcArcLength(int2 - j.center, Tf.p - j.center, r, j.orientation)
                    if j.orientation == 1:
                        path.append(('L', s3))
                    else:
                        path.append(('R', s3))
                    if s1 + s2 + s3 < dubins_length:
                        dubins_length = s1 + s2 + s3
                        dubins_path = path
    return dubins_length, dubins_path


def perp(v):
    return np.array([-v[1], v[0]])/np.linalg.norm(v) if np.linalg.norm(v) else v


def normalize(v):
    return v / np.linalg.norm(v) if np.linalg.norm(v) else v


def dubins(start, end, limit_radius, r_road = False):
    Ti = Target(np.array([start[0], start[1]]), start[2])
    Tf = Target(np.array([end[0], end[1]]), end[2])
    length, road = calcDubinsLength(Ti, Tf, limit_radius)
    if r_road:
        return length, road
    return length


if __name__ == '__main__':
    length = dubins([0,0,0],[35,60,60],10)
    print(length)