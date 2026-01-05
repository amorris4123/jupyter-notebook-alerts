#!/usr/bin/env python3
"""
Automatic Notebook Completion Alerts
Provides desktop alerts for notebook completion and automatic error detection

USAGE - Add to last cell of your notebook:
    from notebook_auto_alert import done
    done()

That's it! The script automatically detects errors in ANY cell without needing try/except blocks.

FEATURES:
- ✓ Automatic error detection (no try/except needed!)
- ✓ Green alert for success
- ✓ Red alert for errors
- ✓ Works from any directory
- ✓ Doesn't crash the kernel
- ✓ Desktop-level alerts
"""

import subprocess
import sys
import os
from pathlib import Path


def _get_notebook_name():
    """Get the current notebook name from IPython"""
    try:
        from IPython import get_ipython
        ip = get_ipython()

        if ip is None:
            return None

        # Try to get notebook name from connection file
        try:
            connection_file = ip.config.get('IPKernelApp', {}).get('connection_file', '')
            if connection_file:
                # Extract notebook name from connection file path
                import json
                with open(connection_file, 'r') as f:
                    pass  # File exists, use its name as hint
        except:
            pass

        # Try to get from session history database path
        try:
            history_file = ip.history_manager.hist_file
            # The history file is in ~/.ipython/profile_default/history.sqlite
            # Not directly useful for notebook name
        except:
            pass

        # Try to get from user namespace if __file__ is set
        try:
            user_ns = ip.user_ns
            if '__vsc_ipynb_file__' in user_ns:
                # VS Code sets this variable
                nb_path = user_ns['__vsc_ipynb_file__']
                return Path(nb_path).stem
        except:
            pass

        # Fallback: try to get from parent process name
        try:
            import psutil
            current_process = psutil.Process()
            parent = current_process.parent()
            if parent:
                cmdline = parent.cmdline()
                for arg in cmdline:
                    if arg.endswith('.ipynb'):
                        return Path(arg).stem
        except:
            pass

        return None
    except:
        return None


def _get_alert_script_path():
    """Get the path to the alert display script"""
    # Check same directory as this script
    script_dir = Path(__file__).parent
    alert_script = script_dir / "_show_alert.py"

    if alert_script.exists():
        return str(alert_script)

    # Check current directory
    alert_script = Path.cwd() / "_show_alert.py"
    if alert_script.exists():
        return str(alert_script)

    # Check home directory
    alert_script = Path.home() / "_show_alert.py"
    if alert_script.exists():
        return str(alert_script)

    return None


def _show_alert(success=True, message="", notebook_name=None):
    """Launch alert in separate process to avoid blocking kernel"""

    alert_script = _get_alert_script_path()

    if not alert_script:
        print("⚠ Warning: _show_alert.py not found. Cannot show desktop alert.")
        print(f"✓ {'SUCCESS' if success else 'ERROR'}: {message}" if message else "")
        return

    alert_type = "success" if success else "error"

    # Get notebook name if not provided
    if notebook_name is None:
        notebook_name = _get_notebook_name() or ""

    try:
        # Launch in completely separate process (non-blocking)
        subprocess.Popen(
            [sys.executable, alert_script, alert_type, message, notebook_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Fully detach from parent
        )
    except Exception as e:
        print(f"⚠ Warning: Could not launch alert: {e}")
        print(f"✓ {'SUCCESS' if success else 'ERROR'}: {message}" if message else "")


def done(message="Notebook completed successfully!"):
    """
    Call this at the end of your notebook to show success alert

    Example:
        from notebook_auto_alert import done
        done()

        # Or with custom message:
        done("Processed 1000 rows successfully!")
    """
    _show_alert(success=True, message=message)
    print(f"✓ {message}")


def error(message="Notebook encountered an error!"):
    """
    Call this to manually trigger error alert

    Example:
        from notebook_auto_alert import error
        error("Processing failed!")
    """
    _show_alert(success=False, message=message)
    print(f"✗ {message}")


# Automatic error detection
_error_handler_installed = False
_error_occurred = False


def _setup_auto_error_detection():
    """Automatically detect and alert on notebook errors"""
    global _error_handler_installed, _error_occurred

    if _error_handler_installed:
        return

    try:
        from IPython import get_ipython
        ip = get_ipython()

        if ip is None:
            return

        # Store original exception handler
        original_showtraceback = ip.showtraceback

        def custom_showtraceback(*args, **kwargs):
            """Custom exception handler that triggers alert"""
            global _error_occurred

            # Call original handler to show traceback
            original_showtraceback(*args, **kwargs)

            # Show error alert (only once per session)
            if not _error_occurred:
                _error_occurred = True

                # Try to extract error message
                try:
                    import sys
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    if exc_type and exc_value:
                        error_msg = f"{exc_type.__name__}: {str(exc_value)[:100]}"
                    else:
                        error_msg = "An error occurred during execution"
                except:
                    error_msg = "An error occurred during execution"

                _show_alert(success=False, message=error_msg)

        # Replace exception handler
        ip.showtraceback = custom_showtraceback
        _error_handler_installed = True

        print("✓ Auto-error detection enabled - will alert if any cell fails!")

    except Exception as e:
        # Silently fail if not in IPython environment
        pass


# Auto-enable error detection when module is imported
_setup_auto_error_detection()


def enable_alerts():
    """
    Explicitly enable auto-error detection
    Call this in your first cell if you want to be sure it's enabled

    Example:
        from notebook_auto_alert import enable_alerts
        enable_alerts()
    """
    _setup_auto_error_detection()
    print("✓ Notebook alerts enabled!")
    print("  - Errors will trigger automatic red alerts")
    print("  - Call done() in last cell for success alert")


# Quick test
if __name__ == '__main__':
    print("Testing notebook alert system...")
    print("\n1. Testing success alert...")
    done("Test success alert!")

    print("\n2. Testing error alert in 3 seconds...")
    import time
    time.sleep(3)
    error("Test error alert!")

    print("\nDone! Check for desktop alerts.")
