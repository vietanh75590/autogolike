import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bot', ROOT / 'golike_bot.py')
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)


class MobileRuntimeTests(unittest.TestCase):
    def test_config_path_does_not_depend_on_working_directory(self):
        previous = os.getcwd()
        with tempfile.TemporaryDirectory() as folder:
            try:
                os.chdir(folder)
                self.assertEqual(Path(bot.CONFIG_FILE), ROOT / 'config.json')
            finally:
                os.chdir(previous)

    def test_config_roundtrip_private_permissions(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'config.json'
            with patch.object(bot, 'CONFIG_FILE', str(target)):
                bot.ConfigManager.save({'token': 'test-only', 'account_name': 'Điện thoại'})
                self.assertEqual(bot.ConfigManager.load()['account_name'], 'Điện thoại')
                if os.name != 'nt':
                    self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_non_object_config_does_not_crash_startup(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'config.json'
            target.write_text('[]')
            with patch.object(bot, 'CONFIG_FILE', str(target)):
                self.assertEqual(bot.ConfigManager.load(), {})

    @patch.object(bot, 'is_termux_env', return_value=True)
    @patch.object(bot.subprocess, 'run')
    def test_android_falls_back_when_termux_opener_fails(self, run, _):
        run.side_effect = [FileNotFoundError(), subprocess.CompletedProcess([], 0)]
        self.assertTrue(bot.open_job_url('https://example.com/video'))
        self.assertEqual(run.call_args_list[0].args[0][0], 'termux-open-url')
        self.assertEqual(run.call_args_list[1].args[0], [
            'am', 'start', '-a', 'android.intent.action.VIEW', '-d', 'https://example.com/video'])

    @patch.object(bot, 'is_termux_env', return_value=False)
    @patch.object(bot.webbrowser, 'open', return_value=False)
    def test_browser_failure_is_reported(self, *_):
        self.assertFalse(bot.open_job_url('https://example.com'))

    def test_launcher_works_outside_checkout(self):
        result = subprocess.run(['bash', str(ROOT / 'run.sh'), '--help'],
                                cwd='/tmp', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--config', result.stdout)

    def test_check_does_not_read_config_or_call_api(self):
        with patch.object(bot.sys, 'argv', ['golike_bot.py', '--check']), \
                patch.object(bot.ConfigManager, 'load') as load, \
                patch.object(bot, 'http_request') as http:
            bot.main()
            load.assert_not_called()
            http.assert_not_called()

    def test_zero_cli_overrides_saved_limits(self):
        cfg = {'token': 'test-only', 'platform': 'tiktok', 'account_id': 1,
               'job_interval': 5, 'max_jobs': 10}
        with patch.object(bot.sys, 'argv', ['golike_bot.py', '--interval', '0', '--max-jobs', '0']), \
                patch.object(bot.ConfigManager, 'load', return_value=cfg), \
                patch.object(bot, 'GolikeBot') as runner:
            bot.main()
            self.assertEqual(runner.call_args.args[0]['job_interval'], 0)
            self.assertEqual(runner.call_args.args[0]['max_jobs'], 0)
            runner.return_value.run.assert_called_once()

    def test_invalid_config_reports_actionable_error(self):
        with self.assertRaisesRegex(ValueError, '--config'):
            bot.validate_config({'token': 'test-only', 'platform': 'tiktok', 'account_id': 0})

    def test_installer_success_with_simulated_termux_packages(self):
        with tempfile.TemporaryDirectory() as folder:
            pkg = Path(folder) / 'pkg'
            pkg.write_text('#!/bin/sh\nexit 0\n')
            pkg.chmod(0o700)
            result = subprocess.run(['bash', str(ROOT / 'install_termux.sh')],
                                    env={**os.environ, 'PATH': folder + os.pathsep + os.environ['PATH']},
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Cài đặt hoàn tất', result.stdout)
            self.assertIn('TLS:', result.stdout)

    def test_installer_stops_when_package_update_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            pkg = Path(folder) / 'pkg'
            pkg.write_text('#!/bin/sh\nexit 42\n')
            pkg.chmod(0o700)
            result = subprocess.run(['bash', str(ROOT / 'install_termux.sh')],
                                    env={**os.environ, 'PATH': folder + os.pathsep + os.environ['PATH']},
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 42)
            self.assertNotIn('Cài đặt hoàn tất', result.stdout)


if __name__ == '__main__':
    unittest.main()
