#!/usr/bin/env python3
"""
Internal alert display script - launched as separate process
DO NOT call this directly - use notebook_auto_alert.py instead
"""

import sys
import subprocess
import tkinter as tk
from datetime import datetime


def show_alert_window(success=True, message=""):
    """Show the alert window"""

    root = tk.Tk()
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.95)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    if success:
        bg_color = '#00FF00'  # Green
        title_text = "✓ NOTEBOOK COMPLETE ✓"
        sound = "Glass"
    else:
        bg_color = '#FF0000'  # Red
        title_text = "✗ NOTEBOOK ERROR ✗"
        sound = "Basso"

    root.configure(bg=bg_color)

    window_width = 650
    window_height = 300
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    root.title("Notebook Alert")

    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(expand=True, fill='both', padx=20, pady=20)

    title_label = tk.Label(
        main_frame,
        text=title_text,
        font=('Arial', 32, 'bold'),
        bg=bg_color,
        fg='white'
    )
    title_label.pack(pady=15)

    time_str = datetime.now().strftime('%I:%M:%S %p')
    display_msg = message if message else f"Completed at {time_str}"

    message_label = tk.Label(
        main_frame,
        text=display_msg,
        font=('Arial', 16),
        bg=bg_color,
        fg='white',
        justify='center',
        wraplength=600
    )
    message_label.pack(pady=15)

    close_btn = tk.Button(
        main_frame,
        text="OK",
        font=('Arial', 14, 'bold'),
        command=root.destroy,
        bg='white',
        fg=bg_color,
        padx=30,
        pady=10
    )
    close_btn.pack(pady=15)

    # Flash effect
    def flash(count=0):
        if count < 8:
            try:
                current_alpha = root.attributes('-alpha')
                new_alpha = 0.3 if current_alpha > 0.5 else 0.95
                root.attributes('-alpha', new_alpha)
                root.after(150, lambda: flash(count + 1))
            except:
                pass

    flash()

    # System notification
    try:
        subprocess.run([
            'osascript', '-e',
            f'display notification "{display_msg[:100]}" '
            f'with title "{title_text}" sound name "{sound}"'
        ], check=False, capture_output=True, timeout=2)
    except:
        pass

    # Play sound
    try:
        subprocess.Popen(['afplay', f'/System/Library/Sounds/{sound}.aiff'],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except:
        pass

    root.after(12000, root.destroy)
    root.mainloop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python _show_alert.py <success|error> [message]")
        sys.exit(1)

    alert_type = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else ""

    success = alert_type == "success"
    show_alert_window(success, message)
