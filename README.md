
# geo-encodings

![Multi-Point Proximity encodings for all shape types](images/mpp-encodings-6.jpg)

### Positional encodings for geometric objects
	
A lot of spatial analysis deals with
geometric objects of type Point LineString, and Polygon; 
plus groupings of multiple instances of these objects: MultiPoint, 
MultiLineString, and MultiPolygon. 
Unfortunately most Machine Learning (ML) tools --
classifiers, regression models, neural networks -- 
are not built to ingest geometric objects 
in their native format. That's where this package comes in.

The `geo-encodings` package turns 
arbitrary geometric objects into vectors that approximately encode
their shape and location.
Here's a quick example of its use.

```python
# Define a Point object using the `shapely` package.
import shapely
g = shapely.from_wkt('POINT(23 37)')

# Get an encoding of that point.
from geo_encodings.encoders import MPPEncoder
encoder = MPPEncoder(domain=[0, 0, 100, 100], resolution=20)
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

We just defined a 25-element vector that encodes the Point location
(x = 23, y = 37) within a square domain (lower left = (0, 0), 
upper right = (100, 100)).

So why bother encoding a coordinate pair as a 25-element vector?
Mostly because the vector can be fed to most machine learning models,
where the string `"POINT(23, 37)"` typically can not.
And importantly, the exact same operation works for all other types of geometries: 
LineString, Polygon, MultiPoint, MultiLineString, and MultiPolygon.
In other words, *any* geometric object in a given domain can be represented 
using a consistent format -- a vector of a given size.

That is, this lets you feed shapes to machine learning models. 

## Supported encoding models

The `geo-encodings` package implements a few different ways to encode shapes.

### Multi-Point Proximity (MPP) Encoding

MPP encoding involves laying out a grid of reference points 
$\bf{r} = {r_i: i \in [1..n]}$
over a rectangular domain.
Then for a given shape $\bf{g}$, compute its distance $d_i$ to each reference point, 
where "distance" is the Euclidean distance between the reference point and the closest point of the shape. 
The apply negative exponential scaling to the distances:
$\bf{e} = {e_i = \exp(-d_i / s): i \in [1 .. n]}$
where $s$ is the `scale` parameter of the MPP encoder.

### Discrete Indicator Vector (DIV) Encoding

DIV encoding involves dividing a given domain into non-overlapping square "tiles".
An encoding for a shape is an indicator vector (0 or 1) indicating which tiles 
it intersects.  

### Partial Coverage Fraction (PCF) encoding

PCE encoding is similar to DIV encoding in that it divides a domain into 
non-overlapping tiles. But instead of an indicator vector, the encoded values are computes differently for different geometry types.
* For Point and MultiPoint types, the encoding is an indicator vector: 1 if a point falls into a give tile, or 0 otherwise.
* For LineString and MultiLineString types, the encoding is given by 
$e = z / r$ where $z$ is the length of the geometry that
intersects the tile, and $r$ is the `resolution` parameter.
* For Polygon and MultiPolygon type, the encoding is
$z / r^2$, where $z$ is the area of overlap between the shape
and the tile. 

## Supporting packages

* `shapely`: Provides computations on geometric objects.
* `scipy`: Provides tools for handling sparse arrays.

## Installation

```python
pip install geo-encodings
```

## Release History

* 1.0.0: Coming soon

## Author and maintainers

* John Collins -- `john@odyssey-geospatial.com`

## Contributing

1. Fork the repo (https://github.com/yourname/yourproject/fork)
2. Create your feature branch (git checkout -b feature/fooBar)
3. Commit your changes (git commit -am 'Add some fooBar')
4. Push to the branch (git push origin feature/fooBar)
5. Create a new Pull Request
