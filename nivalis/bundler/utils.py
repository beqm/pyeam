import platform

def get_system_architecture() -> str:
    arch = platform.machine().lower()
    if arch in ['x86_64', 'amd64']:
        return 'x64'
    elif arch in ['x86', 'i686']:
        return 'x86'
    elif arch == 'arm64':
        return 'arm64'
    else:
        return 'x64'