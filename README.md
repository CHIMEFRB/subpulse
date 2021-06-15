# subpulse-analysis

Welcome to subpulse-analysis. For more information, see documentation [subpulse-analysis](chimefrb.github.io/subpulse-analysis)

## Installation

```
git clone git@github.com:CHIMEFRB/subpulse.git
cd subpulse
poetry install
```

## Usage
*subpulse* currently supports a single-thread local execution, or a distributed instantiation on the CHIME/FRB Cluster.

### Local

```
poetry run subpulse --help
```

### Cluster
```
poetry run subpulse-cluster --help
```

**NOTE:** For executing a job on the CHIME/FRB Cluster, you need valid `FRB_MASTER_ACCESS_TOKEN` and `FRB_MASTER_REFRESH_TOKEN` environment paramters instantiated in your local environment.

## Example

```
poetry run subpulse --event 65777546 --chi 0.2 --simulations 1e6 --arrivals '[0.000, 439.018, 653.038, 1080.966, 1304.422, 1517.858, 1733.211, 1952.779, 2170.596, 2390.536, 2603.326, 3073.348]'
```
