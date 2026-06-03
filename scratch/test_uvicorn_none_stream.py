import sys

# Save the original standard streams so we can restore them for printing!
orig_stdout = sys.stdout
orig_stderr = sys.stderr

class DummyStream:
    def write(self, data):
        pass
    def flush(self):
        pass
    def isatty(self):
        return False

# 1. Simulate user's environment: set standard streams to None
sys.stdout = None
sys.stderr = None
sys.stdin = None

# 2. Apply our defensive replacement
if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()
if sys.stdin is None:
    sys.stdin = DummyStream()

# 3. Test importing and configuring uvicorn
error_occurred = None
try:
    import uvicorn
    from ayen_ode.server import app
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=54224,
        log_level="warning",
        access_log=False,
        lifespan="on",
    )
except Exception as e:
    import traceback
    error_occurred = traceback.format_exc()

# Restore original streams so we can print the result
sys.stdout = orig_stdout
sys.stderr = orig_stderr

if error_occurred:
    print("FAILED TO INITIALIZE UVICORN CONFIG!")
    print(error_occurred)
else:
    print("SUCCESSFULLY INITIALIZED UVICORN CONFIG!")
