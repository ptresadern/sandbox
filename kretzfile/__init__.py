"""
Kretzfile module for reading volumetric ultrasound data.

This module provides functionality to load and access binary kretzfile format data
used by GE/Kretztechnik 3D ultrasound systems.
"""

from .kretzfile import KretzFileLoader

__version__ = "0.1.0"
__all__ = ["KretzFileLoader"]
