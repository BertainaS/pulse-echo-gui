"""
Internationalization (i18n) support for PulseEchoGui.

This module provides translation support for the GUI applications,
allowing users to switch between English and French.
"""

import gettext
import locale
from pathlib import Path
from typing import Optional

# Package directory
PACKAGE_DIR = Path(__file__).parent
LOCALE_DIR = PACKAGE_DIR / "locales"

# Supported languages (currently English only, extensible for future)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "en_US": "English (United States)",
    # Add more languages here in the future:
    # "fr": "Français",
    # "de": "Deutsch",
    # "es": "Español",
}

# Current language (default to English)
_current_language: Optional[str] = None
_translator: Optional[gettext.GNUTranslations] = None


def get_system_language() -> str:
    """
    Detect the system's default language.

    Returns
    -------
    str
        Language code (e.g., 'en', 'fr', 'en_US', 'fr_FR')

    Examples
    --------
    >>> lang = get_system_language()
    >>> print(f"System language: {lang}")
    System language: en_US
    """
    try:
        # Try to get system locale
        system_locale, _ = locale.getdefaultlocale()
        if system_locale:
            # Extract language code (e.g., 'en_US' -> 'en', or keep 'en_US')
            if system_locale in SUPPORTED_LANGUAGES:
                return system_locale
            # Try short code
            lang_code = system_locale.split("_")[0]
            if lang_code in SUPPORTED_LANGUAGES:
                return lang_code
    except Exception:
        pass

    # Default to English
    return "en"


def set_language(lang_code: str) -> bool:
    """
    Set the application language.

    Parameters
    ----------
    lang_code : str
        Language code ('en', 'fr', 'en_US', 'fr_FR')

    Returns
    -------
    bool
        True if language was set successfully, False otherwise

    Examples
    --------
    >>> set_language('fr')
    True
    >>> _('Time')  # Returns French translation
    'Temps'
    """
    global _current_language, _translator

    if lang_code not in SUPPORTED_LANGUAGES:
        # Try short code if full code not found
        short_code = lang_code.split("_")[0]
        if short_code not in SUPPORTED_LANGUAGES:
            print(f"Warning: Language '{lang_code}' not supported, using English")
            lang_code = "en"
        else:
            lang_code = short_code

    try:
        # Load translation catalog
        if lang_code == "en":
            # English is the default, no translation needed
            _translator = None
            _current_language = "en"
            return True

        # Try to load .mo file
        mo_file = LOCALE_DIR / f"{lang_code}_US" / "LC_MESSAGES" / "pulseechogui.mo"
        if not mo_file.exists():
            mo_file = LOCALE_DIR / lang_code / "LC_MESSAGES" / "pulseechogui.mo"

        if mo_file.exists():
            with open(mo_file, "rb") as f:
                _translator = gettext.GNUTranslations(f)
            _current_language = lang_code
            return True
        else:
            print(f"Warning: Translation file not found for '{lang_code}'")
            _translator = None
            _current_language = "en"
            return False

    except Exception as e:
        print(f"Error loading language '{lang_code}': {e}")
        _translator = None
        _current_language = "en"
        return False


def get_current_language() -> str:
    """
    Get the currently active language.

    Returns
    -------
    str
        Current language code

    Examples
    --------
    >>> get_current_language()
    'en'
    """
    return _current_language or "en"


def _(message: str) -> str:
    """
    Translate a message to the current language.

    Parameters
    ----------
    message : str
        Message in English (source language)

    Returns
    -------
    str
        Translated message

    Examples
    --------
    >>> _('Time')
    'Time'
    >>> set_language('fr')
    >>> _('Time')
    'Temps'
    """
    if _translator is None:
        return message
    return _translator.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """
    Translate a message with plural forms.

    Parameters
    ----------
    singular : str
        Singular form in English
    plural : str
        Plural form in English
    n : int
        Number determining which form to use

    Returns
    -------
    str
        Translated message

    Examples
    --------
    >>> ngettext("1 pulse", "{n} pulses", 1).format(n=1)
    '1 pulse'
    >>> ngettext("1 pulse", "{n} pulses", 5).format(n=5)
    '5 pulses'
    """
    if _translator is None:
        return singular if n == 1 else plural
    return _translator.ngettext(singular, plural, n)


# String catalog for GUI translations
# Currently empty - English is the default language
# Add translations here when supporting additional languages:
#
# TRANSLATIONS = {
#     "Time": {"fr": "Temps", "de": "Zeit"},
#     "Signal Amplitude": {"fr": "Amplitude du Signal", "de": "Signalamplitude"},
#     # Add more translations...
# }
TRANSLATIONS = {}


def translate(key: str, lang: Optional[str] = None) -> str:
    """
    Translate a key using the built-in translation dictionary.

    This is a fallback method when gettext catalogs are not available.

    Parameters
    ----------
    key : str
        String to translate (English)
    lang : str, optional
        Target language code (default: current language)

    Returns
    -------
    str
        Translated string

    Examples
    --------
    >>> translate("Time", "fr")
    'Temps'
    >>> translate("Time", "en")
    'Time'
    """
    if lang is None:
        lang = get_current_language()

    if lang == "en":
        return key

    if key in TRANSLATIONS and lang in TRANSLATIONS[key]:
        return TRANSLATIONS[key][lang]

    return key


def list_available_languages() -> dict:
    """
    List all available languages.

    Returns
    -------
    dict
        Dictionary mapping language codes to language names

    Examples
    --------
    >>> langs = list_available_languages()
    >>> print(langs)
    {'en': 'English', 'fr': 'Français', ...}
    """
    return SUPPORTED_LANGUAGES.copy()


# Initialize with system language
_system_lang = get_system_language()
set_language(_system_lang)


if __name__ == "__main__":
    # Test i18n functionality
    print("PulseEchoGui Internationalization Test")
    print("=" * 50)

    print(f"\nSystem language: {get_system_language()}")
    print(f"Current language: {get_current_language()}")

    print("\nAvailable languages:")
    for code, name in list_available_languages().items():
        print(f"  {code}: {name}")

    print("\nTesting translations:")
    print("  Note: Currently only English is supported")
    for test_string in ["Time", "Signal Amplitude", "Echo Delay"]:
        translated = translate(test_string, "en")
        print(f"  {test_string}: {translated}")

    print("\nTesting language switching:")
    print(f"  Current: {get_current_language()}")
    print("  English is the default and only supported language")
    print(f"  Translation of 'Time': {translate('Time')}")
