
# Generators
Where all of my generator tricks are collected!

## How to install it?

```
pip install generators
```

### generators.iter_kv
```python
@noglobals
def iter_kv(d):
    ''' This iterates through massive dictionaries without the slowdown and memory usage of
    dict.items. Python 3 does provide an iterable dict.items but using this instead gives you
    uniform behavior in both versions of python '''
    for k in d:
        yield k, d[k]
del noglobals
```

### generators.tee
```python
del print_function
@noglobals
def tee(pipeline, name, output_function=print):
    for i in pipeline:
        output_function('{} - {}'.format(name,i))
        yield i
del noglobals
```

### generators.all_subslices
```python
sys.path.append(os.path.dirname(__file__))
del sys
del os
@strict_globals(iterable=iterable, islice=islice, deque=deque)
def all_subslices(itr):
    """ generates every possible slice that can be generated from an iterable """
    assert iterable(itr), 'generators.all_subslices only accepts iterable arguments, not {}'.format(itr)
    if not hasattr(itr, '__len__'): # if itr isnt materialized, make it a deque
        itr = deque(itr)
    len_itr = len(itr)
    for start,_ in enumerate(itr):
        d = deque()
        for i in islice(itr, start, len_itr): # how many slices for this round
            d.append(i)
            yield tuple(d)
del iterable
del islice
del deque
del strict_globals
```

### generators.iterable
```python
@noglobals
def iterable(target):
    ''' returns true if the given argument is iterable '''
    if any(i in ('next', '__next__', '__iter__') for i in dir(target)):
        return True
    else:
        try:
            iter(target)
            return True
        except:
            return False
del noglobals
```

### generators.itemgetter
```python
@strict_globals(deque=deque, itemgetter=itemgetter)
def itemgetter(iterable, indexes):
    ''' same functionality as operator.itemgetter except, this one supports
        both positive and negative indexing of generators as well '''
    assert type(indexes)==tuple, 'indexes needs to be a tuple of ints'
    assert all(type(i)==int for i in indexes), 'indexes needs to be a tuple of ints'
    positive_indexes=[i for i in indexes if i>=0]
    negative_indexes=[i for i in indexes if i<0]
    out = {}
    if len(negative_indexes):
        # if there are any negative indexes
        negative_index_buffer = deque(maxlen=min(indexes)*-1)
        for i,x in enumerate(iterable):
            if i in positive_indexes:
                out[i]=x
            negative_index_buffer.append(i)
        out.update({ni:negative_index_buffer[ni] for ni in negative_indexes})
    else:
        # if just positive results
        out.update({i:x for i,x in enumerate(iterable) if i in positive_indexes})
    return itemgetter(*indexes)(out)
del deque, strict_globals
```

### generators.window
```python
@strict_globals(deque=deque)
def window(iterable, size):
    ''' yields wondows of a given size '''
    d = deque(maxlen=size)
    # normalize iterable into a generator
    iterable = (i for i in iterable)
    # fill d until full
    for i in iterable:
        d.append(i)
        if len(d) == size:
            break
    if len(d) == d.maxlen:
        # yield the windows
        for i in iterable:
            yield tuple(d)
            d.append(i)
        yield tuple(d)
del deque, strict_globals
```

### generators.inline_tools
```python
_print = print
del print_function
__all__ = 'asserts', 'print', 'attempt'
@strict_globals(getsource=getsource)
def asserts(input_value, rule, message=''):
    """ this function allows you to write asserts in generators since there are
        moments where you actually want the program to halt when certain values
        are seen.
    """
    assert callable(rule) or type(rule)==bool, 'asserts needs rule to be a callable function or a test boolean'
    assert isinstance(message, str), 'asserts needs message to be a string'
    # if the message is empty and rule is callable, fill message with rule's source code
    if len(message)==0 and callable(rule):
        try:
            s = getsource(rule).splitlines()[0].strip()
        except:
            s = repr(rule).strip()
        message = 'illegal input of {} breaks - {}'.format(input_value, s)
    if callable(rule):
        # if rule is a function, run the function and assign it to rule
        rule = rule(input_value)
    # now, assert the rule and return the input value
    assert rule, message
    return input_value
del getsource
@strict_globals(_print=_print)
def print(*a):
    """ print just one that returns what you give it instead of None """
    try:
        _print(*a)
        return a[0] if len(a) == 1 else a
    except:
        _print(*a)
del _print
@noglobals
def attempt(fn, default_output=None):
    ''' attempt running a function in a try block without raising exceptions '''
    assert callable(fn), 'generators.inline_tools.attempt needs fn to be a callable function'
    try:
        return fn()
    except:
        return default_output
del strict_globals, noglobals
```

### generators.chain
```python
@strict_globals(partial=partial)
def chain(*args):
    """itertools.chain, just better"""
    has_iter = partial(hasattr, name='__iter__')
    # check if a single iterable is being passed for
    # the case that it's a generator of generators
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        args = args[0]
    for arg in args:
        # if the arg is iterable
        if hasattr(arg, '__iter__'):
            # iterate through it
            for i in arg:
                yield i
        # otherwise
        else:
            # yield the whole argument
            yield arg
del partial
del strict_globals
```

### generators.all_substrings
```python
@strict_globals(window=window)
def all_substrings(s):
    ''' yields all substrings of a string '''
    join = ''.join
    for i in range(1, len(s) + 1):
        for sub in window(s, i):
            yield join(sub)
del window
del strict_globals
```

### generators.timer
```python
@started
@strict_globals(ts=ts)
def timer():
    """ generator that tracks time """
    start_time = ts()
    while 1:
        yield ts()-start_time
del ts, started, strict_globals
```

### generators.fork
```python
@noglobals
def fork(iterate, forks=2):
    """ use this to fork a generator """
    return ((i,)*forks for i in iterate)
del noglobals
```

### generators.side_task
```python
del print_function
sys.path.append(os.path.dirname(__file__))
del sys
del os
@strict_globals(map=map, iterable=iterable)
def side_task(pipe, *side_jobs):
    ''' allows you to run a function in a pipeline without affecting the data '''
    # validate the input
    assert iterable(pipe), 'side_task needs the first argument to be iterable'
    for sj in side_jobs:
        assert callable(sj), 'all side_jobs need to be functions, not {}'.format(sj)
    # add a pass through function to side_jobs
    side_jobs = (lambda i:i ,) + side_jobs
    # run the pipeline
    for i in map(pipe, *side_jobs):
        yield i[0]
del iterable, strict_globals
```

### generators.timed_pipe
```python
@strict_globals(ts=ts)
def timed_pipe(generator, seconds=3):
    ''' This is a time limited pipeline. If you have a infinite pipeline and
        want it to stop yielding after a certain amount of time, use this! '''
    # grab the highest precision timer
    # when it started
    start = ts()
    # when it will stop
    end = start + seconds
    # iterate over the pipeline
    for i in generator:
        # if there is still time
        if ts() < end:
            # yield the next item
            yield i
        # otherwise
        else:
            # stop
            break
del ts, strict_globals
```

### generators.map
```python
"""
what does map do
- run first argument (the function) against the input iterables
- if multiple iterables are defined, multiple inputs are required for the function
what does our map do
- run multi-ops if multiple functions are given
- run window or chunks if multiple args in function
"""
@noglobals
def function_arg_count(fn):
    """ returns how many arguments a funciton has """
    assert callable(fn), 'function_arg_count needed a callable function, not {0}'.format(repr(fn))
    if hasattr(fn, '__code__') and hasattr(fn.__code__, 'co_argcount'):
        return fn.__code__.co_argcount
    else:
        return 1 # not universal, but for now, enough... :/
@strict_globals(function_arg_count=function_arg_count, multi_ops=multi_ops, window=window)
def map(*args):
    """ this map works just like the builtin.map, except, this one you can also:
        - give it multiple functions to map over an iterable
        - give it a single function with multiple arguments to run a window
          based map operation over an iterable
    """
    functions_to_apply = [i for i in args if callable(i)]
    iterables_to_run = [i for i in args if not callable(i)]
    #print('functions_to_apply:',functions_to_apply)
    #print('iterables_to_run:',iterables_to_run)
    assert len(functions_to_apply)>0, 'at least one function needs to be given to map'
    assert len(iterables_to_run)>0, 'no iterables were given to map'
    # check for native map usage
    if len(functions_to_apply) == 1 and len(iterables_to_run) >= 1 and function_arg_count(*functions_to_apply)==1:
        if hasattr(iter([]), '__next__'): # if python 3
            return __builtins__.map(functions_to_apply[0], *iterables_to_run)
        else:
            return iter(__builtins__.map(functions_to_apply[0], *iterables_to_run))
    # ---------------------------- new logic below ----------------------------
    # logic for a single function
    elif len(functions_to_apply) == 1:
        fn = functions_to_apply[0]
        # if there is a single iterable, chop it up
        if len(iterables_to_run) == 1:
            return (fn(*i) for i in window(iterables_to_run[0], function_arg_count(functions_to_apply[0])))
    # logic for more than 1 function
    elif len(functions_to_apply) > 1 and len(iterables_to_run) == 1:
        return multi_ops(*(iterables_to_run + functions_to_apply))
    else:
        raise ValueError('invalid usage of map()')
del function_arg_count, window, multi_ops, noglobals, strict_globals
```

### generators.total
```python
@started
@noglobals
def total():
    "generator that holds a total"
    total = 0
    while 1:
        total += yield total
del started, noglobals
```

### generators.multi_ops
```python
@noglobals
def multi_ops(data_stream, *funcs):
    """ fork a generator with multiple operations/functions
        data_stream  -  an iterable data structure (ie: list/generator/tuple)
        funcs        -  every function that will be applied to the data_stream """
    assert all(callable(func) for func in funcs), 'multi_ops can only apply functions to the first argument'
    assert len(funcs), 'multi_ops needs at least one function to apply to data_stream'
    for i in data_stream:
        if len(funcs) > 1:
            yield tuple(func(i) for func in funcs)
        elif len(funcs) == 1:
            yield funcs[0](i)
del noglobals
```

### generators.performance_tools
```python
del print_function
__all__ = 'cpu_time', 'time_pipeline', 'runs_per_second'
if hasattr(iter([]), 'next'): # only python2
    def _cpu_time(rusage):
        ''' just like python3's time.process_time :
            Process time for profiling: sum of the kernel and user-space CPU time.
        '''
        usage = rusage()
        return usage.ru_utime + usage.ru_stime
    # i used a nested partial because access to the arguments is
    # faster than doing global lookups and I didn't want to allow
    # access to manipulate that variable so a partial hid it.
    #
    # for those who agree that the code below is ugly, this is
    # pretty much optimizing this call into cpu_time:
    #
    #   _cpu_time(getrusage(RUSAGE_SELF))
    #
    cpu_time = partial(_cpu_time, partial(getrusage, RUSAGE_SELF))
    # clean up the namespace
    del _cpu_time, partial, getrusage, RUSAGE_SELF
else: # only python3
@strict_globals(ts=ts, getsource=getsource)
def time_pipeline(iterable, *steps):
    ''' this times the steps in a pipeline.
        give it an iterable to test against
        followed by the steps of the pipeline
        seperated in individual functions.
    '''
    if callable(iterable):
        try:
            iter(iterable())
            callable_base = True
        except:
            raise TypeError('time_pipeline needs the first argument to be an iterable or a function that produces an iterable.')
    else:
        try:
            iter(iterable)
            callable_base = False
        except:
            raise TypeError('time_pipeline needs the first argument to be an iterable or a function that produces an iterable.')
    # if iterable is not a function, load the whole thing
    # into a list so it can be ran over multiple times
    if not callable_base:
        iterable = tuple(iterable)
    # these store timestamps for time calculations
    durations = []
    results = []
    for i,_ in enumerate(steps):
        current_tasks = steps[:i+1]
        #print('testing',current_tasks)
        duration = 0.0
        # run this test x number of times
        for t in range(100000):
            # build the generator
            test_generator = iter(iterable()) if callable_base else iter(iterable)
            # time its execution
            start = ts()
            for task in current_tasks:
                test_generator = task(test_generator)
            for i in current_tasks[-1](test_generator):
                pass
            duration += ts() - start
        durations.append(duration)
        if len(durations) == 1:
            results.append(durations[0])
            #print(durations[0],durations[0])
        else:
            results.append(durations[-1]-durations[-2])
            #print(durations[-1]-durations[-2],durations[-1])
    #print(results)
    #print(durations)
    assert sum(results) > 0
    resultsum = sum(results)
    ratios = [i/resultsum for i in results]
    #print(ratios)
    for i in range(len(ratios)):
        try:
            s = getsource(steps[i]).splitlines()[0].strip()
        except:
            s = repr(steps[i]).strip()
        print('step {} | {:2.4f}s | {}'.format(i+1, durations[i], s))
@strict_globals(ts=ts)
def runs_per_second(generator, seconds=3):
    ''' use this function as a profiler for both functions and generators
    to see how many iterations or cycles they can run per second '''
    assert type(seconds) is int, 'runs_per_second needs seconds to be an int, not {}'.format(repr(seconds))
    assert seconds>0, 'runs_per_second needs seconds to be positive, not {}'.format(repr(seconds))
    # if generator is a function, turn it into a generator for testing
    if callable(generator) and not any(i in ('next', '__next__', '__iter__') for i in dir(generator)):
        try:
            # get the output of the function
            output = generator()
        except:
            # if the function crashes without any arguments
            raise Exception('runs_per_second needs a working function that accepts no arguments')
        else:
            # this usage of iter infinitely calls a function until the second argument is the output
            # so I set the second argument to something that isnt what output was.
            generator = iter(generator, (1 if output is None else None))
            del output
    c=0  # run counter, keep this one short for performance reasons
    entire_test_time_used = False
    start = ts()
    end = start+seconds
    for _ in generator:
        if ts()>end:
            entire_test_time_used = True
            break
        else:
            c += 1
    duration = (ts())-start  # the ( ) around ts ensures that it will be the first thing calculated
    return int(c/(seconds if entire_test_time_used else duration))
del getsource, noglobals, strict_globals
```

### generators.loop
```python
@strict_globals(cycle=cycle)
def loop():
    '''
    use this for infinite iterations with
        for _ in loop():
    instead of:
        while True:
    to get a free speedup in loops.
    '''
    return cycle({0})
del cycle, strict_globals
```

### generators.just
```python
@strict_globals(cycle=cycle)
def just(*args):
    ''' this works as an infinite loop that yields
        the given argument(s) over and over
    '''
    assert len(args) >= 1, 'generators.just needs at least one arg'
    if len(args) == 1: # if only one arg is given
        try:
            # try to cycle in a set for iteration speedup
            return cycle(set(args))
        except:
            # revert to cycling args as a tuple
            return cycle(args)
    else:
        return cycle({args})
del cycle, strict_globals
```

### generators.started
```python
@strict_globals(wraps=wraps)
def started(generator_function):
    """ starts a generator when created """
    @wraps(generator_function)
    def wrapper(*args, **kwargs):
        g = generator_function(*args, **kwargs)
        next(g)
        return g
    return wrapper
del strict_globals, wraps
```

### generators.average
```python
@started
@strict_globals(total=total)
def average():
    """ generator that holds a rolling average """
    count = 0
    total = total()
    i=0
    while 1:
        i = yield ((total.send(i)*1.0)/count if count else 0)
        count += 1
del total
del started
del strict_globals
```

### generators.unfork
```python
@noglobals
def unfork(g):
    """ returns a generator with one output at a time if
        multiple outputs are coming out of the given """
    for i in g:
        for x in i:
            yield x
del noglobals
```

### generators.iter_csv
```python
@strict_globals(DictReader=DictReader)
def iter_csv(path, mode='r'):
    with open(path, mode) as f:
        for row in DictReader(f):
            yield dict(row)
del DictReader, strict_globals
```

### generators.counter
```python
@started
@noglobals
def counter():
    "generator that holds a sum"
    c = 0
    while 1:
        yield c
        c += 1
del started
del noglobals
```

### generators.chunks
```python
@strict_globals(deque=deque)
def chunks(stream, chunk_size, output_type=tuple):
    ''' returns chunks of a stream '''
    if callable(chunk_size):
        ''' chunk_size is acting as a separator function '''
        seperator = chunk_size
        chunk = deque()
        for i in stream:
            if seperator(i) and len(chunk):
                yield output_type(chunk)
                chunk.clear()
            chunk.append(i)
    else:
        chunk = deque(maxlen=chunk_size)
        for i in stream:
            chunk.append(i)
            if len(chunk) == chunk_size:
                yield output_type(chunk)
                chunk.clear()
    if len(chunk):
        yield output_type(chunk)
del deque
del strict_globals
```

### generators.early_warning
```python
@strict_globals(warning=warning)
def early_warning(iterable, name='this generator'):
    ''' This function logs an early warning that the generator is empty.
    This is handy for times when you're manually playing with generators and
    would appreciate the console warning you ahead of time that your generator
    is now empty, instead of being surprised with a StopIteration or
    GeneratorExit exception when youre trying to test something. '''
    nxt = None
    prev = next(iterable)
    while 1:
        try:
            nxt = next(iterable)
        except:
            warning(' {} is now empty'.format(name))
            yield prev
            break
        else:
            yield prev
            prev = nxt
del warning
del strict_globals
```

### generators.read
```python
@strict_globals(partial=partial)
def read_with_seperator(f, seperator, stop_value):
    assert hasattr(f, 'read')
    assert isinstance(stop_value, str)
    assert isinstance(seperator, str)
    assert len(seperator)
    out = stop_value
    for i in iter(partial(f.read, 1), stop_value):
        out += i
        if seperator in out:
            yield out
            out = stop_value
@strict_globals(partial=partial, stdin=stdin, read_with_seperator=read_with_seperator)
def read(path='', mode='r', record_size=None, record_seperator=None, offset=0, autostrip=False):
    ''' instead of writing open('file').read(), this is much more efficient and has some extra goodies '''
    assert isinstance(path, str), 'path needs to be a string, not: {}'.format(repr(path))
    assert isinstance(mode, str), 'mode needs to be a string, not: {}'.format(repr(mode))
    assert ((record_size is None)+(record_seperator is None))>0 , 'generators.read does not support both record_seperator and record_size options being used at the same time: {} {}'.format(record_size, record_seperator)
    assert record_size is None or type(record_size) is int, 'record_size can only be defined as an int, not: {}'.format(repr(record_size))
    assert record_seperator is None or isinstance(record_seperator, str) and len(record_seperator), 'record_seperator can only be defined as a non-empty string, not: {}'.format(repr(record_seperator))
    assert type(offset) == int and offset>=0, 'offset needs to be a positive int, not: {}'.format(repr(offset))
    assert type(autostrip) == bool, 'autostrip needs to be a boolean, not: {}'.format(repr(autostrip))
    stop_value = b'' if mode == 'rb' else ''
    if autostrip:
        autostrip = lambda i:i.strip()
    else:
        autostrip = lambda i:i
    if path=='': # if path is empty, use stdin
        if record_seperator is None:
            for line in stdin:
                yield autostrip(line)
        else:
            for entry in read_with_seperator(stdin, record_seperator, stop_value):
                yield autostrip(entry)
    else: # otherwise, open path
        with open(path, mode) as f:
            if record_size is None and record_seperator is None:  # no record_size or record_seperator? iterate over lines
                for line in f:
                    if offset > 0: # offset in line reading mode offsets per each line
                        offset -= 1
                    else:
                        yield autostrip(line)
            elif record_seperator is not None:
                f.seek(offset)
                for record in read_with_seperator(f, record_seperator, stop_value):
                    yield autostrip(record)
            else:  # if record_size is specified, iterate over records at that size
                f.seek(offset)
                for record in iter(partial(f.read, record_size), stop_value):
                    yield autostrip(record)
        # before this generator raises StopIteration, it will
        # close the file since we are using a context manager.
del partial, stdin, strict_globals, read_with_seperator
```

