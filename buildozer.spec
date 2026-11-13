[app]
title = Crosshair
package.name = crosshair
package.domain = org.ahmed
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy,pyjnius,android
orientation = portrait
fullscreen = 0

android.permissions = SYSTEM_ALERT_WINDOW
android.api = 33
android.minapi = 26
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
