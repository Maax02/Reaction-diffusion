# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
from cython.parallel import prange
from libc.stdlib cimport malloc, free

cdef inline double clamp01(double x) nogil:
    if x < 0.0:
        return 0.0
    elif x > 1.0:
        return 1.0
    return x

def evolve_gray_scott(double[:] u, double[:] v,
                      int size, int steps,
                      double Du, double Dv, double F, double k,
                      bint do_clamp=True):
    
    cdef Py_ssize_t n = size * size
    if u.shape[0] != n or v.shape[0] != n:
        raise ValueError("u/v must have length size*size")

    cdef double* u2 = <double*> malloc(n * sizeof(double))
    cdef double* v2 = <double*> malloc(n * sizeof(double))
    if u2 == NULL or v2 == NULL:
        if u2 != NULL: free(u2)
        if v2 != NULL: free(v2)
        raise MemoryError()

    cdef int step, x, y
    cdef int xm, xp, ym, yp
    cdef Py_ssize_t c, up, um, rp, rm
    cdef double uu, vv, lapu, lapv, uvv, new_u, new_v

    try:
        for step in range(steps):
            # paralelizuj po riadkoch
            for y in prange(size, nogil=True, schedule='static'):
                ym = y - 1
                if ym < 0: ym = size - 1
                yp = y + 1
                if yp >= size: yp = 0

                for x in range(size):
                    xm = x - 1
                    if xm < 0: xm = size - 1
                    xp = x + 1
                    if xp >= size: xp = 0

                    c  = y * size + x
                    up = yp * size + x
                    um = ym * size + x
                    rp = y * size + xp
                    rm = y * size + xm

                    uu = u[c]
                    vv = v[c]

                    # 4-neighborhood laplacian
                    lapu = (u[um] + u[up] + u[rm] + u[rp] - 4.0 * uu)
                    lapv = (v[um] + v[up] + v[rm] + v[rp] - 4.0 * vv)

                    uvv = uu * vv * vv

                    new_u = uu + Du * lapu - uvv + F * (1.0 - uu)
                    new_v = vv + Dv * lapv + uvv - (F + k) * vv

                    if do_clamp:
                        new_u = clamp01(new_u)
                        new_v = clamp01(new_v)

                    u2[c] = new_u
                    v2[c] = new_v

            for c in prange(n, nogil=True, schedule='static'):
                u[c] = u2[c]
                v[c] = v2[c]

    finally:
        free(u2)
        free(v2)

    return None


def evolve_gray_scott_3d(double[:] u, double[:] v,
                         int size, int steps,
                         double Du, double Dv, double F, double k,
                         bint do_clamp=True):

    cdef Py_ssize_t size2 = size * size
    cdef Py_ssize_t n = size2 * size
    if u.shape[0] != n or v.shape[0] != n:
        raise ValueError("u/v must have length size*size*size")

    cdef double* u2 = <double*> malloc(n * sizeof(double))
    cdef double* v2 = <double*> malloc(n * sizeof(double))
    if u2 == NULL or v2 == NULL:
        if u2 != NULL:
            free(u2)
        if v2 != NULL:
            free(v2)
        raise MemoryError()

    cdef int step, x, y, z
    cdef int xm, xp, ym, yp, zm, zp
    cdef Py_ssize_t c, xl, xr, yd, yu, zb, zf
    cdef Py_ssize_t zoff, zmoff, zpoff, yoff, ymoff, ypoff
    cdef double uu, vv, lapu, lapv, uvv, new_u, new_v

    try:
        for step in range(steps):
            # parallelize over z-slices
            for z in prange(size, nogil=True, schedule='static'):
                zm = z - 1
                if zm < 0:
                    zm = size - 1
                zp = z + 1
                if zp >= size:
                    zp = 0

                zoff = z * size2
                zmoff = zm * size2
                zpoff = zp * size2

                for y in range(size):
                    ym = y - 1
                    if ym < 0:
                        ym = size - 1
                    yp = y + 1
                    if yp >= size:
                        yp = 0

                    yoff = zoff + y * size
                    ymoff = zoff + ym * size
                    ypoff = zoff + yp * size

                    for x in range(size):
                        xm = x - 1
                        if xm < 0:
                            xm = size - 1
                        xp = x + 1
                        if xp >= size:
                            xp = 0

                        c  = yoff + x
                        xl = yoff + xm
                        xr = yoff + xp
                        yd = ymoff + x
                        yu = ypoff + x
                        zb = zmoff + y * size + x
                        zf = zpoff + y * size + x

                        uu = u[c]
                        vv = v[c]

                        # 6-neighborhood Laplacian
                        lapu = (u[xl] + u[xr] + u[yd] + u[yu] + u[zb] + u[zf] - 6.0 * uu)
                        lapv = (v[xl] + v[xr] + v[yd] + v[yu] + v[zb] + v[zf] - 6.0 * vv)

                        uvv = uu * vv * vv

                        new_u = uu + Du * lapu - uvv + F * (1.0 - uu)
                        new_v = vv + Dv * lapv + uvv - (F + k) * vv

                        if do_clamp:
                            new_u = clamp01(new_u)
                            new_v = clamp01(new_v)

                        u2[c] = new_u
                        v2[c] = new_v

            for c in prange(n, nogil=True, schedule='static'):
                u[c] = u2[c]
                v[c] = v2[c]

    finally:
        free(u2)
        free(v2)

    return None


def evolve_brusselator(double[:] u, double[:] v,
                       int size, int steps,
                       double Du, double Dv,
                       double A, double B, double dt):

    cdef Py_ssize_t n = size * size
    if u.shape[0] != n or v.shape[0] != n:
        raise ValueError("u/v must have length size*size")

    cdef double* u2 = <double*> malloc(n * sizeof(double))
    cdef double* v2 = <double*> malloc(n * sizeof(double))
    if u2 == NULL or v2 == NULL:
        if u2 != NULL:
            free(u2)
        if v2 != NULL:
            free(v2)
        raise MemoryError()

    cdef int step, x, y
    cdef int xm, xp, ym, yp
    cdef Py_ssize_t c, up, um, rp, rm
    cdef double uu, vv, lapu, lapv, reaction_uv, dU, dV

    try:
        for step in range(steps):
            for y in prange(size, nogil=True, schedule='static'):
                ym = y - 1
                if ym < 0:
                    ym = size - 1
                yp = y + 1
                if yp >= size:
                    yp = 0

                for x in range(size):
                    xm = x - 1
                    if xm < 0:
                        xm = size - 1
                    xp = x + 1
                    if xp >= size:
                        xp = 0

                    c  = y * size + x
                    up = yp * size + x
                    um = ym * size + x
                    rp = y * size + xp
                    rm = y * size + xm

                    uu = u[c]
                    vv = v[c]

                    # 4-neighborhood Laplacian
                    lapu = (u[um] + u[up] + u[rm] + u[rp] - 4.0 * uu)
                    lapv = (v[um] + v[up] + v[rm] + v[rp] - 4.0 * vv)

                    # Brusselator reaction terms
                    reaction_uv = uu * uu * vv

                    dU = A - (B + 1.0) * uu + reaction_uv + Du * lapu
                    dV = B * uu - reaction_uv + Dv * lapv

                    u2[c] = uu + dt * dU
                    v2[c] = vv + dt * dV

            for c in prange(n, nogil=True, schedule='static'):
                u[c] = u2[c]
                v[c] = v2[c]

    finally:
        free(u2)
        free(v2)

    return None


def evolve_brusselator_3d(double[:] u, double[:] v,
                          int size, int steps,
                          double Du, double Dv,
                          double A, double B, double dt):

    cdef Py_ssize_t size2 = size * size
    cdef Py_ssize_t n = size2 * size

    if u.shape[0] != n or v.shape[0] != n:
        raise ValueError("u/v must have length size*size*size")

    cdef double* u2 = <double*> malloc(n * sizeof(double))
    cdef double* v2 = <double*> malloc(n * sizeof(double))

    if u2 == NULL or v2 == NULL:
        if u2 != NULL:
            free(u2)
        if v2 != NULL:
            free(v2)
        raise MemoryError()

    cdef int step, x, y, z
    cdef int xm, xp, ym, yp, zm, zp
    cdef Py_ssize_t c, xl, xr, yd, yu, zb, zf
    cdef Py_ssize_t zoff, zmoff, zpoff, yoff, ymoff, ypoff
    cdef double uu, vv, lapu, lapv
    cdef double reaction_uv, dU, dV

    try:
        for step in range(steps):
            for z in prange(size, nogil=True, schedule='static'):
                zm = z - 1
                if zm < 0:
                    zm = size - 1

                zp = z + 1
                if zp >= size:
                    zp = 0

                zoff = z * size2
                zmoff = zm * size2
                zpoff = zp * size2

                for y in range(size):
                    ym = y - 1
                    if ym < 0:
                        ym = size - 1

                    yp = y + 1
                    if yp >= size:
                        yp = 0

                    yoff = zoff + y * size
                    ymoff = zoff + ym * size
                    ypoff = zoff + yp * size

                    for x in range(size):
                        xm = x - 1
                        if xm < 0:
                            xm = size - 1

                        xp = x + 1
                        if xp >= size:
                            xp = 0

                        c  = yoff + x
                        xl = yoff + xm
                        xr = yoff + xp
                        yd = ymoff + x
                        yu = ypoff + x
                        zb = zmoff + y * size + x
                        zf = zpoff + y * size + x

                        uu = u[c]
                        vv = v[c]

                        lapu = (
                            u[xl] + u[xr] +
                            u[yd] + u[yu] +
                            u[zb] + u[zf] -
                            6.0 * uu
                        )

                        lapv = (
                            v[xl] + v[xr] +
                            v[yd] + v[yu] +
                            v[zb] + v[zf] -
                            6.0 * vv
                        )

                        reaction_uv = uu * uu * vv

                        dU = A - (B + 1.0) * uu + reaction_uv + Du * lapu
                        dV = B * uu - reaction_uv + Dv * lapv

                        u2[c] = uu + dt * dU
                        v2[c] = vv + dt * dV

            for c in prange(n, nogil=True, schedule='static'):
                u[c] = u2[c]
                v[c] = v2[c]

    finally:
        free(u2)
        free(v2)

    return None



def evolve_fitzhugh_nagumo(double[:] u, double[:] v,
                           int size, int steps,
                           double Du, double Dv,
                           double a, double b, double eps, double dt):

    cdef Py_ssize_t n = size * size
    if u.shape[0] != n or v.shape[0] != n:
        raise ValueError("u/v must have length size*size")

    cdef double* u2 = <double*> malloc(n * sizeof(double))
    cdef double* v2 = <double*> malloc(n * sizeof(double))

    if u2 == NULL or v2 == NULL:
        if u2 != NULL:
            free(u2)
        if v2 != NULL:
            free(v2)
        raise MemoryError()

    cdef int step, x, y
    cdef int xm, xp, ym, yp
    cdef Py_ssize_t c, up, um, rp, rm
    cdef double uu, vv, lapu, lapv, du_dt, dv_dt

    try:
        for step in range(steps):
            for y in prange(size, nogil=True, schedule='static'):
                ym = y - 1
                if ym < 0:
                    ym = size - 1

                yp = y + 1
                if yp >= size:
                    yp = 0

                for x in range(size):
                    xm = x - 1
                    if xm < 0:
                        xm = size - 1

                    xp = x + 1
                    if xp >= size:
                        xp = 0

                    c  = y * size + x
                    up = yp * size + x
                    um = ym * size + x
                    rp = y * size + xp
                    rm = y * size + xm

                    uu = u[c]
                    vv = v[c]

                    lapu = u[um] + u[up] + u[rm] + u[rp] - 4.0 * uu
                    lapv = v[um] + v[up] + v[rm] + v[rp] - 4.0 * vv

                    du_dt = uu - (uu * uu * uu) / 3.0 - vv + Du * lapu
                    dv_dt = eps * (uu + a - b * vv) + Dv * lapv

                    u2[c] = uu + dt * du_dt
                    v2[c] = vv + dt * dv_dt

            for c in prange(n, nogil=True, schedule='static'):
                u[c] = u2[c]
                v[c] = v2[c]

    finally:
        free(u2)
        free(v2)

    return None


def evolve_fitzhugh_nagumo_3d(double[:] u, double[:] v,
                              int size, int steps,
                              double Du, double Dv,
                              double a, double b,
                              double eps, double dt):

    cdef Py_ssize_t size2 = size * size
    cdef Py_ssize_t n = size2 * size

    if u.shape[0] != n or v.shape[0] != n:
        raise ValueError("u/v must have length size*size*size")

    cdef double* u2 = <double*> malloc(n * sizeof(double))
    cdef double* v2 = <double*> malloc(n * sizeof(double))

    if u2 == NULL or v2 == NULL:
        if u2 != NULL:
            free(u2)
        if v2 != NULL:
            free(v2)
        raise MemoryError()

    cdef int step, x, y, z
    cdef int xm, xp, ym, yp, zm, zp
    cdef Py_ssize_t c, xl, xr, yd, yu, zb, zf
    cdef Py_ssize_t zoff, zmoff, zpoff, yoff, ymoff, ypoff
    cdef double uu, vv, lapu, lapv, du_dt, dv_dt

    try:
        for step in range(steps):
            for z in prange(size, nogil=True, schedule='static'):
                zm = z - 1
                if zm < 0:
                    zm = size - 1

                zp = z + 1
                if zp >= size:
                    zp = 0

                zoff = z * size2
                zmoff = zm * size2
                zpoff = zp * size2

                for y in range(size):
                    ym = y - 1
                    if ym < 0:
                        ym = size - 1

                    yp = y + 1
                    if yp >= size:
                        yp = 0

                    yoff = zoff + y * size
                    ymoff = zoff + ym * size
                    ypoff = zoff + yp * size

                    for x in range(size):
                        xm = x - 1
                        if xm < 0:
                            xm = size - 1

                        xp = x + 1
                        if xp >= size:
                            xp = 0

                        c  = yoff + x
                        xl = yoff + xm
                        xr = yoff + xp
                        yd = ymoff + x
                        yu = ypoff + x
                        zb = zmoff + y * size + x
                        zf = zpoff + y * size + x

                        uu = u[c]
                        vv = v[c]

                        lapu = (
                            u[xl] + u[xr] +
                            u[yd] + u[yu] +
                            u[zb] + u[zf] -
                            6.0 * uu
                        )

                        lapv = (
                            v[xl] + v[xr] +
                            v[yd] + v[yu] +
                            v[zb] + v[zf] -
                            6.0 * vv
                        )

                        du_dt = uu - (uu * uu * uu) / 3.0 - vv + Du * lapu
                        dv_dt = eps * (uu + a - b * vv) + Dv * lapv

                        u2[c] = uu + dt * du_dt
                        v2[c] = vv + dt * dv_dt

            for c in prange(n, nogil=True, schedule='static'):
                u[c] = u2[c]
                v[c] = v2[c]

    finally:
        free(u2)
        free(v2)

    return None