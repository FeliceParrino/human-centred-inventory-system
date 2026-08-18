import os


def configure_pdf_native_libraries():
    homebrew_lib = '/opt/homebrew/lib'
    current_path = os.environ.get('DYLD_LIBRARY_PATH', '')

    if os.path.exists(homebrew_lib) and homebrew_lib not in current_path.split(':'):
        os.environ['DYLD_LIBRARY_PATH'] = (
            f'{homebrew_lib}:{current_path}' if current_path else homebrew_lib
        )
