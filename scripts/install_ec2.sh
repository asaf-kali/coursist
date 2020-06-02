VERSION=3.7.4
VESRION_SHORT=37
VESRION_SHORT_DOT=3.7
VESRION_VERY_SHORT=3

set -e
sudo yum -y update
# Packages needed to compile the python files
sudo yum -y install wget yum-utils gcc openssl-devel bzip2-devel libffi-devel

# Install sqlite3
cd /tmp/
wget https://www.sqlite.org/2020/sqlite-autoconf-3320100.tar.gz
tar -zxvf sqlite-autoconf-3320100.tar.gz && cd sqlite-autoconf-3320100
sudo ./configure && sudo make && sudo make install
sudo mv /usr/bin/sqlite3 /usr/bin/sqlite3.bak
sudo mv sqlite3 /usr/bin/sqlite3

# Install python
wget https://www.python.org/ftp/python/"$VERSION"/Python-"$VERSION".tgz
tar xzf Python-"$VERSION".tgz
cd Python-"$VERSION"
sudo ./configure --enable-optimizations --prefix=/opt/python"$VESRION_SHORT"
sudo make -j "$(nproc)"
sudo make altinstall
sudo rm /tmp/Python-"$VERSION".tgz
sudo ln -s /opt/python"$VESRION_SHORT"/bin/python"$VESRION_SHORT_DOT" /usr/bin/python"$VESRION_VERY_SHORT"
sudo ln -s /opt/python"$VESRION_SHORT"/bin/pip"$VESRION_SHORT_DOT" /usr/bin/pip"$VESRION_VERY_SHORT"
