# SCMeTA

SCMeTA is a python library of single-cell meta-analysis tools. It provides a set of functions for single-cell meta-analysis, including data integration, batch effect correction, cell type annotation, cell clustering, cell trajectory inference, and cell type marker identification. It also provides a set of functions for single-cell data visualization, including dimension reduction, cell clustering, cell trajectory inference, and cell type marker identification. 

## Installation

SCMeTA is available on PyPI and can be installed with pip:

```bash
pip install scmeta
```

## Usage

### Data integration

```python

from SCMeTA import Process

sc = Process()

# Load data

sc.load("data/example.RAW")

# Data process

sc.pre_process()
sc.process()
sc.post_process()

```

## Documentation

The official documentation is hosted on Read the Docs: https://sc-meta.com/

## License

SCMeTA is licensed under the GPLv3 license. See the LICENSE file for more details.


