import collections
import re
import zlib
import aiohttp

from public import public

from .. import enums

@public
class Translator(collections.abc.MutableMapping):
    TRANSLATIONS_URL_FMT = "https://www.transformice.com/langues/tfm-{language}.gz"

    # Starts with '$', is at least one character long, and is ended by several
    # characters, namely whitespace, Additionally the captured text could be
    # wrapped in braces.
    NESTED_TRANSLATION_KEY_PATTERN = re.compile(r"\$(\{[^(){}[\]<>$\s,]+\}|[^(){}[\]<>$\s,]+)")

    NESTED_TRANSLATION_REMOVED_CHARS_PATTERN = re.compile(r"\{|\}|\$|trad#")

    NESTED_TRANSLATION_ARG_PATTERN = re.compile(r"%\d+")

    NESTED_TRANSLATION_ESCAPE_CHARS_PATTERN = re.compile(r"[-\/\\^$*+?.()|[\]{}]")

    GENDER_PATTERN = re.compile(r"\((.*?)\|(.*?)\)")

    def __init__(self, translations):
        self._translations = translations

    @classmethod
    async def download(cls, language):
        async with aiohttp.ClientSession() as session:
            async with session.get(cls.TRANSLATIONS_URL_FMT.format(language=language)) as response:
                data = zlib.decompress(await response.read()).decode("utf-8")

                data = data.split("\n-\n")
                data = [entry.split("=", 1) for entry in data if len(entry) != 0]

                return cls({
                    pair[0]: pair[1]

                    for pair in data if len(pair) > 1
                })

    def _nested_translate(self, translated_tracker, capture, args):
        if translated_tracker is not None:
            if capture in translated_tracker:
                return None, None

            translated_tracker[capture] = True

        real_key = self.NESTED_TRANSLATION_REMOVED_CHARS_PATTERN.sub("", capture)

        local_result    = self.get(real_key, default=capture)
        num_format_args = sum(1 for _ in self.NESTED_TRANSLATION_ARG_PATTERN.finditer(local_result))

        for i, arg in enumerate(args):
            if i >= num_format_args:
                break

            local_result = arg.join(local_result.split(f"%{i + 1}"))

        return local_result, num_format_args

    def translate(self, key, *args, gender=enums.Gender.Unknown):
        # NOTE: This could potentially result in different
        # string representations than Actionscript would
        # give, particularly for booleans. For now we choose
        # not to care.
        args = [str(arg) for arg in args]

        if key.rfind("$") == 0 and " " not in key and "\n" not in key:
            result = self.get(key[1:], default=key)

            for i, arg in enumerate(args):
                result = arg.join(result.split(f"%{i + 1}"))
        else:
            result = key

            translated_tracker = {} if len(args) == 0 else None
            for capture in self.NESTED_TRANSLATION_KEY_PATTERN.finditer(result):
                try:
                    # Get the captured string out of the match object.
                    capture = capture[0]

                    local_result, num_format_args = self._nested_translate(translated_tracker, capture, args)
                    if local_result is None:
                        continue

                    args = args[:num_format_args]

                    # If we started with no arguments.
                    if translated_tracker is not None:
                        # Escape certain characters and treat the capture as a regex.
                        result = re.sub(self.NESTED_TRANSLATION_ESCAPE_CHARS_PATTERN.sub(lambda m: "\\" + m[0], capture), local_result, result)
                    else:
                        result = result.replace(capture, local_result)

                except Exception:
                    return result

            # Deal with remnant arguments.
            num_format_args = sum(1 for _ in self.NESTED_TRANSLATION_ARG_PATTERN.finditer(result))
            for i, arg in enumerate(args):
                if i >= num_format_args:
                    break

                result = arg.join(result.split(f"%{i + 1}"))

        if "|" in result:
            if gender is enums.Gender.Feminine:
                repl = lambda m: m[2]
            else:
                repl = lambda m: m[1]

            result = self.GENDER_PATTERN.sub(repl, result)

        return result

    def __repr__(self):
        return f"{type(self).__qualname__}({repr(self._translations)})"

    # NOTE: Below are methods for 'MutableMapping' which
    # just forward on to the '_translations' attribute.

    def __getitem__(self, key):
        return self._translations[key]

    def __setitem__(self, key, value):
        self._translations[key] = value

    def __delitem__(self, key):
        del self._translations[key]

    def __iter__(self):
        return iter(self._translations)

    def __len__(self):
        return len(self._translations)

    def keys(self):
        return self._translations.keys()

    def values(self):
        return self._translations.values()

    def items(self):
        return self._translations.items()

    def get(self, key, default=None):
        return self._translations.get(key, default)

    def pop(self, key):
        return self._translations.pop(key)

    def popitem(self):
        return self._translations.popitem()

    def clear(self):
        self._translations.clear()

    def update(self, other=(), /, **kwargs):
        self._translations.update(other, **kwargs)

    def setdefault(self, key, default=None):
        return self._translations.setdefault(key, default)

    def __contains__(self, key):
        return key in self._translations

    def __eq__(self, other):
        if not isinstance(other, Translator):
            return NotImplemented

        return self._translations == other._translations

    def __ne__(self, other):
        if not isinstance(other, Translator):
            return NotImplemented

        return self._translations != other._translations
