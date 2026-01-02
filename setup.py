"""Setup script for pysha-sdk with Cython extensions."""

from pathlib import Path

from Cython.Build import cythonize
from setuptools import Extension, find_packages, setup

# Find all .pyx files
source_dir = Path("src")
pyx_files = list(source_dir.rglob("*.pyx"))

# Create Extension objects for each .pyx file
extensions = []
for pyx_file in pyx_files:
    # Convert path like src/pysha_sdk/utils/strings/_native.pyx
    # to pysha_sdk.utils.strings._native
    # Use parts to handle both Windows and Unix paths correctly
    rel_path = pyx_file.relative_to(source_dir)
    module_name = ".".join(rel_path.with_suffix("").parts)
    extensions.append(Extension(module_name, [str(pyx_file)]))

# Cythonize the extensions
if extensions:
    cythonized_extensions = cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
        },
        build_dir="build",
    )
else:
    cythonized_extensions = []

setup(
    ext_modules=cythonized_extensions,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
