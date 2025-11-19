# Internationalization (i18n) Files

This directory contains translation infrastructure for PulseEchoGui.

## Current Status

**Language Support**: English only (default)

The internationalization framework is in place and ready for future language additions.

## Structure

```
locales/
├── README.md           # This file
└── en_US/              # English (United States) - default language
    └── LC_MESSAGES/    # Placeholder for future translation files
```

## Using the i18n Framework

### In Python Code

```python
from pulseechogui.i18n import _

# Wrap user-facing strings with _() for future translation support
print(_("Time"))  # Currently returns "Time"
label = _("Signal Amplitude")
```

### In GUI Code

```python
from pulseechogui.i18n import _

# Use _ for all user-facing strings
self.ax.set_xlabel(_('Time'))
self.ax.set_ylabel(_('Signal Amplitude'))
self.ax.set_title(_('2-Pulse Spin Echo Simulation'))
```

## Adding New Languages (Future)

To add support for additional languages:

### Step 1: Update SUPPORTED_LANGUAGES

Edit `pulseechogui/i18n.py`:

```python
SUPPORTED_LANGUAGES = {
    "en": "English",
    "en_US": "English (United States)",
    "fr": "Français",        # Add new language
    "de": "Deutsch",         # Add another
    # etc.
}
```

### Step 2: Add Translations

#### Method A: Using Built-in Dictionary (Simple)

Edit `pulseechogui/i18n.py`:

```python
TRANSLATIONS = {
    "Time": {"fr": "Temps", "de": "Zeit"},
    "Signal Amplitude": {"fr": "Amplitude du Signal", "de": "Signalamplitude"},
    # Add more translations...
}
```

#### Method B: Using gettext (Recommended for Many Strings)

1. **Extract translatable strings**:
   ```bash
   xgettext --language=Python --keyword=_ --output=messages.pot pulseechogui/**/*.py
   ```

2. **Create language .po file**:
   ```bash
   mkdir -p locales/fr_FR/LC_MESSAGES
   msginit --input=messages.pot --locale=fr_FR \
           --output=locales/fr_FR/LC_MESSAGES/pulseechogui.po
   ```

3. **Translate strings** in the .po file:
   ```po
   msgid "Time"
   msgstr "Temps"

   msgid "Signal Amplitude"
   msgstr "Amplitude du Signal"
   ```

4. **Compile to .mo**:
   ```bash
   msgfmt locales/fr_FR/LC_MESSAGES/pulseechogui.po \
          -o locales/fr_FR/LC_MESSAGES/pulseechogui.mo
   ```

### Step 3: Test Translation

```python
from pulseechogui.i18n import set_language, _

set_language('fr')
print(_("Time"))  # Should print "Temps"
```

## Translation Guidelines

### String Formatting

Use Python format strings:

```python
# Good
message = _("Processing {count} files").format(count=n)

# Bad
message = _("Processing ") + str(n) + _(" files")
```

### Context

Provide context for ambiguous strings:

```python
_("File")         # Menu item
_("File Name")    # Input label
_("Save File")    # Button - more specific is better
```

### Plurals

Use ngettext for plurals:

```python
from pulseechogui.i18n import ngettext

msg = ngettext("1 pulse", "{n} pulses", count)
print(msg.format(n=count))
```

## Tools

### Installation

```bash
# Ubuntu/Debian
sudo apt-get install gettext

# macOS
brew install gettext

# Windows
# Download from: https://mlocati.github.io/articles/gettext-iconv-windows.html
```

### Recommended Editors

- **Poedit**: GUI editor for .po files (https://poedit.net/)
- **VS Code**: Extension "gettext" by mrorz
- Any text editor for simple edits

## Contributing Translations

To contribute translations:

1. Fork the repository
2. Add your language following steps above
3. Test translations thoroughly
4. Submit a pull request

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for more details.

## References

- [GNU gettext manual](https://www.gnu.org/software/gettext/manual/)
- [Python gettext documentation](https://docs.python.org/3/library/gettext.html)
- [i18n Best Practices](https://phrase.com/blog/posts/i18n-best-practices/)

## Maintainer

- **English**: Sylvain Bertaina (sylvain.bertaina@cnrs.fr)

---

**Note**: The i18n framework is ready for expansion, but currently only English is supported.
