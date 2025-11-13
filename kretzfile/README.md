# Kretzfile Module

A Python library for loading and accessing volumetric ultrasound data from binary kretzfile format used by GE Voluson 3D ultrasound systems.

## Overview

The kretzfile format is a proprietary binary format developed by Kretztechnik (now part of GE Healthcare) for storing 3D volumetric ultrasound data. This module provides functionality to:

- Read and parse binary kretzfile format files
- Extract metadata (dimensions, spacing, patient information, system information)
- Access 3D volumetric ultrasound data as numpy arrays
- Support multiple coordinate systems (cartesian, toroidal, spherical, cylindrical)
- Handle various data types (uint8, uint16, uint32, int8, int16, int32, float32, float64)
- Support compressed and uncompressed data

## Installation

### Requirements
- Python 3.7+
- numpy

Install the module:

```bash
pip install numpy
```

## Usage

### Basic Usage

```python
from kretzfile import KretzFileLoader

# Load a kretzfile
loader = KretzFileLoader('path/to/file.vol')

# Access metadata
metadata = loader.get_metadata()
print(f"Dimensions: {loader.get_dimension()}")
print(f"Spacing: {loader.get_spacing()}")
print(f"Coordinate System: {loader.get_coordinate_system()}")

# Access volumetric data
volume = loader.get_volume()
print(f"Volume shape: {volume.shape}")
print(f"Volume dtype: {volume.dtype}")

# Access patient information
patient_info = loader.get_patient_info()
print(f"Patient: {patient_info['patient_name']}")
print(f"Study Date: {patient_info['study_date']}")

# Access system information
system_info = loader.get_system_info()
print(f"System: {system_info['system_name']}")
print(f"Probe: {system_info['probe_name']}")
```

### Working with Volume Data

```python
import numpy as np
from kretzfile import KretzFileLoader

loader = KretzFileLoader('ultrasound_data.vol')
volume = loader.get_volume()

# Get voxel at specific location
voxel_value = volume[10, 20, 30]

# Get a slice
x_slice = volume[50, :, :]
y_slice = volume[:, 50, :]
z_slice = volume[:, :, 50]

# Perform image processing
smoothed = np.convolve(volume.flatten(), kernel='same')

# Access specific metadata
dims = loader.get_dimension()  # (x, y, z)
spacing = loader.get_spacing()  # (x_mm, y_mm, z_mm)

# Get all metadata
full_metadata = loader.get_metadata()
```

## File Format

The kretzfile format consists of:

1. **Magic String** (9 bytes): "KRETZFILE"
2. **Version** (3 bytes): "1.0"
3. **Separator** (1 byte): Space character
4. **Extended Header** (243 bytes):
   - Frame count (4 bytes)
   - Dimensions: X, Y, Z (12 bytes)
   - Voxel spacing: X, Y, Z (12 bytes)
   - Coordinate system type (1 byte)
   - Data type (1 byte)
   - Compression flag (1 byte)
   - Patient name (64 bytes)
   - Study date (16 bytes)
   - Study time (16 bytes)
   - Acquisition mode (32 bytes)
   - System name (32 bytes)
   - Probe name (32 bytes)
   - Origin coordinates (12 bytes)
5. **Volume Data** (variable):
   - Voxel data in specified data type
   - Can be uncompressed or RLE compressed

### Coordinate Systems

- **Cartesian** (0): Standard 3D Cartesian coordinates
- **Toroidal** (1): Toroidal coordinate system used by some ultrasound probes
- **Spherical** (2): Spherical coordinate system
- **Cylindrical** (3): Cylindrical coordinate system

### Data Types

- `uint8`: Unsigned 8-bit integer
- `uint16`: Unsigned 16-bit integer
- `uint32`: Unsigned 32-bit integer
- `int8`: Signed 8-bit integer
- `int16`: Signed 16-bit integer
- `int32`: Signed 32-bit integer
- `float32`: 32-bit floating point
- `float64`: 64-bit floating point

## API Reference

### KretzFileLoader

Main class for loading and accessing kretzfile data.

#### Constructor

```python
KretzFileLoader(filepath: str)
```

**Parameters:**
- `filepath` (str): Path to the kretzfile

**Raises:**
- `FileNotFoundError`: If the file does not exist
- `ValueError`: If the file is not a valid kretzfile format

#### Methods

##### `get_metadata() -> Dict[str, Any]`
Returns a copy of all parsed metadata from the file.

##### `get_volume() -> np.ndarray`
Returns a copy of the 3D volumetric data as a numpy array.

##### `get_dimension() -> Tuple[int, int, int]`
Returns the dimensions of the volume as (x, y, z).

##### `get_spacing() -> Tuple[float, float, float]`
Returns the voxel spacing in millimeters as (x, y, z).

##### `get_coordinate_system() -> str`
Returns the coordinate system type as a string.

##### `get_patient_info() -> Dict[str, str]`
Returns patient information including name, study date, and study time.

##### `get_system_info() -> Dict[str, str]`
Returns system information including system name and probe name.

## Testing

Run the test suite:

```bash
python -m unittest kretzfile.tests -v
```

The module includes 21 comprehensive unit tests covering:
- File loading and validation
- Metadata parsing
- Coordinate system support
- Data type handling
- Volume data integrity
- Error handling
- Integration testing

## Limitations

- The implementation is based on reverse-engineering the kretzfile format from publicly available documentation and open-source implementations
- The RLE decompression is a basic implementation; proprietary compression formats may require additional handling
- Some advanced kretzfile features may not be fully supported

## References

- plooney/kretz: https://github.com/plooney/kretz
- 3D Slicer / SlicerHeart: https://github.com/SlicerHeart
- Research papers on 3D ultrasound file reading and coordinate transformations

## License

This module is provided as-is for research and educational purposes.
