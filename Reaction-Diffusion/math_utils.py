def clamp01(x):
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def idx(x, y, size):
    return y * size + x


def idx3(x, y, z, size):
    return z * size * size + y * size + x


def normalize_field(field):
    fmin = min(field)
    fmax = max(field)
    if abs(fmax - fmin) < 1e-12:
        return [0.0] * len(field)
    inv = 1.0 / (fmax - fmin)
    return [(x - fmin) * inv for x in field]


def fitzhugh_rest_state(a, b):
    """
    Rest state for:
        du/dt = u - u^3/3 - v
        dv/dt = eps * (u + a - b*v)
    """
    u = -1.0

    for _ in range(30):
        f = u - (u * u * u) / 3.0 - (u + a) / b
        df = 1.0 - u * u - 1.0 / b

        if abs(df) < 1e-12:
            break

        u -= f / df

    v = (u + a) / b
    return u, v
