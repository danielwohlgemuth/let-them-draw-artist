# Let Them Draw - Artist

This is the artist Lambda function for the Let Them Draw app that generates artwork based on the user's requirements.

The "art" that the artists generate are just simple shapes and patterns.

The patterns were inspired by the [generativeartistry.com tutorials](https://generativeartistry.com/tutorials/).

See the [let-them-draw-infrastructure](https://github.com/danielwohlgemuth/let-them-draw-infrastructure) repo for more information.

## Shapes

### Square

![Square](/assets/square_blue.png)

### Circle

![Circle](/assets/circle_green.png)

### Hypnotic Squares

![Hypnotic Squares](/assets/hypnotic_squares_red.png)

### Tiled Lines

![Tiled Lines](/assets/tiled_lines_indigo.png)

### Voronoi

![Voronoi](/assets/voronoi_black.png)

## Setup

Install [uv](https://docs.astral.sh/uv/).

Run `uv sync` to install dependencies.

## Testing

Run `./run-tests.sh` to run tests.

The coverage report can then be found in the `coverage_report` folder.

## Drawing

Run `./draw-image.sh <shape> <color>` to draw an image.

Shape should be one of the following: `square`, `circle`, `"hypnotic squares"`, `"tiled lines"`, `voronoi`

Color should be a color name or hex code. See [CSS Color Names](https://drafts.csswg.org/css-color-4/#named-colors) for a list of color names.