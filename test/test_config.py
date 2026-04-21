import json
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
ROOT_CONFIG_FILE = ROOT_DIR / "config.json"


class ConfigLoadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._created_root_config = False
        if not ROOT_CONFIG_FILE.exists():
            ROOT_CONFIG_FILE.write_text(json.dumps({"auth-key": "test-auth"}), encoding="utf-8")
            cls._created_root_config = True

        from services import config as config_module

        cls.config_module = config_module

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._created_root_config and ROOT_CONFIG_FILE.exists():
            ROOT_CONFIG_FILE.unlink()

    def test_load_settings_falls_back_to_example_when_config_path_is_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            data_dir = base_dir / "data"
            config_dir = base_dir / "config.json"
            example_file = base_dir / "config.example.json"

            config_dir.mkdir()
            example_file.write_text(
                json.dumps({"auth-key": "example-auth", "refresh_account_interval_minute": 15}),
                encoding="utf-8",
            )

            module = self.config_module
            old_base_dir = module.BASE_DIR
            old_data_dir = module.DATA_DIR
            old_config_file = module.CONFIG_FILE
            old_config_example_file = module.CONFIG_EXAMPLE_FILE
            try:
                module.BASE_DIR = base_dir
                module.DATA_DIR = data_dir
                module.CONFIG_FILE = config_dir
                module.CONFIG_EXAMPLE_FILE = example_file

                settings = module._load_settings()

                self.assertEqual(settings.auth_key, "example-auth")
                self.assertEqual(settings.refresh_account_interval_minute, 15)
            finally:
                module.BASE_DIR = old_base_dir
                module.DATA_DIR = old_data_dir
                module.CONFIG_FILE = old_config_file
                module.CONFIG_EXAMPLE_FILE = old_config_example_file


if __name__ == "__main__":
    unittest.main()
