import os
import sys

# Ensure the test runner can import the Django project package when running from the repo root.
# Insert `backend/books_service` so `books_service` and the `books` app are importable,
# set DJANGO_SETTINGS_MODULE and change CWD so pytest-django can find `manage.py`.
ROOT = os.path.dirname(__file__)
REPO_ROOT = ROOT
PROJECT_ROOT = os.path.join(REPO_ROOT, 'backend', 'books_service')

# Ensure both the repository root and the Django project package are on sys.path
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ensure Django settings module is set for pytest-django (pointing to the project package)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'books_service.settings')

# Change working directory so pytest-django can locate manage.py inside the project
try:
    os.chdir(PROJECT_ROOT)
except FileNotFoundError:
    # If the expected path doesn't exist, leave cwd unchanged and allow pytest to report the error
    pass


    def pytest_terminal_summary(terminalreporter, exitstatus, config):
        """Print a concise combined test summary (totals and pass percentage).

        This hooks into pytest's terminal summary so the pass percentage appears
        right under the regular pytest output.
        """
        stats = terminalreporter.stats

        def _count(key):
            return len(stats.get(key, []))

        passed = _count('passed')
        failed = _count('failed')
        errors = _count('error') + _count('errors')
        skipped = _count('skipped')
        xfailed = _count('xfailed')
        xpassed = _count('xpassed')

        total = passed + failed + errors + skipped + xfailed + xpassed
        pass_pct = (passed / total * 100) if total else 0.0

        terminalreporter.write_sep('=', 'Tests summary')
        terminalreporter.write_line(f'  Total tests: {total}')
        terminalreporter.write_line(f'  Passed:      {passed}')
        terminalreporter.write_line(f'  Failed:      {failed}')
        terminalreporter.write_line(f'  Errors:      {errors}')
        terminalreporter.write_line(f'  Skipped:     {skipped}')
        terminalreporter.write_line(f'  XFailed:     {xfailed}')
        terminalreporter.write_line(f'  XPassed:     {xpassed}')
        terminalreporter.write_line(f'  Pass rate:   {pass_pct:.2f}%')


    # Collect per-test results in execution order so we can print them with percentages
    _TEST_RESULTS = []


    def pytest_runtest_logreport(report):
        # Called for each setup/call/teardown phase; we only care about the call phase
        if report.when != 'call':
            return
        # report.nodeid is like 'tests/test_mod.py::TestClass::test_name'
        status = report.outcome.upper()
        _TEST_RESULTS.append((report.nodeid, status))


    def _print_per_test_progress(terminalreporter):
        total = len(_TEST_RESULTS)
        if total == 0:
            return
        terminalreporter.write_sep('-', 'Per-test progress')
        for i, (nodeid, status) in enumerate(_TEST_RESULTS, start=1):
            pct = int(i / total * 100)
            terminalreporter.write_line(f"{nodeid} {status} [{pct:3d}%]")


    # Ensure the per-test listing is printed before the summary block
    def pytest_sessionfinish(session, exitstatus):
        # session.config.pluginmanager.get_plugin('terminalreporter') may be used,
        # but pytest passes the terminalreporter to pytest_terminal_summary; here
        # we directly obtain it from the session if available and print the per-test
        # progress so users running `pytest` see it in the run output.
        tr = session.config.pluginmanager.get_plugin('terminalreporter')
        if tr is not None:
            _print_per_test_progress(tr)


    def pytest_configure(config):
        # Disable pytest's built-in progress reporting (dots/percent lines)
        tr = config.pluginmanager.get_plugin('terminalreporter')
        if tr is not None:
            try:
                tr.showprogress = False
            except Exception:
                pass
        # Force verbose level to 0 so pytest won't print per-file progress even
        # when the user passes -v. This gives us only the per-test listing and
        # final summary that we generate.
        try:
            # If the option exists, override it
            if hasattr(config.option, 'verbose'):
                config.option.verbose = 0
        except Exception:
            pass
