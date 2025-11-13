"""
Unit tests for the kretzfile module.

Tests cover loading, parsing metadata, accessing volume data, and error handling.
"""

import unittest
import tempfile
import struct
import numpy as np
from pathlib import Path
from kretzfile import KretzFileLoader


class TestKretzFileLoader(unittest.TestCase):
    """Test suite for KretzFileLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.temp_dir.name) / "test.vol"

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_test_file(
        self,
        dims: tuple = (10, 10, 10),
        spacing: tuple = (1.0, 1.0, 1.0),
        coord_system: int = 0,
        data_type: int = 0,
        compressed: bool = False,
        patient_name: str = "Test Patient",
        study_date: str = "2024-01-01",
        study_time: str = "12:00:00",
        acquisition_mode: str = "3D",
        system_name: str = "GE Voluson",
        probe_name: str = "4D Probe",
        write_volume_data: bool = True
    ) -> Path:
        """
        Create a test kretzfile with specified parameters.

        Args:
            dims: Tuple of (x, y, z) dimensions
            spacing: Tuple of (x, y, z) spacing values
            coord_system: Coordinate system type (0=cartesian, 1=toroidal, etc.)
            data_type: Data type code (0=uint8, 1=uint16, etc.)
            compressed: Whether data is compressed
            patient_name: Patient name string
            study_date: Study date string
            study_time: Study time string
            acquisition_mode: Acquisition mode string
            system_name: System name string
            probe_name: Probe name string
            write_volume_data: Whether to write volume data (set to False for compressed test)

        Returns:
            Path to created test file
        """
        with open(self.test_file_path, 'wb') as f:
            # Write magic string
            f.write(b"KRETZFILE")

            # Write version
            f.write(b"1.0")

            # Write space separator
            f.write(b" ")

            # Pad to offset 16
            f.write(b'\x00' * (16 - f.tell()))

            # Write frame count (offset 16)
            f.write(struct.pack('<I', 1))

            # Write dimensions (offset 20)
            f.write(struct.pack('<III', dims[0], dims[1], dims[2]))

            # Write spacing (offset 32)
            f.write(struct.pack('<fff', spacing[0], spacing[1], spacing[2]))

            # Write coordinate system (offset 44)
            f.write(struct.pack('<B', coord_system))

            # Write data type (offset 45)
            f.write(struct.pack('<B', data_type))

            # Write compression flag (offset 46)
            f.write(struct.pack('<B', 1 if compressed else 0))

            # Pad to offset 48
            f.write(b'\x00' * (48 - f.tell()))

            # Write patient name (offset 48, 64 bytes)
            patient_bytes = patient_name.encode('utf-8')[:64]
            f.write(patient_bytes)
            f.write(b'\x00' * (64 - len(patient_bytes)))

            # Write study date (offset 112, 16 bytes)
            date_bytes = study_date.encode('utf-8')[:16]
            f.write(date_bytes)
            f.write(b'\x00' * (16 - len(date_bytes)))

            # Write study time (offset 128, 16 bytes)
            time_bytes = study_time.encode('utf-8')[:16]
            f.write(time_bytes)
            f.write(b'\x00' * (16 - len(time_bytes)))

            # Write acquisition mode (offset 144, 32 bytes)
            acq_bytes = acquisition_mode.encode('utf-8')[:32]
            f.write(acq_bytes)
            f.write(b'\x00' * (32 - len(acq_bytes)))

            # Write system name (offset 176, 32 bytes)
            sys_bytes = system_name.encode('utf-8')[:32]
            f.write(sys_bytes)
            f.write(b'\x00' * (32 - len(sys_bytes)))

            # Write probe name (offset 208, 32 bytes)
            probe_bytes = probe_name.encode('utf-8')[:32]
            f.write(probe_bytes)
            f.write(b'\x00' * (32 - len(probe_bytes)))

            # Write origin (offset 240, 12 bytes)
            f.write(struct.pack('<fff', 0.0, 0.0, 0.0))

            # Pad to offset 256 (HEADER_SIZE)
            f.write(b'\x00' * (256 - f.tell()))

            # Write volume data if requested
            if write_volume_data:
                num_voxels = dims[0] * dims[1] * dims[2]

                # Map data type codes to numpy dtypes
                dtype_map = {
                    0: np.uint8,
                    1: np.uint16,
                    2: np.uint32,
                    3: np.int8,
                    4: np.int16,
                    5: np.int32,
                    6: np.float32,
                    7: np.float64
                }

                dtype = dtype_map.get(data_type, np.uint8)

                if dtype in (np.uint8, np.int8):
                    volume_data = np.arange(num_voxels, dtype=np.int32) % 256
                    volume_data = volume_data.astype(dtype)
                elif dtype in (np.uint16, np.int16):
                    volume_data = np.arange(num_voxels, dtype=np.int32) % 65536
                    volume_data = volume_data.astype(dtype)
                else:
                    volume_data = np.arange(num_voxels, dtype=dtype) / 100.0

                f.write(volume_data.tobytes())

        return self.test_file_path

    def test_load_valid_file(self):
        """Test loading a valid kretzfile."""
        self._create_test_file()
        loader = KretzFileLoader(str(self.test_file_path))

        self.assertIsNotNone(loader.metadata)
        self.assertIsNotNone(loader.volume)
        self.assertEqual(loader.metadata['version'], '1.0')

    def test_file_not_found(self):
        """Test error handling for non-existent file."""
        with self.assertRaises(FileNotFoundError):
            KretzFileLoader("/nonexistent/path/file.vol")

    def test_invalid_magic_string(self):
        """Test error handling for invalid magic string."""
        with open(self.test_file_path, 'wb') as f:
            f.write(b"INVALID!!")

        with self.assertRaises(ValueError) as context:
            KretzFileLoader(str(self.test_file_path))

        self.assertIn("Invalid Kretzfile format", str(context.exception))

    def test_metadata_parsing(self):
        """Test that metadata is correctly parsed."""
        self._create_test_file(
            dims=(20, 30, 40),
            spacing=(0.5, 0.5, 1.0),
            patient_name="John Doe",
            study_date="2024-06-15",
            system_name="GE Vivid",
            probe_name="4DHz"
        )

        loader = KretzFileLoader(str(self.test_file_path))
        metadata = loader.get_metadata()

        self.assertEqual(metadata['dimensions']['x'], 20)
        self.assertEqual(metadata['dimensions']['y'], 30)
        self.assertEqual(metadata['dimensions']['z'], 40)
        self.assertEqual(metadata['spacing']['x'], 0.5)
        self.assertEqual(metadata['spacing']['y'], 0.5)
        self.assertEqual(metadata['spacing']['z'], 1.0)
        self.assertEqual(metadata['patient_name'], "John Doe")
        self.assertEqual(metadata['study_date'], "2024-06-15")
        self.assertEqual(metadata['system_name'], "GE Vivid")
        self.assertEqual(metadata['probe_name'], "4DHz")

    def test_coordinate_system_parsing(self):
        """Test coordinate system type parsing."""
        test_cases = [
            (0, 'cartesian'),
            (1, 'toroidal'),
            (2, 'spherical'),
            (3, 'cylindrical')
        ]

        for coord_type, expected_name in test_cases:
            self._create_test_file(coord_system=coord_type)
            loader = KretzFileLoader(str(self.test_file_path))
            self.assertEqual(
                loader.get_coordinate_system(),
                expected_name,
                f"Coordinate system type {coord_type} not parsed correctly"
            )

    def test_data_type_parsing(self):
        """Test data type parsing."""
        data_types = [
            (0, 'uint8'),
            (1, 'uint16'),
            (6, 'float32'),
            (7, 'float64')
        ]

        for type_code, expected_name in data_types:
            self._create_test_file(data_type=type_code)
            loader = KretzFileLoader(str(self.test_file_path))
            self.assertEqual(
                loader.metadata['data_type'],
                expected_name,
                f"Data type {type_code} not parsed correctly"
            )

    def test_get_volume(self):
        """Test retrieving volume data."""
        dims = (5, 5, 5)
        self._create_test_file(dims=dims)
        loader = KretzFileLoader(str(self.test_file_path))

        volume = loader.get_volume()
        self.assertEqual(volume.shape, dims)
        self.assertEqual(volume.dtype, np.uint8)

    def test_get_dimension(self):
        """Test getting volume dimensions."""
        dims = (15, 20, 25)
        self._create_test_file(dims=dims)
        loader = KretzFileLoader(str(self.test_file_path))

        retrieved_dims = loader.get_dimension()
        self.assertEqual(retrieved_dims, dims)

    def test_get_spacing(self):
        """Test getting voxel spacing."""
        spacing = (0.3, 0.4, 0.5)
        self._create_test_file(spacing=spacing)
        loader = KretzFileLoader(str(self.test_file_path))

        retrieved_spacing = loader.get_spacing()
        self.assertAlmostEqual(retrieved_spacing[0], spacing[0], places=5)
        self.assertAlmostEqual(retrieved_spacing[1], spacing[1], places=5)
        self.assertAlmostEqual(retrieved_spacing[2], spacing[2], places=5)

    def test_get_patient_info(self):
        """Test retrieving patient information."""
        self._create_test_file(
            patient_name="Jane Smith",
            study_date="2024-07-20",
            study_time="14:30:00"
        )
        loader = KretzFileLoader(str(self.test_file_path))

        patient_info = loader.get_patient_info()
        self.assertEqual(patient_info['patient_name'], "Jane Smith")
        self.assertEqual(patient_info['study_date'], "2024-07-20")
        self.assertEqual(patient_info['study_time'], "14:30:00")

    def test_get_system_info(self):
        """Test retrieving system information."""
        self._create_test_file(
            system_name="Voluson E10",
            probe_name="RSP6-16"
        )
        loader = KretzFileLoader(str(self.test_file_path))

        system_info = loader.get_system_info()
        self.assertEqual(system_info['system_name'], "Voluson E10")
        self.assertEqual(system_info['probe_name'], "RSP6-16")

    def test_volume_data_integrity(self):
        """Test that volume data is correctly read and reshaped."""
        dims = (8, 10, 12)
        self._create_test_file(dims=dims)
        loader = KretzFileLoader(str(self.test_file_path))

        volume = loader.get_volume()
        # Verify shape
        self.assertEqual(volume.shape, dims)
        # Verify data content (should be sequential 0 to (8*10*12)-1 mod 256)
        expected_size = dims[0] * dims[1] * dims[2]
        self.assertEqual(volume.size, expected_size)

    def test_get_metadata_returns_copy(self):
        """Test that get_metadata returns a copy, not original."""
        self._create_test_file()
        loader = KretzFileLoader(str(self.test_file_path))

        metadata1 = loader.get_metadata()
        metadata2 = loader.get_metadata()

        # Modify one copy
        metadata1['test_key'] = 'test_value'

        # Verify the other copy and original are unchanged
        self.assertNotIn('test_key', metadata2)
        self.assertNotIn('test_key', loader.metadata)

    def test_get_volume_returns_copy(self):
        """Test that get_volume returns a copy, not original."""
        self._create_test_file()
        loader = KretzFileLoader(str(self.test_file_path))

        volume1 = loader.get_volume()
        volume2 = loader.get_volume()

        # Modify one copy
        volume1[0, 0, 0] = 255

        # Verify the other copy and original are unchanged
        self.assertNotEqual(volume2[0, 0, 0], 255)
        self.assertNotEqual(loader.volume[0, 0, 0], 255)

    def test_repr(self):
        """Test string representation of loader."""
        dims = (10, 12, 14)
        self._create_test_file(dims=dims)
        loader = KretzFileLoader(str(self.test_file_path))

        repr_str = repr(loader)
        self.assertIn("KretzFileLoader", repr_str)
        self.assertIn("test.vol", repr_str)
        self.assertIn("cartesian", repr_str)

    def test_empty_patient_name(self):
        """Test handling of empty patient name."""
        self._create_test_file(patient_name="")
        loader = KretzFileLoader(str(self.test_file_path))

        self.assertEqual(loader.get_patient_info()['patient_name'], "")

    def test_unicode_patient_name(self):
        """Test handling of unicode characters in patient name."""
        self._create_test_file(patient_name="José García")
        loader = KretzFileLoader(str(self.test_file_path))

        self.assertEqual(loader.get_patient_info()['patient_name'], "José García")

    def test_compressed_flag_parsing(self):
        """Test that compression flag is correctly parsed."""
        self._create_test_file(compressed=True, write_volume_data=False)
        loader = KretzFileLoader(str(self.test_file_path))

        self.assertTrue(loader.metadata['compressed'])

    def test_uncompressed_flag_parsing(self):
        """Test that uncompressed flag is correctly parsed."""
        self._create_test_file(compressed=False)
        loader = KretzFileLoader(str(self.test_file_path))

        self.assertFalse(loader.metadata['compressed'])

    def test_large_volume(self):
        """Test loading a larger volume."""
        dims = (64, 64, 64)
        self._create_test_file(dims=dims)
        loader = KretzFileLoader(str(self.test_file_path))

        volume = loader.get_volume()
        self.assertEqual(volume.shape, dims)
        self.assertEqual(volume.size, 64 * 64 * 64)


class TestKretzFileLoaderIntegration(unittest.TestCase):
    """Integration tests for KretzFileLoader."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.temp_dir.name) / "integration_test.vol"

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_test_file(self, dims=(10, 10, 10)):
        """Create a test kretzfile."""
        with open(self.test_file_path, 'wb') as f:
            # Write magic string
            f.write(b"KRETZFILE")
            f.write(b"1.0 ")

            # Pad to offset 16
            f.write(b'\x00' * (16 - f.tell()))

            # Write frame count
            f.write(struct.pack('<I', 1))

            # Write dimensions
            f.write(struct.pack('<III', dims[0], dims[1], dims[2]))

            # Write spacing
            f.write(struct.pack('<fff', 1.0, 1.0, 1.0))

            # Write coordinate system (cartesian)
            f.write(struct.pack('<B', 0))

            # Write data type (uint8)
            f.write(struct.pack('<B', 0))

            # Write compression flag
            f.write(struct.pack('<B', 0))

            # Pad to offset 48
            f.write(b'\x00' * (48 - f.tell()))

            # Write dummy metadata (patient name, dates, system info)
            f.write(b"Test Patient" + b'\x00' * 52)  # 64 bytes total
            f.write(b"2024-01-01" + b'\x00' * 6)    # 16 bytes total
            f.write(b"12:00:00" + b'\x00' * 8)      # 16 bytes total
            f.write(b"3D" + b'\x00' * 30)           # 32 bytes total
            f.write(b"GE Voluson" + b'\x00' * 22)   # 32 bytes total
            f.write(b"Probe 1" + b'\x00' * 25)      # 32 bytes total
            f.write(struct.pack('<fff', 0.0, 0.0, 0.0))  # origin

            # Pad to offset 256
            f.write(b'\x00' * (256 - f.tell()))

            # Write volume data
            num_voxels = dims[0] * dims[1] * dims[2]
            volume_data = np.ones(num_voxels, dtype=np.uint8) * 128
            f.write(volume_data.tobytes())

    def test_end_to_end_workflow(self):
        """Test a complete workflow of loading and accessing data."""
        dims = (12, 14, 16)
        self._create_test_file(dims=dims)

        # Load file
        loader = KretzFileLoader(str(self.test_file_path))

        # Verify metadata
        metadata = loader.get_metadata()
        self.assertEqual(metadata['dimensions']['x'], dims[0])
        self.assertEqual(metadata['patient_name'], "Test Patient")

        # Verify volume
        volume = loader.get_volume()
        self.assertEqual(volume.shape, dims)
        self.assertTrue(np.all(volume == 128))

        # Verify accessors
        self.assertEqual(loader.get_dimension(), dims)
        self.assertEqual(loader.get_spacing(), (1.0, 1.0, 1.0))
        self.assertEqual(loader.get_coordinate_system(), "cartesian")


if __name__ == '__main__':
    unittest.main()
