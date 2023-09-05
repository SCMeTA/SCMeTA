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

from SCMeTA import SCProcess

sc = SCProcess()

# Load data

sc.load("data/pancreas.RAW")

# Data process

sc.pre_process()
sc.process()
sc.post_process()

```


