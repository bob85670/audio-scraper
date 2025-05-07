# Audioscrape

Scrape audio from various websites with a simple command-line interface.

## Usage

First make sure Python is installed, then run:

```sh
pip install audioscrape
```

Then you can use the program as:

```sh
audioscrape "acoustic guitar"
```

See `audioscrape --help` for more details.

### Python API

You can also use the scraper directly in Python, as:

```python
import audioscrape

audioscrape.download(
    query="Cerulean Crayons",
    include=["guitar"],
    exclude=["remix"],
    quiet=True,
)
