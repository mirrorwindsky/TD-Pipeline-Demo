"""Optional Windows credential storage; no keys are written to project files."""
import ctypes
from ctypes import wintypes
from dataclasses import dataclass, field
import sys

PROVIDERS = {"OpenAI", "DeepSeek"}


class CredentialError(ValueError):
    pass


def checked_key(value):
    key = value.strip()
    if len(key) > 2560 or any(ord(char) < 33 or ord(char) > 126 for char in key):
        raise CredentialError("Invalid API key: paste the key only, without spaces or line breaks")
    return key


class _Credential(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)), ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR),
    ]


class WindowsCredentialStore:
    available = sys.platform == "win32"

    def __init__(self, namespace="TD-Pipeline-Demo/AI"):
        self.namespace = namespace
        self._library = None

    def _target(self, provider):
        if provider not in PROVIDERS:
            raise CredentialError("Unknown AI provider")
        return f"{self.namespace}/{provider}"

    def _api(self):
        if not self.available:
            raise CredentialError("Remembering keys is supported on Windows only")
        if self._library is None:
            try:
                api = ctypes.WinDLL("advapi32.dll", use_last_error=True)
                pointer = ctypes.POINTER(_Credential)
                api.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(pointer)]
                api.CredWriteW.argtypes = [pointer, wintypes.DWORD]
                api.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
                for name in ("CredReadW", "CredWriteW", "CredDeleteW"):
                    getattr(api, name).restype = wintypes.BOOL
                api.CredFree.argtypes = [ctypes.c_void_p]
                api.CredFree.restype = None
                self._library = api
            except OSError:
                raise CredentialError("Windows Credential Manager is unavailable") from None
        return self._library

    def read(self, provider):
        target = self._target(provider)
        if not self.available:
            return None
        api = self._api()
        pointer = ctypes.POINTER(_Credential)()
        if not api.CredReadW(target, 1, 0, ctypes.byref(pointer)):
            if ctypes.get_last_error() == 1168:  # ERROR_NOT_FOUND
                return None
            raise CredentialError("Cannot read saved API key; you can enter a session key")
        try:
            blob = ctypes.string_at(pointer.contents.CredentialBlob, pointer.contents.CredentialBlobSize)
            return checked_key(blob.decode("utf-8"))
        except UnicodeError:
            raise CredentialError("Saved API key is invalid; remove it and enter a new key") from None
        finally:
            api.CredFree(pointer)

    def write(self, provider, value):
        target = self._target(provider)
        key = checked_key(value)
        if not key:
            raise CredentialError("Enter an API key before remembering it")
        blob = key.encode("utf-8")
        buffer = (ctypes.c_ubyte * len(blob)).from_buffer_copy(blob)
        credential = _Credential()
        credential.Type = 1  # CRED_TYPE_GENERIC
        credential.TargetName = target
        credential.UserName = provider
        credential.CredentialBlobSize = len(blob)
        credential.CredentialBlob = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
        credential.Persist = 2  # Same Windows user, this computer; no roaming.
        try:
            if not self._api().CredWriteW(ctypes.byref(credential), 0):
                raise CredentialError("Cannot save API key; session use is still available")
        finally:
            ctypes.memset(buffer, 0, len(blob))

    def delete(self, provider):
        target = self._target(provider)
        if not self.available:
            return
        if not self._api().CredDeleteW(target, 1, 0) and ctypes.get_last_error() != 1168:
            raise CredentialError("Cannot remove saved API key")


@dataclass
class KeyProfile:
    key: str = field(default="", repr=False)
    remember: bool = False


class KeySettings:
    def __init__(self, store=None):
        self.store = store if store is not None else WindowsCredentialStore()
        self.profiles = {}

    def get(self, provider):
        if provider not in PROVIDERS:
            return KeyProfile()
        if provider not in self.profiles:
            self.profiles[provider] = KeyProfile()
            key = self.store.read(provider)
            self.profiles[provider] = KeyProfile(key or "", bool(key))
        return self.profiles[provider]

    def edit(self, provider, key, remember):
        if provider in PROVIDERS:
            self.profiles[provider] = KeyProfile(key, remember)

    def apply(self, provider, key, remember):
        key = checked_key(key)
        if remember:
            self.store.write(provider, key)
        else:
            self.store.delete(provider)
        self.profiles[provider] = KeyProfile(key, remember)

    def forget(self, provider):
        self.store.delete(provider)
        self.profiles[provider] = KeyProfile()
