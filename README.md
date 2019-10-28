# osv-results-demo

[![Build Status](https://travis-ci.org/OSVTAC/osv-results-demo.svg?branch=master)](https://travis-ci.org/OSVTAC/osv-results-demo)

Contains example demonstrations of OSVTAC's
[results reporter](https://github.com/OSVTAC/osv-results-reporter) component.

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
$ orr -h
```

To regenerate the samples, run the following from the repo root using
Python 3.6:

```
$ python generate.py
```

(For help, pass `-h`: `python generate.py -h`)

Then commit and push the changes.


## Copyright

Copyright (C) 2019  Carl Hage

Copyright (C) 2019  Chris Jerdonek


## License

This file is part of Open Source Voting Results Demo (ORD).

ORD is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


## Contact

The authors can be reached at--

* Carl Hage <ch@carlhage.com>
* Chris Jerdonek <chris.jerdonek@gmail.com>
