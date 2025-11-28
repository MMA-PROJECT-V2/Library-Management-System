"""Compatibility shim so tests can import the app as ``books``.

The real Django app lives at ``backend.books_service.books``. Tests import
``books`` (and submodules like ``books.models``). To make those imports
work when running from the repository root, import the real backend module
and register equivalents in ``sys.modules``.
"""
import importlib
import sys
import types

# Load the real package
_real = importlib.import_module('backend.books_service.books')

# Create a lightweight module named 'books' that exposes the backend package's
# attributes and acts as the public package for tests.
_shim = types.ModuleType('books')

# Copy some standard attributes from the real package if present
for _attr in ('__file__', '__path__', '__package__', '__loader__', '__spec__'):
	if hasattr(_real, _attr):
		setattr(_shim, _attr, getattr(_real, _attr))

# Copy public symbols (avoid private names)
for _k, _v in _real.__dict__.items():
	if not _k.startswith('_'):
		try:
			setattr(_shim, _k, _v)
		except Exception:
			pass

# Make the shim act like a real package by exposing the backend package's
# filesystem search path. This avoids importing submodules (like
# ``models``) at shim-import time — which would instantiate Django models
# before the Django app registry is ready.
if hasattr(_real, '__path__'):
	_shim.__path__ = list(getattr(_real, '__path__'))

# Create a ModuleSpec for the shim so import machinery treats it as a package
try:
	from importlib import util as _util
	_shim.__spec__ = _util.spec_from_loader('books', loader=None, submodule_search_locations=getattr(_shim, '__path__', None))
except Exception:
	pass

# Register the shim in sys.modules so `import books` and `import books.xxx`
# resolve to the backend package files on disk without eagerly importing
# those submodules here.
sys.modules['books'] = _shim
