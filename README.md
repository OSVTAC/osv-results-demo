# osv-results-demo

Contains example demonstrations of OSVTAC's results reporter component

The demos are published here: https://osvtac.github.io/osv-results-demo/

## Developer Instructions

To get started:

```
$ git clone git@github.com:OSVTAC/osv-results-demo.git
$ cd osv-results-demo/
$ git submodule init
$ git submodule update
```

Make sure you are using Python 3.6.  Then, preferably from a fresh
Python virtual environment:

```
$ pip install -e submodules/osv-results-reporter/src/
```

You should now be able to run the results reporter, e.g.:

```
orr -h
```

To regenerate the samples:

```
$ ./generate.sh
```

Then commit and push the changes.
