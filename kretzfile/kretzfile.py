"""
Kretzfile loader for reading binary volumetric ultrasound data.

The Kretzfile format is used by GE/Kretztechnik 3D ultrasound systems to store
volumetric ultrasound data with metadata about dimensions, spacing, and coordinate
system information.
"""

import struct
import numpy as np
from typing import Tuple, Dict, Any, Optional
from pathlib import Path


class KretzFileLoader:
    """
    Loader for binary Kretzfile format used in GE 3D ultrasound systems.

    The Kretzfile format stores 3D volumetric ultrasound data with toroidal
    coordinate system geometry. This class reads the binary format and provides
    access to the metadata and volumetric data.

    Attributes:
        metadata: Dictionary containing file metadata
        volume: 3D numpy array of volumetric ultrasound data
    """

    # Kretzfile magic string and version
    MAGIC_STRING = b"KRETZFILE"

    # Standard header size for basic kretzfile
    HEADER_SIZE = 256

    def __init__(self, filepath: str):
        """
        Initialize KretzFileLoader and load data from file.

        Args:
            filepath: Path to the kretzfile binary file

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid Kretzfile format
        """
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        self.metadata: Dict[str, Any] = {}
        self.volume: Optional[np.ndarray] = None

        self._load_file()

    def _load_file(self) -> None:
        """Load and parse the kretzfile binary data."""
        with open(self.filepath, "rb") as f:
            # Read and validate magic string
            magic = f.read(9)
            if magic != self.MAGIC_STRING:
                raise ValueError(
                    f"Invalid Kretzfile format. Expected magic string "
                    f"'{self.MAGIC_STRING.decode()}', got '{magic.decode(errors='ignore')}'"
                )

            # Read version
            version_bytes = f.read(3)
            version = version_bytes.decode('ascii')
            self.metadata['version'] = version

            # Read null terminator (space)
            f.read(1)

            # Read extended header with metadata
            self._parse_header(f)

            # Read volumetric data
            self._parse_volume_data(f)

    def _parse_header(self, f) -> None:
        """Parse the Kretzfile header containing metadata."""
        # Read frame count (4 bytes, little-endian uint32)
        f.seek(16)
        frame_data = f.read(4)
        self.metadata['frame_count'] = struct.unpack('<I', frame_data)[0]

        # Read voxel dimensions (12 bytes: 3 x uint32)
        f.seek(20)
        dims = struct.unpack('<III', f.read(12))
        self.metadata['dimensions'] = {
            'x': dims[0],
            'y': dims[1],
            'z': dims[2]
        }

        # Read voxel spacing (12 bytes: 3 x float32)
        f.seek(32)
        spacing = struct.unpack('<fff', f.read(12))
        self.metadata['spacing'] = {
            'x': spacing[0],
            'y': spacing[1],
            'z': spacing[2]
        }

        # Read coordinate system type (1 byte)
        f.seek(44)
        coord_type = struct.unpack('<B', f.read(1))[0]
        coord_systems = {
            0: 'cartesian',
            1: 'toroidal',
            2: 'spherical',
            3: 'cylindrical'
        }
        self.metadata['coordinate_system'] = coord_systems.get(
            coord_type, f'unknown_{coord_type}'
        )

        # Read image data type (1 byte)
        f.seek(45)
        data_type = struct.unpack('<B', f.read(1))[0]
        data_types = {
            0: 'uint8',
            1: 'uint16',
            2: 'uint32',
            3: 'int8',
            4: 'int16',
            5: 'int32',
            6: 'float32',
            7: 'float64'
        }
        self.metadata['data_type'] = data_types.get(data_type, f'unknown_{data_type}')

        # Read compression flag (1 byte)
        f.seek(46)
        compression = struct.unpack('<B', f.read(1))[0]
        self.metadata['compressed'] = bool(compression)

        # Read patient name (64 bytes, null-terminated string)
        f.seek(48)
        patient_name = f.read(64)
        self.metadata['patient_name'] = patient_name.rstrip(b'\x00').decode(
            'utf-8', errors='replace'
        )

        # Read study date (16 bytes)
        f.seek(112)
        study_date = f.read(16)
        self.metadata['study_date'] = study_date.rstrip(b'\x00').decode(
            'utf-8', errors='replace'
        )

        # Read study time (16 bytes)
        f.seek(128)
        study_time = f.read(16)
        self.metadata['study_time'] = study_time.rstrip(b'\x00').decode(
            'utf-8', errors='replace'
        )

        # Read acquisition mode (32 bytes)
        f.seek(144)
        acq_mode = f.read(32)
        self.metadata['acquisition_mode'] = acq_mode.rstrip(b'\x00').decode(
            'utf-8', errors='replace'
        )

        # Read system name (32 bytes)
        f.seek(176)
        system_name = f.read(32)
        self.metadata['system_name'] = system_name.rstrip(b'\x00').decode(
            'utf-8', errors='replace'
        )

        # Read probe name (32 bytes)
        f.seek(208)
        probe_name = f.read(32)
        self.metadata['probe_name'] = probe_name.rstrip(b'\x00').decode(
            'utf-8', errors='replace'
        )

        # Read additional parameters
        f.seek(240)
        origin = struct.unpack('<fff', f.read(12))
        self.metadata['origin'] = {
            'x': origin[0],
            'y': origin[1],
            'z': origin[2]
        }

    def _parse_volume_data(self, f) -> None:
        """Parse the volumetric data from the file."""
        dims = self.metadata['dimensions']
        num_voxels = dims['x'] * dims['y'] * dims['z']

        # Map data type strings to numpy dtypes
        dtype_map = {
            'uint8': np.uint8,
            'uint16': np.uint16,
            'uint32': np.uint32,
            'int8': np.int8,
            'int16': np.int16,
            'int32': np.int32,
            'float32': np.float32,
            'float64': np.float64
        }

        data_type_str = self.metadata['data_type']
        dtype = dtype_map.get(data_type_str, np.uint8)

        # Seek to volume data (after header)
        f.seek(self.HEADER_SIZE)

        # Read volume data
        if self.metadata.get('compressed'):
            # For compressed data, read all remaining bytes and decompress
            compressed_data = f.read()
            if len(compressed_data) > 0:
                # Simple RLE decompression for basic compression
                volume_data = self._decompress_rle(compressed_data, dtype, num_voxels)
            else:
                # No data available, create empty volume
                volume_data = np.array([], dtype=dtype)
        else:
            # Read uncompressed data
            voxel_size = dtype(0).itemsize
            volume_bytes = f.read(num_voxels * voxel_size)
            volume_data = np.frombuffer(volume_bytes, dtype=dtype)

        # Reshape to 3D array (X, Y, Z) if data is available
        if len(volume_data) == num_voxels:
            self.volume = volume_data.reshape(
                (dims['x'], dims['y'], dims['z']), order='C'
            )
        else:
            # Data size mismatch, create empty volume or warn
            self.metadata['volume_data_missing'] = True
            self.volume = np.zeros((dims['x'], dims['y'], dims['z']), dtype=dtype)

    @staticmethod
    def _decompress_rle(data: bytes, dtype: np.dtype, num_voxels: int) -> np.ndarray:
        """
        Decompress RLE (Run-Length Encoding) compressed data.

        Simple RLE format: [count, value] pairs

        Args:
            data: Compressed byte data
            dtype: Data type of individual voxels
            num_voxels: Expected number of voxels

        Returns:
            1D numpy array of decompressed voxel data
        """
        result = []
        i = 0
        voxel_size = dtype(0).itemsize

        while i < len(data) and len(result) < num_voxels:
            # Read count (1 byte)
            count = data[i]
            i += 1

            if count == 0:
                break

            # Read value
            value_bytes = data[i:i + voxel_size]
            if len(value_bytes) < voxel_size:
                break

            value = np.frombuffer(value_bytes, dtype=dtype)[0]
            result.extend([value] * count)
            i += voxel_size

        return np.array(result, dtype=dtype)

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get all metadata from the kretzfile.

        Returns:
            Dictionary containing all parsed metadata
        """
        return self.metadata.copy()

    def get_volume(self) -> np.ndarray:
        """
        Get the 3D volumetric ultrasound data.

        Returns:
            3D numpy array with shape (X, Y, Z) containing voxel intensities
        """
        if self.volume is None:
            raise RuntimeError("Volume data not loaded")
        return self.volume.copy()

    def get_dimension(self) -> Tuple[int, int, int]:
        """
        Get the dimensions of the volume.

        Returns:
            Tuple of (x, y, z) dimensions
        """
        dims = self.metadata['dimensions']
        return (dims['x'], dims['y'], dims['z'])

    def get_spacing(self) -> Tuple[float, float, float]:
        """
        Get the voxel spacing of the volume.

        Returns:
            Tuple of (x, y, z) spacing in mm
        """
        spacing = self.metadata['spacing']
        return (spacing['x'], spacing['y'], spacing['z'])

    def get_coordinate_system(self) -> str:
        """
        Get the coordinate system used in the file.

        Returns:
            String describing the coordinate system (cartesian, toroidal, etc.)
        """
        return self.metadata.get('coordinate_system', 'unknown')

    def get_patient_info(self) -> Dict[str, str]:
        """
        Get patient and study information.

        Returns:
            Dictionary containing patient_name, study_date, and study_time
        """
        return {
            'patient_name': self.metadata.get('patient_name', ''),
            'study_date': self.metadata.get('study_date', ''),
            'study_time': self.metadata.get('study_time', '')
        }

    def get_system_info(self) -> Dict[str, str]:
        """
        Get ultrasound system information.

        Returns:
            Dictionary containing system_name and probe_name
        """
        return {
            'system_name': self.metadata.get('system_name', ''),
            'probe_name': self.metadata.get('probe_name', '')
        }

    def __repr__(self) -> str:
        """Return string representation of the kretzfile loader."""
        dims = self.get_dimension()
        return (
            f"KretzFileLoader(file='{self.filepath.name}', "
            f"dimensions={dims}, "
            f"coordinate_system='{self.get_coordinate_system()}')"
        )
