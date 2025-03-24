#
# Visualizations for geometries.
# These are designed to work with "plotly". They add shapes to a given figure subplot.
#

import plotly
from plotly.graph_objects import Scatter

def px_draw(geom, fig, irow=1, icol=1, color='blue'):

    gt = geom.geom_type

    if gt == 'Point':
        xx = [geom.xy[0][0]]
        yy = [geom.xy[1][0]]
        trace = Scatter(
            x=xx, y=yy, name=gt, 
            mode='markers', marker={'color': color, 'size': 12}
        )
        fig.append_trace(trace, irow, icol)
        
    elif gt == 'MultiPoint':
        xx = [z.xy[0][0] for z in geom.geoms]
        yy = [z.xy[1][0] for z in geom.geoms]
        trace = Scatter(
            x=xx, y=yy, name=gt, 
            mode='markers', marker={'color': color, 'size': 12}
        )
        fig.append_trace(trace, irow, icol)
        
    elif gt == 'LineString':
        coords = geom.coords
        xx = [z[0] for z in coords]
        yy = [z[1] for z in coords]
        trace = Scatter(
            x=xx, y=yy, name=gt, 
            mode='lines', marker={'color': color, 'size': 12}
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
            x=xx, y=yy, name=gt, 
            mode='lines', marker={'color': color, 'size': 12}
        )
        fig.append_trace(trace, irow, icol)

    elif gt == 'Polygon':
        coords = geom.exterior.coords
        xx = [z[0] for z in coords]
        yy = [z[1] for z in coords]
        trace = Scatter(
            x=xx, y=yy, name=gt, 
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
                x=xx, y=yy, name=gt, 
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

    

