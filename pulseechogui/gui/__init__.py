"""
GUI applications for PulseEchoGui.

Interactive graphical interfaces for pulse sequence simulation:
- Basic 2-pulse and 3-pulse spin echo sequences
- Advanced shaped pulse explorers
- Real-time parameter modification interfaces
"""

# Import GUI modules (they contain tkinter so only import when needed)


def launch_basic_gui():
    """Launch the basic spin echo GUI (parallel version)."""
    from .Spin_echo_2p_3p_gui import main

    main()


def launch_basic_gui_single():
    """Launch the basic spin echo GUI (single core version)."""
    from .Spin_echo_2p_3p_single_core_gui import main

    main()


def launch_shaped_pulse_gui():
    """Launch the advanced shaped pulse explorer GUI."""
    import tkinter as tk

    from .PulseShapedSeq_gui import PulseExplorerGUI

    root = tk.Tk()
    _app = PulseExplorerGUI(root)  # noqa: F841
    root.mainloop()


__all__ = ["launch_basic_gui", "launch_basic_gui_single", "launch_shaped_pulse_gui"]
