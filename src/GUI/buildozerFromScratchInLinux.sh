sudo apt -y install autoconf
sudo apt -y install automake
sudo apt -y install libtool
sudo apt -y install build-essentials
sudo apt -y install openjdk-17-jdk
sudo apt -y install unzip
sudo apt -y install zip
sudo apt -y install wget
sudo apt -y install libffi-dev
sudo apt -y install libssl-dev
sudo apt -y install python3
sudo apt -y install python3-dev
sudo apt -y install python3-venv
sudo apt -y install python3-pip

sudo ldconfig

sudo python3 -m venv  --system-site-packages .venvAPK
echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> .venvAPK/bin/activate
echo "export GRADLE_OPTS='-Xmx8g -Dorg.gradle.daemon=true'" >> .venvAPK/bin/activate
echo "export ANDROID_SDK_ROOT=~/Android/Sdk" >> .venvAPK/bin/activate
echo "export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin" >> .venvAPK/bin/activate

source .venvAPK/bin/activate

pip install --upgrade pip
pip install cython
pip install setuptools
pip install buildozer

wget https://dl.google.com/android/repository/commandlinetools-linux-7302050_latest.zip
unzip commandlinetools-linux-7302050_latest.zip
rm commandlinetools-linux-7302050_latest.zip
mkdir -p ~/Android/Sdk/cmdline-tools/latest
mv ./commandlinetools-linux-7302050_latest/* ~/Android/Sdk/cmdline-tools/latest/