# subpulse-analysis

Welcome to subpulse-analysis. For more information, see documentation [subpulse-analysis](chimefrb.github.io/subpulse-analysis)

## Installation

```
git clone git@github.com:CHIMEFRB/subpulse.git
cd subpulse
pip install .
```

## Usage
*subpulse* currently supports a single-thread local execution or a distributed instantiation on the CHIME/FRB Cluster.

### Local

```
subpulse --help
```
```
Usage: subpulse [OPTIONS]

  Run single-thread subpulse analysis.

Options:
  --event INTEGER        CHIME/FRB Event Number  [required]
  --arrivals TEXT        List of TOAs, e.g. '[0.01, 0.002]'   [required]
  --chi FLOAT
  --simulations INTEGER  Number of total simulations to run.
  --fingerprint TEXT     Unique ID for analysis bookeeping.
  --cluster BOOLEAN      If running on the CHIME/FRB Cluster.
  --job INTEGER          Job Identification.
  --debug BOOLEAN        Change logging level to debug.
  --help                 Show this message and exit.
```

### Cluster
```
subpulse-cluster --help
```
```
Usage: subpulse-cluster [OPTIONS]

  Run the subpulse analysis on the CHIME/FRB Cluster.

Options:
  --event INTEGER        CHIME/FRB Event Number  [required]
  --arrivals TEXT        List of TOAs, e.g. '[0.01, 0.002]'   [required]
  --chi FLOAT            [default: 0.0]
  --simulations INTEGER  Number of total simulations to run.
  --jobs INTEGER         Job Identification.
  --help                 Show this message and exit.
```

**NOTE:** For executing a job on the CHIME/FRB Cluster, you need valid `FRB_MASTER_ACCESS_TOKEN` and `FRB_MASTER_REFRESH_TOKEN` environment paramters instantiated in your local environment.

## Example

```
subpulse --event 65777546 --chi 0.2 --simulations 1e6 --arrivals '[0.000, 439.018, 653.038, 1080.966, 1304.422, 1517.858, 1733.211, 1952.779, 2170.596, 2390.536, 2603.326, 3073.348]'
```

## Developer Environment

The recommended to install and develop on *subpulse* is through the *poetry* virtualenv setup.

### Installation

```
cd subpulse/
poetry install
poetry run pre-commit install
```

### Usage

To run commands within the a *poetry* managed virtualenv simply execute,

```
poetry run <command>
```

e.g.
```
poetry run subpulse --help
```
