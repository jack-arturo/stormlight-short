#!/usr/bin/env python3
"""
Test Suite for Stormlight Short Pipeline
Comprehensive testing of all pipeline components.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from vertex_manager import VertexVideoManager
from flow_manager import FlowManager
from midjourney_manager import MidjourneyManager
from safety_manager import SafetyManager


class TestVertexManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "03_vertex_jobs").mkdir(parents=True)
        
        self.manager = VertexVideoManager("test-project")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_job_folder(self):
        """Test job folder creation with proper structure"""
        job_path = self.manager.create_job_folder("test_scene", 1)
        
        self.assertTrue(job_path.exists())
        self.assertTrue((job_path / "inputs").exists())
        self.assertTrue((job_path / "outputs").exists())
        self.assertTrue((job_path / "metadata").exists())
        
        # Check naming convention
        self.assertIn("test_scene_take01", str(job_path))
    
    def test_prepare_veo3_request(self):
        """Test Veo 3 request payload preparation"""
        request = self.manager.prepare_veo3_request(
            prompt="Test prompt",
            negative_prompt="bad quality",
            seed=12345,
            duration=10
        )
        
        self.assertIn("instances", request)
        self.assertEqual(request["instances"][0]["prompt"], "Test prompt")
        self.assertEqual(request["instances"][0]["seed"], 12345)
        self.assertEqual(request["instances"][0]["duration"], 10)
    
    def test_save_job_metadata(self):
        """Test metadata saving functionality"""
        job_path = self.manager.create_job_folder("test_scene", 1)
        request_payload = self.manager.prepare_veo3_request("Test prompt")
        
        metadata = self.manager.save_job_metadata(job_path, request_payload)
        
        # Check files were created
        self.assertTrue((job_path / "metadata" / "job_metadata.json").exists())
        self.assertTrue((job_path / "inputs" / "request_payload.json").exists())
        self.assertTrue((job_path / "README.md").exists())
        
        # Verify metadata content
        self.assertIn("timestamp", metadata)
        self.assertIn("request_payload", metadata)


class TestFlowManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "04_flow_exports").mkdir(parents=True)
        (self.temp_dir / "02_prompts").mkdir(parents=True)
        
        self.manager = FlowManager(self.temp_dir)
        
        # Create test file
        self.test_file = self.temp_dir / "test_video.mp4"
        self.test_file.write_text("fake video content")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_organize_flow_export(self):
        """Test Flow export organization"""
        organized_path = self.manager.organize_flow_export(
            self.test_file,
            "test_scene",
            "Test prompt",
            seed=12345
        )
        
        self.assertTrue(organized_path.exists())
        self.assertIn("test_scene_take01", organized_path.name)
        self.assertIn("seed12345", organized_path.name)
        
        # Check metadata file
        metadata_path = organized_path.with_suffix(organized_path.suffix + ".meta.json")
        self.assertTrue(metadata_path.exists())
    
    def test_get_next_take_number(self):
        """Test take number generation"""
        # First take should be 1
        take_num = self.manager._get_next_take_number("new_scene")
        self.assertEqual(take_num, 1)
        
        # Create a fake existing take
        scene_dir = self.temp_dir / "04_flow_exports" / "new_scene"
        scene_dir.mkdir(parents=True)
        (scene_dir / "new_scene_take01_20241215_120000.mp4").touch()
        
        # Next take should be 2
        take_num = self.manager._get_next_take_number("new_scene")
        self.assertEqual(take_num, 2)


class TestMidjourneyManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "01_styleframes_midjourney").mkdir(parents=True)
        (self.temp_dir / "02_prompts").mkdir(parents=True)
        
        self.manager = MidjourneyManager(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('PIL.Image.open')
    def test_validate_image(self, mock_image_open):
        """Test image validation"""
        # Mock valid image
        mock_img = MagicMock()
        mock_img.size = (1920, 1080)  # Valid 16:9 resolution
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        test_file = self.temp_dir / "test.png"
        test_file.touch()
        
        is_valid, message = self.manager.validate_image(test_file)
        self.assertTrue(is_valid)
        self.assertIn("Valid", message)
    
    def test_extract_seed_from_filename(self):
        """Test seed extraction from filenames"""
        # Test various filename patterns
        test_cases = [
            ("image_12345.png", 12345),
            ("style_frame_seed_67890.jpg", 67890),
            ("test_--seed 11111.png", 11111),
            ("no_seed_here.png", None)
        ]
        
        for filename, expected_seed in test_cases:
            result = self.manager.extract_seed_from_filename(filename)
            self.assertEqual(result, expected_seed)


class TestSafetyManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)
        
        # Create required directories
        (self.temp_dir / "00_docs" / "safety_logs").mkdir(parents=True)
        
        self.manager = SafetyManager(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_log_operation(self):
        """Test operation logging"""
        self.manager.log_operation(
            "test_operation",
            {"key": "value"},
            approved=True,
            user_confirmation="yes"
        )
        
        self.assertTrue(self.manager.safety_log.exists())
        
        # Read and verify log entry
        with open(self.manager.safety_log, 'r') as f:
            log_entry = json.loads(f.read().strip())
        
        self.assertEqual(log_entry["operation"], "test_operation")
        self.assertTrue(log_entry["approved"])
    
    def test_estimate_gcs_costs(self):
        """Test GCS cost estimation"""
        estimates = self.manager.estimate_gcs_costs(
            "gcs_upload",
            {"file_count": 100, "total_size_gb": 5.0}
        )
        
        self.assertIn("storage_cost", estimates)
        self.assertIn("operation_cost", estimates)
        self.assertIn("total_estimated", estimates)
        self.assertGreater(estimates["total_estimated"], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)
        
        # Create full directory structure
        dirs = [
            "00_docs/sync_logs",
            "01_styleframes_midjourney",
            "02_prompts",
            "03_vertex_jobs",
            "04_flow_exports",
            "05_audio",
            "06_final_cut",
            "config"
        ]
        
        for dir_path in dirs:
            (self.temp_dir / dir_path).mkdir(parents=True)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_pipeline_structure(self):
        """Test that all required directories exist"""
        required_dirs = [
            "00_docs", "01_styleframes_midjourney", "02_prompts",
            "03_vertex_jobs", "04_flow_exports", "05_audio", "06_final_cut"
        ]
        
        for dir_name in required_dirs:
            self.assertTrue((self.temp_dir / dir_name).exists())


def run_tests():
    """Run all tests with detailed output"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestVertexManager,
        TestFlowManager,
        TestMidjourneyManager,
        TestSafetyManager,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
