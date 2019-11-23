# Federated-Byzantine-Agreement

## Setup python virtualenv and clone
```
$ python3 -m venv
$ cd simple-fba
$ source bin/activate

$ git clone https://github.com/Iaoouvy/Federated-Byzantine-Agreement.git
$ cd src/fba
$ python setup.py develop
```
## Run

```
$ simulator.py -s
```
To give number of nodes and threshold as arguments (default: nodes = 4 & threshold = 80)

```
$simulator.py -s -nodes 8 -trs 60
```
