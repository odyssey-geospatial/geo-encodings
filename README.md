
# geo-encodings

![Multi-Point Proximity encodings for all shape types](https://github.com/odyssey-geospatial/geo-encodings/raw/main/images/mpp-encodings-6.jpg)

### Positional encodings for geometric objects
	
Spatial analysis deals with
geometric objects of type Point LineString, and Polygon; 
plus multipart extensions: MultiPoint, 
MultiLineString, and MultiPolygon. 
Most Machine Learning (ML) tools --
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
encoder = MPPEncoder(region=[0, 0, 100, 100], resolution=20)
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
(x = 23, y = 37) within a square region (lower left = (0, 0), 
upper right = (100, 100)).

So why bother encoding a coordinate pair as a 25-element vector?
Mostly because the vector can be fed to most machine learning models,
where the string `"POINT(23, 37)"` typically can not
(unless we are talking about certain Large Language Models (LLMS), 
which are a whole other story).
And importantly, the exact same operation works for all other types of geometries: 
LineString, Polygon, MultiPoint, MultiLineString, and MultiPolygon.
In other words, *any* geometric object in the region can be represented 
in the same form: a vector of aparticular size.

## Supported encoding models

The `geo-encodings` package implements a few different ways to encode shapes.

### Multi-Point Proximity (MPP) Encoding

MPP encoding involves laying out a grid of reference points 
$\bf{r} = {r_i: i \in [1..n]}$
over a rectangular region.
Then for a given shape $\bf{g}$, compute its distance $d_i$ to each reference point, 
where "distance" is the Euclidean distance between the reference point and the closest point of the shape. 
The apply negative exponential scaling to the distances:
$e_i = \exp(-d_i / s)$
where $s$ is the `scale` parameter of the MPP encoder.

### Discrete Indicator Vector (DIV) Encoding

DIV encoding involves dividing a given region into non-overlapping square "tiles".
An encoding for a shape is an indicator vector (0 or 1) indicating which tiles 
it intersects.  

## Supporting packages

* `shapely`: Provides computations on geometric objects.
* `scipy`: Provides tools for handling sparse arrays.

## Installation

```python
pip install geo-encodings
```

## Release History

* 1.0.0: Initial release

## Author and maintainers

* John Collins -- `john@odyssey-geospatial.com`

## Contributing

If you would like to contribute, do this: 
1. Fork the repo (https://github.com/yourname/yourproject/fork)
2. Create your feature branch (git checkout -b feature/myFeatureBranch)
3. Commit your changes (git commit -am 'add some new features')
4. Push to the branch (git push origin feature/myFeatureBranch)
5. Create a new Pull Request
