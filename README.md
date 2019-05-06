# Generators

[![Downloads](https://pepy.tech/badge/generators)](https://pepy.tech/project/generators)
[![Downloads](https://pepy.tech/badge/generators/month)](https://pepy.tech/project/generators)
[![Downloads](https://pepy.tech/badge/generators/week)](https://pepy.tech/project/generators)

Where all of my generator tricks are collected!

## How to install it?

```
pip install --upgrade generators
```

## What is Generators?

`generators` is a library for high performance pure Python pipeline processing

## Examples

### Full, practical examples  #MP I'd move it out out of quickstart

Each of these scripts took 5-10 minutes a piece to write and show how flexible the generators library is.

- [parse_local_dns.py](https://github.com/CodyKochmann/generators/blob/master/examples/parse_local_dns.py) - generate a dict of host:ip pairs from parsing /etc/hosts
- [scrape_urls.py](https://github.com/CodyKochmann/generators/blob/master/examples/scrape_urls.py) - parse html to extract all urls from a webpage with no scraping libraries
- [tail.py](https://github.com/CodyKochmann/generators/blob/master/examples/tail.py) - lightweight iterator that `tail`s a file just like GNU `tail`

### Easy Snippets

#### Streaming Math Operations

##### Rolling mean

```python
In [1]: from statistics import mean

In [2]: from generators import Generator as G

In [3]: G(range(10)).window(5).map(mean).to(list)
Out[3]: [2, 3, 4, 5, 6, 7]

In [4]: # Use print to peek at a mean executed over a 5 element slice ('window')

In [5]: G(range(10)).window(5).print('window ').map(mean).print('avg: ').to(list)
window (0, 1, 2, 3, 4)
avg 2
window (1, 2, 3, 4, 5)
avg 3
window (2, 3, 4, 5, 6)
avg 4
window (3, 4, 5, 6, 7)
avg 5
window (4, 5, 6, 7, 8)
avg 6
window (5, 6, 7, 8, 9)
avg 7
Out[5]: [2, 3, 4, 5, 6, 7]
```

##### Rolling average of an infinite stream

```python
In [1]: from itertools import count

In [2]: from statistics import mean

In [3]: from generators import G  # G is aliased for Generator internally for shorter import

In [4]: G(count()).window(5).print().map(mean).print().first(3).run()
(0, 1, 2, 3, 4)
2
(1, 2, 3, 4, 5)
3
(2, 3, 4, 5, 6)
4
```

#### File Processing

##### Log Parsing
Rough equivalent of `grep 'Xbox' /var/log/messages | tail`

```python
In [1]: from generators import G

In [2]: G(  # open the main system log file for reading
   ...:     open('/var/log/messages', 'r')
   ...: ).map(  # strip trailing whitespaces from each line
   ...:     str.strip
   ...: ).filter(  # filter for lines with the term 'Xbox'
   ...:     lambda line: 'Xbox' in line
   ...: ).last(  # only return the last 5 filtered lines
   ...:     5
   ...: ).to(list)  # return the result as a list
Out[2]:
['Dec 31 13:59:59 gate local7.info dhcpd: DHCPACK on 192.168.0.7 to 2c:54:91:bb:1e:15 (XboxOne) via eth1',
 'Dec 31 13:59:59 gate local7.info dhcpd: DHCPREQUEST for 192.168.0.7 from 2c:54:91:bb:1e:15 (XboxOne) via eth1',
 'Dec 31 13:59:59 gate local7.info dhcpd: DHCPACK on 192.168.0.7 to 2c:54:91:bb:1e:15 (XboxOne) via eth1',
 'Dec 31 13:59:59 gate local7.info dhcpd: DHCPREQUEST for 192.168.0.7 from 2c:54:91:bb:1e:15 (XboxOne) via eth1',
 'Dec 31 13:59:59 gate local7.info dhcpd: DHCPACK on 192.168.0.7 to 2c:54:91:bb:1e:15 (XboxOne) via eth1']
```

##### Random Number Generation   #MP TODO bad example, replace with something better

```python
In [1]: from generators import G, read

In [2]: random_ints = G(
    ...:     # Open /dev/urandom as a byte stream to read random bytes in
    ...:     read('/dev/urandom', mode='rb', record_size=1)
    ...: ).map(
    ...:     # Convert the bytes to ints
    ...:     lambda i: int.from_bytes(i, 'little')
    ...: )

In [3]: next(random_ints)  #MP TODO explain why next() is needed
Out[3]: 186

In [4]: next(random_ints)
Out[4]: 235

In [5]: # If we need to manipulate the stream further we still can

In [6]: random_int_chunks = random_ints.chunk(4)   #MP TODO explain why chunks does not need next()

In [7]: next(random_int_chunks)
Out[7]: (235, 255, 170, 135)

In [8]: next(random_int_chunks)
Out[8]: (132, 56, 22, 170)

In [9]: random_int_chunks.map(sum).first(8).to(list)  #MP TODO maybe use different output like tuple, so demonstrate different usage of `.to`
Out[9]: [649, 710, 294, 699, 550, 581, 561, 726]

In [10]: random_ints.print().accumulate().first(10).to(list) #MP introduction of `accumulate`  what does it do?  why is it necessary here? how would it look like without it?
74
236
106
194
35
45
105
108
38
65
Out[10]: [74, 310, 416, 610, 645, 690, 795, 903, 941, 1006]

In [11]: # this also makes it easy to analyze infinite streams #MP How is it different from normal finite sequences?

In [12]: random_ints.first(10000).to(max)
Out[12]: 255

In [13]: random_ints.first(10000).to(min)
Out[13]: 0
```

### Benchmarking  #MP has nothing to do with usability, does not belong in quickstart

```python
In [1]: from generators import G

In [2]: from itertools import cycle

In [3]: # .benchmark() can be used to return how many iterations
        # a pipeline can run per second
        #
        # this is more useful for generators than timeit because
        # full stream applications should be measured by how many
        # tasks they can run through before becoming overloaded
        # to determine if the pipeline is fast enough for your
        # company's needs.

In [4]: G(cycle(range(10))).benchmark()
Out[4]: 4805936

In [5]: G(cycle(range(10))).map(float).benchmark()
Out[5]: 2740246

In [6]: G(cycle(range(10))).map(float).filter(lambda i: i%2 == 1).benchmark()
Out[6]: 792458
```
