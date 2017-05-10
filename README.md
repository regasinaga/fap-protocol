# fap-protocol
This is the final project from my Protocol Engineering class. This protocol is implemented above TCP layer.

## Getting Started

### Prerequisites
* Python3
* MongoDB
* pymongo (Python library for mongo db)

### Linux
if you are using fap-protocol server in linux, first do

``` 
sudo apt-get update
```
and then install mongodb
```
sudo apt-get install mongo-server
```
next install pymongo
```
sudo pip3 install pymongo
```

### Windows

install pymongo
```
pip install pymongo
```
## Running

### Linux

you have to set executing access for client
```
cd client
chmod +x client.sh
```
and server
```
cd client
chmod +x mongox.sh
chmod +x server.sh
```

### Windows

Just run theses in order
```
mongox.bat
server.bat
client.bat
```



