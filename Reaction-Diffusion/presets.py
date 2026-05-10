# Parameter preset application functions.


def apply_gray_scott_2d_preset(s):
    if s.gray_scott_2d_preset == 'CUSTOM':
        return

    presets = {
        'DOTS':         (128, 20, 10000, 0.16, 0.08, 0.035, 0.065, "U"),
        'WORMS':        (256, 8, 10000, 0.16, 0.08, 0.022, 0.051, "U"),
        'MAZE':         (256, 8, 5000, 0.16, 0.08, 0.029, 0.057, "U"),
        'CORAL':        (256, 8, 15000, 0.16, 0.08, 0.060, 0.062, "U"),
        'FINGERPRINT':  (256, 8, 5000, 0.16, 0.08, 0.026, 0.055, "U"),
        'SYMETRIC':     (128, 20, 5000, 0.09, 0.04, 0.045, 0.06, "U"),
        'WAVES':        (256, 8, 10000, 0.16, 0.08, 0.018, 0.045, "U"),
    }

    s.size, s.perturb_2d, s.steps, s.Du, s.Dv, s.F, s.k, s.field_mode = presets[s.gray_scott_2d_preset]


def apply_gray_scott_3d_preset(s):
    if s.gray_scott_3d_preset == 'CUSTOM':
        return

    presets = {
        'TUBES':    (64, 8, 2500, 0.12, 0.05, 0.025, 0.06, 0.3, "V"), 
        'CUBE':     (64, 8, 5000, 0.09, 0.04, 0.045, 0.06, 0.38, "U"),
        'SYMETRIC': (64, 8, 1000, 0.12, 0.05, 0.025, 0.06, 0.3, "V"),
    }

    s.size_3d, s.perturb_3d, s.steps, s.Du, s.Dv, s.F, s.k, s.iso_level, s.field_mode = presets[s.gray_scott_3d_preset]


def apply_brusselator_2d_preset(s):
    if s.brusselator_2d_preset == 'CUSTOM':
        return

    presets = {
        'WAVES':            (256, 20, 20000, 0.02, 0.1, 1.0, 2.2, 0.005, 0.03, "U"),
        'DENSE_SPIRALS' :   (256, 20, 30000, 0.18, 0.07, 1.0, 3.0, 0.005, 0.03, "U"),
        'SMALL_SPIRALS':    (256, 20, 30000, 0.18, 0.07, 1.0, 3.0, 0.01, 0.0001, "U"),
        'DENSE_SPIKES':     (256, 15, 20000, 0.005, 0.05, 1.0, 2.4, 0.005, 0.08, "U"),
        'SOFT_WAVES':       (256, 15, 20000, 0.03, 0.12, 1.0, 2.05, 0.006, 0.02, "U"),
    }

    s.size, s.perturb_2d, s.steps, s.Du, s.Dv, s.A, s.B, s.dt, s.noise, s.field_mode = presets[s.brusselator_2d_preset]


def apply_brusselator_3d_preset(s):
    if s.brusselator_3d_preset == 'CUSTOM':
        return

    presets = {
        'CORAL':   (32, 8, 9000, 0.002, 0.05, 1.0, 1.7, 0.005, 0.03, 0.45, "U"),
        'MINERAL' :   (32, 20, 9000, 0.004, 0.16, 1.0, 1.92, 0.0008, 0.0001, 0.5, "U"),
        'SPIRAL'  :   (64, 8, 50000, 0.18, 0.07, 1.0, 3.0, 0.01, 0.0001, 0.3, "U"),
    }

    s.size_3d, s.perturb_3d, s.steps, s.Du, s.Dv, s.A, s.B, s.dt, s.noise, s.iso_level, s.field_mode = presets[s.brusselator_3d_preset]


def apply_fhn_2d_preset(s):
    if s.fh_2d_preset == 'CUSTOM':
        return

    presets = {
        'PATTERNS': (256, 800, 1.0, 0.05, 0.15, 0.45, 0.08, 0.01, 0.03, 2.0, 8, 'CENTER', "U"),
        'WAVE':     (256, 6000, 0.30, 0.00, 0.70, 0.80, 0.090, 0.035, 0.000, 2.4, 14, 'CENTER', "U"),
    }

    s.size, s.steps, s.Du, s.Dv, s.fh_a, s.fh_b, s.fh_eps, s.dt, s.noise, s.fh_strength, s.perturb_2d, s.fh_init_mode, s.field_mode = presets[s.fh_2d_preset]


def apply_fhn_3d_preset(s):
    if s.fh_3d_preset == 'CUSTOM':
        return

    presets = {
        'VASE':   (64, 20000, 1.0, 0.05, 0.15, 0.45, 0.08, 0.01, 0.03, 2.0, 6, 6, 0.4, "U"),
        'CUBE':   (64, 850, 0.3, 0, 0.7, 0.8, 0.1, 0.16, 0, 2.4, 6, 1, 0.45, "U"),
        'SPLASH': (64, 1000, 1.0, 0.05, 0.15, 0.45, 0.08, 0.01, 0.03, 2.0, 6, 6, 0.4, "U"),
    }

    s.size_3d, s.steps, s.Du, s.Dv, s.fh_a, s.fh_b, s.fh_eps, s.dt, s.noise, s.fh_strength, s.perturb_3d, s.fh_num_sparks, s.iso_level, s.field_mode = presets[s.fh_3d_preset]
