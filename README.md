![image][images/example-image.png]

# geo-encodings

	Positional encodings for geometric objects
	
If you do geospatial analysis,
you probably deal with geometric objects of type Point LineString, and Polygon 
(in addition to aggregated versions of these objects: MultiPoint, 
MultiLineString, and MultiPolygon). 
Eventually you will run into the problem that most Machine Learning tools --
classifiers, regression models, neural networks -- are not built to ingest these
standard geometric objects. That's where this package comes in.

The `geo-encodings` package implements a few different methods for turning 
arbitrary geometric objects into vectors that encode the essential 
features of their structure. Here's a quick example of its use.

```python
from geo_encodings.encoders import MPPEncoder
encoder = MPPEncoder(domain=[0, 0, 100, 100], resolution=20)

import shapely
g = shapely.from_wkt('POINT(23 37)')
e = encoder.encode(g)
print(e.values())

---
[0.11323363 0.15628545 0.13055936 0.07307309 0.03344699 0.01396199
 0.23930056 0.42183804 0.30056792 0.13055936 0.05109572 0.01939549
 0.31356727 0.80885789 0.42183804 0.15628545 0.0576166  0.02121767
 0.19664689 0.31356727 0.23930056 0.11323363 0.04626952 0.01798739
 0.08731465 0.11587698 0.0990703  0.05863808 0.02815546 0.01215945
 0.03496679 0.04269944 0.03828613 0.02591118 0.01429364 0.00691243]
```

You have just defined a 25-element vector that encodes the Point location
(x = 23, y = 37) within a square domain (lower left = (0, 0), upper right = (100, 100)).

So why bother encoding two numbers as a 25-element vector?

- The vector can be fed to most machine learning models; 'POINT(23, 37)' can not.
- The exact same operation works for all other types of geometries: LineString, Polygon, MultiPoint, MultiLineString, and MultiPolygon.
- In other words, *any* geometric object can be represented using a consistent format -- a vector of a given size -- within a given domain.

That is, this lets you feed shapes to machine learning models. 

## Supported encoding models

The `geo-encodings` package implements a few different ways to encode shapes.

### Multi-Point Proximity (MPP) Encoding

bc

### Discrete Indicator Vector (DIV) Encoding

abc

### Partial Coverage Fraction (PCE) encoding

abc

## Installation

```python
pip install geo-encodings
```


 
- The vector captures all or most of the relevant information





