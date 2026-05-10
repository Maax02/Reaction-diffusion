import random
from array import array

from .deps import rd_core
from .math_utils import clamp01, idx, idx3, fitzhugh_rest_state


def init_gray_scott_state(size, seed=42, perturb=20):
    n = size * size
    u = array('d', [1.0]) * n
    v = array('d', [0.0]) * n

    random.seed(seed)
    half = perturb // 2
    cx = size // 2
    cy = size // 2

    for y in range(cy - half, cy + half):
        for x in range(cx - half, cx + half):
            if 0 <= x < size and 0 <= y < size:
                v[y * size + x] = random.random()

    return u, v

def simulate_gray_scott_fast(size, steps, Du, Dv, F, k, seed=42, perturb=20, do_clamp=True):
    u, v = init_gray_scott_state(size, seed=seed, perturb=perturb)
    rd_core.evolve_gray_scott(u, v, size, steps, Du, Dv, F, k, do_clamp)
    return u, v

def init_brusselator_state(size, A=1.0, B=2.0, seed=42, noise=0.005, perturb=20):
    n = size * size
    u = array('d', [0.0]) * n
    v = array('d', [0.0]) * n

    random.seed(seed)

    u0 = A
    v0 = B / A if A != 0.0 else 0.0

    for i in range(n):
        u[i] = u0 + random.uniform(-noise, noise)
        v[i] = v0 + random.uniform(-noise, noise)

    return u, v


def simulate_brusselator_fast(size, steps, Du, Dv, A, B,
                              dt=0.01, seed=42, noise=0.03, perturb=20):

    u, v = init_brusselator_state(
        size,
        A=A,
        B=B,
        seed=seed,
        noise=noise,
        perturb=perturb,
    )

    rd_core.evolve_brusselator(
        u, v,
        size, steps,
        Du, Dv,
        A, B,
        dt
    )

    return u, v

def init_fitzhugh_nagumo_state(size, a=0.7, b=0.8, seed=42, noise=0.0,
                               perturb=10, strength=2.0,
                               mode="MULTI_SPARK"):
    n = size * size
    u = array('d', [0.0]) * n
    v = array('d', [0.0]) * n

    random.seed(seed)

    u_rest, v_rest = fitzhugh_rest_state(a, b)

    for i in range(n):
        u[i] = u_rest + random.uniform(-noise, noise)
        v[i] = v_rest

    def add_disk(cx, cy, radius, value_u, value_v):
        radius = max(1, min(radius, size // 2))
        r2 = radius * radius

        x0 = max(0, cx - radius)
        x1 = min(size - 1, cx + radius)
        y0 = max(0, cy - radius)
        y1 = min(size - 1, cy + radius)

        for y in range(y0, y1 + 1):
            dy = y - cy
            for x in range(x0, x1 + 1):
                dx = x - cx
                if dx * dx + dy * dy <= r2:
                    i = y * size + x
                    u[i] = value_u
                    v[i] = value_v

    if mode == "CENTER":
        add_disk(size // 2, size // 2, perturb, strength, v_rest)

    elif mode == "TWO_SPARKS":
        add_disk(size // 3, size // 2, perturb, strength, v_rest)
        add_disk((2 * size) // 3, size // 2, perturb, strength, v_rest)

    elif mode == "MULTI_SPARK":
        count = 8
        radius = max(1, min(perturb, size // 6))
        margin = min(radius * 3, max(1, size // 4))

        if size - margin - 1 <= margin:
            add_disk(size // 2, size // 2, radius, strength, v_rest)
        else:
            for _ in range(count):
                cx = random.randint(margin, size - margin - 1)
                cy = random.randint(margin, size - margin - 1)
                add_disk(cx, cy, radius, strength, v_rest)

    elif mode == "BROKEN_LINE":
        y0 = size // 2
        width = max(2, perturb // 3)

        for x in range(size // 5, 4 * size // 5):
            if size // 2 - perturb < x < size // 2 + perturb:
                continue

            for dy in range(-width, width + 1):
                y = y0 + dy
                if 0 <= y < size:
                    i = y * size + x
                    u[i] = strength
                    v[i] = v_rest

    elif mode == "HALF_PLANE":
        width = max(4, perturb)

        for x in range(size // 4, min(size, size // 4 + width)):
            for y in range(size):
                i = y * size + x
                u[i] = strength
                v[i] = v_rest

    else:
        add_disk(size // 2, size // 2, perturb, strength, v_rest)

    return u, v

def simulate_fitzhugh_nagumo_fast(size, steps, Du, Dv, a, b, eps,
                                  dt=0.01, seed=42, noise=0.001,
                                  perturb=20, strength=1.2,
                                  mode="MULTI_SPARK"):
    u, v = init_fitzhugh_nagumo_state(
        size,
        a=a,
        b=b,
        seed=seed,
        noise=noise,
        perturb=perturb,
        strength=strength,
        mode=mode,
    )

    rd_core.evolve_fitzhugh_nagumo(
        u, v,
        size, steps,
        Du, Dv,
        a, b, eps, dt
    )

    return u, v

def init_gray_scott_state_3d(size, seed=42, perturb=8):
    n = size * size * size
    u = array('d', [1.0]) * n
    v = array('d', [0.0]) * n

    random.seed(seed)
    half = perturb // 2
    cx = size // 2
    cy = size // 2
    cz = size // 2

    for z in range(cz - half, cz + half):
        for y in range(cy - half, cy + half):
            for x in range(cx - half, cx + half):
                if 0 <= x < size and 0 <= y < size and 0 <= z < size:
                    v[idx3(x, y, z, size)] = random.random()

    return u, v


def simulate_gray_scott_3d_fast(size, steps, Du, Dv, F, k, seed=42, perturb=8, do_clamp=True):
    u, v = init_gray_scott_state_3d(size, seed=seed, perturb=perturb)
    rd_core.evolve_gray_scott_3d(u, v, size, steps, Du, Dv, F, k, do_clamp)
    return u, v

def init_brusselator_state_3d(size, A=1.0, B=2.0, seed=42, noise=0.002):
    n = size * size * size
    u = array('d', [0.0]) * n
    v = array('d', [0.0]) * n

    random.seed(seed)

    u0 = A
    v0 = B / A if A != 0.0 else 0.0

    for i in range(n):
        u[i] = u0 + random.uniform(-noise, noise)
        v[i] = v0 + random.uniform(-noise, noise)

    return u, v

def simulate_brusselator_3d_fast(size, steps, Du, Dv, A, B,
                                 dt=0.001, seed=42, noise=0.002):
    u, v = init_brusselator_state_3d(
        size,
        A=A,
        B=B,
        seed=seed,
        noise=noise,
    )

    rd_core.evolve_brusselator_3d(
        u, v,
        size, steps,
        Du, Dv,
        A, B,
        dt,
    )

    return u, v

def init_fitzhugh_nagumo_state_3d(size, a=0.7, b=0.8, seed=42, noise=0.0,
                                  perturb=4, strength=2.0,
                                  num_sparks=8):
    n = size * size * size
    u = array('d', [0.0]) * n
    v = array('d', [0.0]) * n

    random.seed(seed)

    # Resting state consistent with the selected FitzHugh-Nagumo parameters.
    u_rest, v_rest = fitzhugh_rest_state(a, b)
    for i in range(n):
        r = random.uniform(-noise, noise)
        u[i] = u_rest + r
        v[i] = v_rest

    def add_sphere(cx, cy, cz, radius):
        r2 = radius * radius

        for z in range(cz - radius, cz + radius + 1):
            if z < 0 or z >= size:
                continue

            for y in range(cy - radius, cy + radius + 1):
                if y < 0 or y >= size:
                    continue

                for x in range(cx - radius, cx + radius + 1):
                    if x < 0 or x >= size:
                        continue

                    dx = x - cx
                    dy = y - cy
                    dz = z - cz

                    if dx * dx + dy * dy + dz * dz <= r2:
                        i = idx3(x, y, z, size)
                        u[i] = strength
                        v[i] = v_rest

    radius = max(1, min(perturb, max(1, size // 2)))
    margin = min(radius * 3, max(1, size // 4))

    # For small volumes or large perturb radii, random placement ranges can collapse.
    # Fall back to one central sphere instead of raising ValueError.
    if size - margin - 1 <= margin:
        add_sphere(size // 2, size // 2, size // 2, radius)
    else:
        for _ in range(num_sparks):
            cx = random.randint(margin, size - margin - 1)
            cy = random.randint(margin, size - margin - 1)
            cz = random.randint(margin, size - margin - 1)

            add_sphere(cx, cy, cz, radius)

    return u, v


def simulate_fitzhugh_nagumo_3d_fast(size, steps, Du, Dv,
                                     a, b, eps, dt=0.01,
                                     seed=42, noise=0.0,
                                     perturb=6, strength=2.0, num_sparks=8):
    u, v = init_fitzhugh_nagumo_state_3d(
        size,
        a=a,
        b=b,
        seed=seed,
        noise=noise,
        perturb=perturb,
        strength=strength,
        num_sparks=num_sparks,
    )

    rd_core.evolve_fitzhugh_nagumo_3d(
        u, v,
        size, steps,
        Du, Dv,
        a, b, eps, dt,
    )

    return u, v

def init_model_state_2d(s):
    if s.model == 'GRAY_SCOTT':
        return init_gray_scott_state(
            s.size,
            seed=s.seed,
            perturb=s.perturb_2d,
        )
        
    elif s.model == 'BRUSSELATOR':
        return init_brusselator_state(
            s.size,
            A=s.A,
            B=s.B,
            seed=s.seed,
            noise=s.noise,
            perturb=s.perturb_2d,
        )
        
    elif s.model == 'FITZHUGH_NAGUMO':
        return init_fitzhugh_nagumo_state(
            s.size,
            a=s.fh_a,
            b=s.fh_b,
            seed=s.seed,
            noise=s.noise,
            perturb=s.perturb_2d,
            strength=s.fh_strength,
            mode=s.fh_init_mode,
        )

def evolve_model_2d_inplace(u, v, s, steps_now):
    if s.model == 'GRAY_SCOTT':
        rd_core.evolve_gray_scott(
            u,
            v,
            s.size,
            steps_now,
            s.Du,
            s.Dv,
            s.F,
            s.k,
            s.do_clamp,
        )
        return

    elif s.model == 'BRUSSELATOR':
        rd_core.evolve_brusselator(
            u,
            v,
            s.size,
            steps_now,
            s.Du,
            s.Dv,
            s.A,
            s.B,
            s.dt,
        )
        return
    
    elif s.model == 'FITZHUGH_NAGUMO':
        rd_core.evolve_fitzhugh_nagumo(
            u, v,
            s.size,
            steps_now,
            s.Du,
            s.Dv,
            s.fh_a,
            s.fh_b,
            s.fh_eps,
            s.dt,
        )
        return

def init_model_state_3d(s):
    if s.model == 'GRAY_SCOTT':
        return init_gray_scott_state_3d(
            s.size_3d,
            seed=s.seed,
            perturb=s.perturb_3d,
        )

    elif s.model == 'BRUSSELATOR':
        return init_brusselator_state_3d(
            s.size_3d,
            A=s.A,
            B=s.B,
            seed=s.seed,
            noise=s.noise,
        )

    elif s.model == 'FITZHUGH_NAGUMO':
        return init_fitzhugh_nagumo_state_3d(
            s.size_3d,
            a=s.fh_a,
            b=s.fh_b,
            seed=s.seed,
            noise=s.noise,
            perturb=s.perturb_3d,
            strength=s.fh_strength,
            num_sparks=s.fh_num_sparks,
        )
        

def evolve_model_3d_inplace(u, v, s, steps_now):
    if s.model == 'GRAY_SCOTT':
        rd_core.evolve_gray_scott_3d(
            u, v,
            s.size_3d,
            steps_now,
            s.Du,
            s.Dv,
            s.F,
            s.k,
            s.do_clamp,
        )
        return

    elif s.model == 'BRUSSELATOR':
        rd_core.evolve_brusselator_3d(
            u, v,
            s.size_3d,
            steps_now,
            s.Du,
            s.Dv,
            s.A,
            s.B,
            s.dt,
        )
        return

    elif s.model == 'FITZHUGH_NAGUMO':
        rd_core.evolve_fitzhugh_nagumo_3d(
            u, v,
            s.size_3d,
            steps_now,
            s.Du,
            s.Dv,
            s.fh_a,
            s.fh_b,
            s.fh_eps,
            s.dt,
        )
        return
