import shapely
import plotly
from plotly.graph_objects import Scatter

def draw_shape(geom:shapely.Geometry, fig:plotly.graph_objs.Figure, irow:int=1, icol:int=1, color:str='blue', name:str='shape', markersize:int=10, linewidth:int=5):
    """
    Add a shape to a plotly figure.
    
    Args:
    	geom: A geometry object.
    	fig: Handle of a plotly figure.
    	irow: Subplot row.
    	icol: Subplot column.
    	color: Color to use.
    	name: Name to use in the plot legend.
        markersize: Size of any points to be drawn.
        linewidth: Width of any lines to be drawn.
    	
    This function adds a `shapely.Geometry` object to a `plotly` plot.
    """

    gt = geom.geom_type

    if gt == 'Point':
        xx = [geom.xy[0][0]]
        yy = [geom.xy[1][0]]
        trace = Scatter(
            x=xx, y=yy, name=name, 
            mode='markers', marker={'color': color, 'size': markersize}
        )
        fig.append_trace(trace, irow, icol)
        
    elif gt == 'MultiPoint':
        xx = [z.xy[0][0] for z in geom.geoms]
        yy = [z.xy[1][0] for z in geom.geoms]
        trace = Scatter(
            x=xx, y=yy, name=name, 
            mode='markers', marker={'color': color, 'size': markersize}
        )
        fig.append_trace(trace, irow, icol)
        
    elif gt == 'LineString':
        coords = geom.coords
        xx = [z[0] for z in coords]
        yy = [z[1] for z in coords]
        trace = Scatter(
            x=xx, y=yy, name=name, 
            mode='lines', marker={'color': color, 'size': markersize},
            line={'width': linewidth}
        )
        fig.append_trace(trace, irow, icol)
        
    elif gt == 'MultiLineString':
        xx = []
        yy = []
        for g in geom.geoms:
            coords = g.coords
            xx += [z[0] for z in coords] + [None]
            yy += [z[1] for z in coords] + [None]
        trace = Scatter(
            x=xx, y=yy, name=name, 
            mode='lines', marker={'color': color, 'size': markersize},
            line={'width': linewidth}
        )
        fig.append_trace(trace, irow, icol)

    elif gt == 'Polygon':
        coords = geom.exterior.coords
        xx = [z[0] for z in coords]
        yy = [z[1] for z in coords]
        trace = Scatter(
            x=xx, y=yy, name=name, 
            mode='lines', marker={'color': color}, fill='toself'
        )
        fig.append_trace(trace, irow, icol)

    elif gt == 'MultiPolygon':
        trace = []
        for g in geom.geoms:
            coords = g.exterior.coords
            xx = [z[0] for z in coords]
            yy = [z[1] for z in coords]
            trace =Scatter(
                x=xx, y=yy, name=name, 
                mode='lines', marker={'color': color}, fill='toself'
            )
            fig.append_trace(trace, irow, icol)


def _holy_polygon(geom):
    
    # Interiors:
    for g in geom.interiors:
        inner_x = [z[0] for z in g.coords]
        inner_y = [z[1] for z in g.coords]
        trace = Scatter(
            x=inner_x, y=inner_y, name='hole', fill='none',
            marker={'color': 'red'}
        )
        fig.append_trace(trace, irow, 1)
    
    coords = geom.exterior.coords
    outer_x = [z[0] for z in coords]
    outer_y = [z[1] for z in coords]
    trace = Scatter(
        x=outer_x, y=outer_y, name='polygon', fill='tonext',
        marker={'color': 'red'}
    )
    fig.append_trace(trace, irow, 1)

