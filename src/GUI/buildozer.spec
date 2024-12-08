[app]
title = RoomController
package.name = roomcontroller
package.domain = tzur.apps
android.sdk_path = /home/mepro/Android/Sdk

android.permissions = INTERNET, ACCESS_NETWORK_STATE
source.dir = .
#source.include_exts = py,kv,png,jpg,so
source.include_patterns = modules/*
gradle_opts = -Xmx8g -Xms2g -XX:MaxPermSize=1g -Dfile.encoding=UTF-8
version = 0.2
requirements = python3,kivy,pillow,paho-mqtt==1.6.0
#requirements = ffpyplayer
#android.archs = armeabi-v7a
android.archs = arm64-v8a,armeabi-v7a
orientation = landscape, landscape-reverse
#orientation = portrait