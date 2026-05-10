from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    name="rd_core",
    sources=["rd_core.pyx"],
    extra_compile_args=["/O2", "/openmp"],
)

setup(
    name="rd_core",
    ext_modules=cythonize([ext], language_level="3"),
)
