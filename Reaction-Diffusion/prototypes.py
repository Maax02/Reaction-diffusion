def simulate_gray_scott(size, steps, Du, Dv, F, k, seed=42, perturb=20, do_clamp=True):
    """
    Python 2D prototype
    """
    u = [1.0] * (size * size)
    v = [0.0] * (size * size)

    random.seed(seed)
    half = perturb // 2
    cx = size // 2
    cy = size // 2

    for y in range(cy - half, cy + half):
        for x in range(cx - half, cx + half):
            if 0 <= x < size and 0 <= y < size:
                v[idx(x, y, size)] = random.random()

    for _ in range(steps):
        lap_u = [0.0] * (size * size)
        lap_v = [0.0] * (size * size)

        for y in range(size):
            ym = (y - 1) % size
            yp = (y + 1) % size
            row = y * size
            for x in range(size):
                xm = (x - 1) % size
                xp = (x + 1) % size

                c = row + x
                up = yp * size + x
                um = ym * size + x
                rp = row + xp
                rm = row + xm

                lap_u[c] = (u[um] + u[up] + u[rm] + u[rp] - 4.0 * u[c])
                lap_v[c] = (v[um] + v[up] + v[rm] + v[rp] - 4.0 * v[c])

        for i in range(size * size):
            uu = u[i]
            vv = v[i]
            uvv = uu * vv * vv

            uu = uu + Du * lap_u[i] - uvv + F * (1.0 - uu)
            vv = vv + Dv * lap_v[i] + uvv - (F + k) * vv

            if do_clamp:
                uu = clamp01(uu)
                vv = clamp01(vv)

            u[i] = uu
            v[i] = vv

    return u, v


def simulate_brusselator(size, steps, Du, Dv, A, B, dt=0.01, seed=42, noise=0.03, perturb=20):
    """
    Python 2D Brusselator prototype.
    Periodic boundaries, explicit Euler.
    """
    u, v = init_brusselator_state(
        size,
        A=A,
        B=B,
        seed=seed,
        noise=noise,
        perturb=perturb,
    )

    n = size * size

    for _ in range(steps):
        u2 = array('d', [0.0]) * n
        v2 = array('d', [0.0]) * n

        for y in range(size):
            ym = (y - 1) % size
            yp = (y + 1) % size
            row = y * size
            row_m = ym * size
            row_p = yp * size

            for x in range(size):
                xm = (x - 1) % size
                xp = (x + 1) % size

                c = row + x
                xl = row + xm
                xr = row + xp
                yd = row_m + x
                yu = row_p + x

                U = u[c]
                V = v[c]

                lap_u = u[xl] + u[xr] + u[yd] + u[yu] - 4.0 * U
                lap_v = v[xl] + v[xr] + v[yd] + v[yu] - 4.0 * V

                reaction_uv = U * U * V

                dU = A - (B + 1.0) * U + reaction_uv + Du * lap_u
                dV = B * U - reaction_uv + Dv * lap_v

                u2[c] = U + dt * dU
                v2[c] = V + dt * dV

        u = u2
        v = v2

    return u, v


def simulate_gray_scott_3d(size, steps, Du, Dv, F, k, seed=42, perturb=8, do_clamp=True):
    """
    Python 3D prototype
    """
    u, v = init_gray_scott_state_3d(size, seed=seed, perturb=perturb)
    n = size * size * size

    for _ in range(steps):
        u2 = array('d', [0.0]) * n
        v2 = array('d', [0.0]) * n

        for z in range(size):
            zm = (z - 1) % size
            zp = (z + 1) % size
            for y in range(size):
                ym = (y - 1) % size
                yp = (y + 1) % size
                for x in range(size):
                    xm = (x - 1) % size
                    xp = (x + 1) % size

                    c = idx3(x, y, z, size)
                    xl = idx3(xm, y, z, size)
                    xr = idx3(xp, y, z, size)
                    yd = idx3(x, ym, z, size)
                    yu = idx3(x, yp, z, size)
                    zb = idx3(x, y, zm, size)
                    zf = idx3(x, y, zp, size)

                    uu = u[c]
                    vv = v[c]

                    lapu = u[xl] + u[xr] + u[yd] + u[yu] + u[zb] + u[zf] - 6.0 * uu
                    lapv = v[xl] + v[xr] + v[yd] + v[yu] + v[zb] + v[zf] - 6.0 * vv

                    uvv = uu * vv * vv

                    new_u = uu + Du * lapu - uvv + F * (1.0 - uu)
                    new_v = vv + Dv * lapv + uvv - (F + k) * vv

                    if do_clamp:
                        new_u = clamp01(new_u)
                        new_v = clamp01(new_v)

                    u2[c] = new_u
                    v2[c] = new_v

        u = u2
        v = v2

    return u, v