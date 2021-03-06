# -*- coding: utf-8 -*-
# @Author: ckochman
# @Date:   2017-05-04 17:06:34
# @Last Modified by:   Cody Kochmann

from os import listdir
from os.path import isfile
from generators import read

readme_header = """
# Generators
Where all of my generator tricks are collected!

## How to install it?

```
pip install generators
```
"""


def get_source(path):
    ''' yields all non-empty lines in a file '''
    for line in read(path):
        if 'import' in line or len(line.strip()) == 0 or line.startswith('#'):
            continue
        if '__name__' in line and '__main__' in line:
            break
        else:
            yield line


# list the directory
gen = ('generators/{}'.format(i) for i in listdir('generators'))
# filter for files only
gen = (i for i in gen if isfile(i))
# filter out __init__.py
gen = (i for i in gen if not '__init__.py' in i)
# filter out pyc's
gen = (i for i in gen if not i.endswith('.pyc'))
# read the lines of each file
gen = (((x for x in get_source(i)), i) for i in gen)

with open('README.md', 'w') as readme:
    readme.write(readme_header + '\n')
    for f, path in gen:
        readme.write('### generators.' + path.split('/')[1].replace('.py','') + '\n```python\n')
        readme.writelines(f)
        readme.write('```\n\n')

with open('README.md') as f:
    print(f.read())
