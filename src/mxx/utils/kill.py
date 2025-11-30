"""Utility helpers to locate and terminate processes by executable path."""

from pathlib import Path

import psutil


def _canonical_path(path: str | Path) -> Path:
	return Path(path).expanduser().resolve()


def processes_by_path(executable_path: str | Path) -> list[psutil.Process]:
	"""Return every running process whose executable matches the given path."""

	target = _canonical_path(executable_path)
	matches: list[psutil.Process] = []

	for proc in psutil.process_iter(["exe"]):
		try:
			exe = proc.info.get("exe")
			if not exe:
				continue
			proc_path = Path(exe).resolve()
			if proc_path == target:
				matches.append(proc)
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
			continue

	return matches


def kill_processes_by_path(
	executable_path: str | Path,
	*,
	wait_timeout: float = 5.0,
) -> int:
	"""Terminate every process whose executable matches ``executable_path``.

	Args:
		wait_timeout: Seconds to wait after ``terminate`` before forcing ``kill``.
	"""

	processes = processes_by_path(executable_path)
	if not processes:
		return 0

	terminated = 0
	for proc in processes:
		try:
			proc.terminate()
			terminated += 1
		except (psutil.NoSuchProcess, psutil.AccessDenied):
			continue

	_, still_alive = psutil.wait_procs(processes, timeout=wait_timeout)

	for proc in still_alive:
		try:
			proc.kill()
		except (psutil.NoSuchProcess, psutil.AccessDenied):
			continue

	return terminated
