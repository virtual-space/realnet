# realnet
## How to run on linux:

The realnet server needs to be configured and running. How to do that can be found in the readme.md for https://github.com/virtual-space/realnet-server/

- Clone out the repo
```
git clone https://github.com/virtual-space/realnet/realnet.git
```

- Go to the repo root folder 
```
cd realnet
```

- In the repo root folder create an .env file with the following content:
```
REALNET_TOKEN=''
```

- run command
```
chmod 700 .env
```

NEED TO RETRIEVE THE REALNET TOKEN. THIS CAN EXPIRE.
`realnet auth token --clientkey='' --clientsecret='' --username='' --password=''`
^realnet token retrieval function

- run the following commands:
```
python3 -m venv venv
. ./venv/bin/activate
python setup.py install
```
- finally to start realnet run the following command:
```
realnet type
```
Choose from 'type', 'item', 'device'.

- python setup.py install notes

You may need to manually install some dependencies. `python setup.py install` should tell you what is missing.

The Cryptography module takes a long time to compile.

Below is an incomplete list of installation instructions for dependencies. If you're not doing this on a fresh installation, you should run `python setup.py install` to see what you need first.

- Inside VENV
Cryptography
```
pip install --upgrade pip
pip install setuptools-rust
```
- Outside VENV
postgreSQL (pg_config is missing)
```
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install postgresql
```
c/c++ compilers (gcc/g++ is missing)
```
sudo apt update
sudo apt install build-essential
```
Optional Man pages
```
sudo apt-get install manpages-dev
```
To test the C & C++ compiler installations run these commands:
```
gcc --version
g++ --version
```
bluetooth dev tools (bluetooth/bluetooth.h is missing)
```
sudo apt-get install libbluetooth-dev
```