# MyStudent Buildozer Configuration
[app]

# (str) Title of your application
title = MyStudent

# (str) Package name
package.name = mystudent

# (str) Package domain (needed for android packaging)
package.domain = org.mystudent.app

# (str) Application version
version = 1.0.0

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,ttf,json

# (list) List of requirements
# Note: we need openssl for HTTPS (Firebase) and arabic-reshaper/python-bidi for Arabic
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,requests,urllib3,certifi,openssl,arabic-reshaper,python-bidi

# (str) Custom source folders for requirements
# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android architecture to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) indicates if the application should be fullscreen or not
fullscreen = 0

# (list) list of service to declare
# (str) Orientation (portrait, landscape or all)
orientation = portrait

# (str) Adaptive icon of the application (used if Android API level is 26+)
# icon.filename = %(source.dir)s/assets/icon.png

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/assets/splash.png

# (bool) If True, then skip the acknowledgement of the Android SDK license
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = no, 1 = yes)
warn_on_root = 1
