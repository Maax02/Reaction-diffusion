# Reaction-Diffusion Blender Add-on

A Blender add-on for generating two-dimensional and three-dimensional procedural structures using reaction-diffusion systems.

The project was developed as part of a master's thesis focused on procedural geometry generation using reaction-diffusion models inside Blender.

---

# Features

- Multiple reaction-diffusion models
  - Gray–Scott
  - Brusselator
  - FitzHugh–Nagumo
- Two-dimensional and three-dimensional simulations
- Real-time preview workflow
- Marching Cubes isosurface extraction
- Cython-accelerated simulation core
- OpenMP parallelization
- Blender-integrated user interface
- Procedural mesh generation directly inside Blender

---

# Installation

## 1. Download the add-on

Clone the repository or download it as a ZIP archive.

## 2. Install in Blender

Open Blender:

```text
Edit → Preferences → Add-ons → Install
```

Select the ZIP archive or the add-on folder.

Enable the add-on after installation.

---

# Dependencies

The add-on uses external Python libraries:

- NumPy
- scikit-image

Dependencies can be installed directly from the add-on interface using the included dependency installer.

The compiled Cython module must be included in the `cython/` folder.

---

# Usage

After enabling the add-on:

1. Open the **RD** panel in the 3D View sidebar
2. Select:
   - simulation mode (2D or 3D)
   - reaction-diffusion model
3. Configure:
   - grid resolution
   - iteration count
   - model parameters
4. Generate preview
5. Generate final mesh

---

# Implemented Models

## Gray–Scott

Produces:
- spots
- worms
- labyrinths
- symmetric structures
- volumetric tunnels

## Brusselator

Produces:
- spirals
- oscillatory waves
- chaotic volumetric structures

## FitzHugh–Nagumo

Produces:
- wavefronts
- pulse propagation
- excitable patterns
- volumetric wave structures

---

# Performance

The simulation core is accelerated using Cython and OpenMP.

---

# Notes

The current version was primarily developed and tested on Windows.

Linux and macOS require recompilation of the Cython extension module for the target platform and Blender Python version.
