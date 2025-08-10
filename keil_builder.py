#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import shutil
import threading
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime


class KeilBuilder:

    def __init__(self):
        self.current_dir = Path.cwd()
        self.keil_path = self._find_keil_uv4()
        self.project_path = None
        self.project_target = None
        self.parallel_jobs = 0
        self.build_log_file = self.current_dir / "keil_builder.log"

    def _find_keil_uv4(self) -> Path:
        locations = [
            "D:/000_soft/keiluVision5/core/UV4/UV4.exe",
        ]
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            uv4_path = Path(path_dir) / "UV4.exe"
            if uv4_path.exists():
                return uv4_path
        for location in locations:
            if Path(location).exists():
                return Path(location)
        return Path("UV4.exe")

    def _find_projects(self) -> List[Path]:
        projects = []
        for suffix in [".uvprojx", ".uvproj"]:
            projects.extend(self.current_dir.rglob(f"*{suffix}"))
        return projects

    def _parse_output_info(self) -> Tuple[Optional[str], Optional[str]]:
        if not self.build_log_file.exists():
            return None, None
        try:
            content = self.build_log_file.read_text(encoding="utf-8", errors="ignore")
            match = re.search(
                r'"([^"]+)"\s*-\s*\d+\s*Error\(s\),\s*\d+\s*Warning\(s\)', content
            )
            if match:
                output_path = match.group(1)
                path_obj = Path(output_path)
                return str(path_obj.parent), path_obj.name.replace(".axf", "")
        except:
            pass
        return None, None

    def _combine_path(self, base_path: Path, relative_path: str) -> Optional[Path]:
        try:
            if Path(relative_path).is_absolute():
                return Path(relative_path)
            if not relative_path.startswith("."):
                relative_path = "./" + relative_path
            return (base_path.parent / relative_path).resolve()
        except:
            return None

    def _print_build_output(self, stop_event: threading.Event):
        last_pos = 0
        while not stop_event.is_set():
            try:
                if self.build_log_file.exists():
                    with open(
                        self.build_log_file, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        f.seek(last_pos)
                        new_content = f.read()
                        if new_content:
                            print(new_content, end="")
                            last_pos = f.tell()
            except:
                pass
            time.sleep(0.2)

    def _show_help(self):
        print("Keil Builder - Automated Keil Compilation Tool")
        print("Usage: python keil_builder.py [options] [project_file] [target]")
        print()
        print("Options:")
        print(
            "  -j<n>           Set parallel compilation jobs (default: -j0 = all cores)"
        )
        print("                  Examples: -j1, -j2, -j4, -j8")
        print("  -h, --help, /?  Show this help message")
        print()
        print("Arguments:")
        print("  project_file    Keil project file (.uvprojx or .uvproj)")
        print("                  If not specified, auto-detect in current directory")
        print("  target          Build target name (optional)")
        print()
        print("Examples:")
        print(
            "  python keil_builder.py                    # Auto-detect project, use -j0"
        )
        print("  python keil_builder.py -j4                # Use 4 parallel jobs")
        print("  python keil_builder.py project.uvprojx    # Build specific project")
        print(
            "  python keil_builder.py -j2 project.uvprojx Debug  # Build with options"
        )

    def _process_args(self, args: List[str]):
        for arg in args:
            if "UV4.exe" in arg:
                self.keil_path = Path(arg)
            elif arg.startswith("-j") and len(arg) > 2:
                try:
                    self.parallel_jobs = int(arg[2:])
                    print(f"[INFO] Parallel jobs set to: {self.parallel_jobs}")
                except ValueError:
                    print(f"[WARNING] Invalid -j parameter: {arg}, using default -j0")
                    self.parallel_jobs = 0
            elif arg.endswith((".uvprojx", ".uvproj")):
                if Path(arg).is_absolute():
                    self.project_path = Path(arg)
                else:
                    self.project_path = self.current_dir / arg
            elif arg in ["-h", "--help", "/?"]:
                self._show_help()
                sys.exit(0)
            elif not any(char in arg for char in '<>:|/\\"*?'):
                self.project_target = arg

    def build(self, args: List[str]) -> int:
        print("[INFO] Keil Builder - Starting Build Process")
        self._process_args(args)
        if not self.project_path:
            projects = self._find_projects()
            if not projects:
                print("[ERROR] No Keil project found!")
                return -1
            self.project_path = projects[-1]
            print(f"[INFO] Auto-detected: {self.project_path.name}")
        if not self.project_path.exists():
            print(f"[ERROR] Project not found: {self.project_path}")
            return -1
        print(f"[INFO] Project: {self.project_path.name}")
        print(f"[INFO] Keil: {self.keil_path}")
        print(
            f"[INFO] Parallel Jobs: -j{self.parallel_jobs} ({'all cores' if self.parallel_jobs == 0 else f'{self.parallel_jobs} cores'})"
        )
        if self.project_target:
            print(f"[INFO] Target: {self.project_target}")
        print(f"[INFO] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("─" * 60)
        cmd = [
            str(self.keil_path),
            f"-j{self.parallel_jobs}",
            "-r",
            str(self.project_path),
        ]
        if self.project_target:
            cmd.extend(["-t", self.project_target])
        cmd.extend(["-o", str(self.build_log_file)])
        print(f"[INFO] Command: {' '.join(cmd)}")
        print("─" * 60)
        self.build_log_file.write_text("", encoding="utf-8")
        stop_event = threading.Event()
        output_thread = threading.Thread(
            target=self._print_build_output, args=(stop_event,)
        )
        output_thread.daemon = True
        output_thread.start()
        try:
            result = subprocess.run(cmd, capture_output=False, text=True, timeout=300)
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            print("\n[ERROR] Build timeout!")
            return -1
        except Exception as e:
            print(f"\n[ERROR] Build error: {e}")
            return -1
        finally:
            time.sleep(1)
            stop_event.set()
            output_thread.join(timeout=1)
        output_dir, output_name = self._parse_output_info()
        print("\n" + "─" * 60)
        if exit_code == 0:
            print("[SUCCESS] Build completed successfully")
        elif exit_code == 1:
            print("[SUCCESS] Build completed with warnings")
        else:
            print(f"[ERROR] Build failed (exit code: {exit_code})")
            return exit_code
        if output_dir and output_name:
            output_path = self._combine_path(self.project_path, output_dir)
            if output_path and output_path.exists():
                output_files = []
                for suffix in [".hex", ".bin"]:
                    files = list(output_path.glob(f"{output_name}{suffix}"))
                    output_files.extend(files)
                if output_files:
                    print(f"\n[INFO] OUTPUT FILES:")
                    for file in output_files:
                        print(f"   - {file.name} ({file.stat().st_size:,} bytes)")
                        try:
                            shutil.copy2(file, self.current_dir)
                            print(f"   [OK] Copied to: {self.current_dir}")
                        except Exception as e:
                            print(f"   [ERROR] Copy failed: {e}")
                else:
                    print("[WARNING] No output files found")
        print("─" * 60)
        return exit_code


def main():
    try:
        builder = KeilBuilder()
        exit_code = builder.build(sys.argv[1:])
        if exit_code == 0:
            print("[INFO] Done!")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted")
        sys.exit(-1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(-1)


if __name__ == "__main__":
    main()
