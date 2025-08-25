import numpy as np

def perspective(fovy, aspect, near, far):
    f = 1.0 / np.tan(fovy * 0.5 * np.pi / 180.0)
    return np.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)

def lookAt(eye, target, up):
    forward = (target - eye)
    forward = forward / np.linalg.norm(forward)
    
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    
    new_up = np.cross(right, forward)
    
    return np.array([
        [right[0], right[1], right[2], -np.dot(right, eye)],
        [new_up[0], new_up[1], new_up[2], -np.dot(new_up, eye)],
        [-forward[0], -forward[1], -forward[2], np.dot(forward, eye)],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def rotate_y(angle):
    rad = angle * np.pi / 180.0
    c, s = np.cos(rad), np.sin(rad)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)