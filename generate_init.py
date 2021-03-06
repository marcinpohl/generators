# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2017-09-09 10:02:28
# @Last Modified 2018-02-28
# @Last Modified time: 2018-02-28 14:30:34

header = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os.path

sys.path.append(os.path.dirname(__file__))

del sys
del os

from performance_tools import runs_per_second as rps
from Generator import Generator

'''

footer = '''
'''

import sys
import os.path
from os import listdir
from functools import partial

script_path = os.path.dirname(__file__)
init_path = os.path.join(script_path, 'generators')

# this builds the full path to a given file in generators
path_of = partial(os.path.join, init_path)

# get all the python files from init_path
gen = (i for i in listdir(init_path) if i.endswith('.py'))
# filter out __init__.py
gen = (i for i in gen if '__init__.py' not in i)
# verify that they all have functions that match the file name
gen = (i for i in gen
       if 'def {}('.format(i[:-3]) in open(path_of(i), 'r').read())
# trim off the .pys
gen = (i[:-3] for i in gen)

# serves as the all that will be injected into __init__
nested_tools = ['inline_tools', 'performance_tools']
__all__ = ['Generator']

# rebuild the __init__
with open(path_of('__init__.py'), 'w') as f:
    print('writing header')
    f.write(header)
    for i in gen:
        __all__.append(i)
        print('adding import for', i)
        f.write('from {i:} import {i:}\n'.format(i=i))
    f.write('\n')
    for i in nested_tools:
        __all__.append(i)
        print('adding nested import for', i)
        f.write('import {}\n'.format(i))
    f.write(footer)
    print('adding __all__')
    f.write('\n__all__ = {}\n'.format(__all__))

print('done')
