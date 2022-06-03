<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    ref="image_container"
    id="image_container">
    <img
      :src="src"
      id="actual_image"
      @load="image_loaded"
      ref="actual_image"/>
    <canvas
      ref="selection_layer"
      id="selection_layer"/>
  </div>
</template>

<script>
import { nextTick } from 'vue';

const MIN_DRAGGING_TIME = 500;
const FILL_STYLE = 'rgba(255, 165, 0, 0.3)';
const STROKE_STYLE = 'rgb(255, 165, 0)';
const FILL_STYLE_HIGHLIGHT = 'rgba(165, 255, 0, 0.3)';
const STROKE_STYLE_HIGHLIGHT = 'rgb(165,255, 0)';

export default {
  name : 'MediaTagImage',
  data : function() {
    return {
      last_mousedown : undefined,
      display : {
        highlights : [],
        selection : null,
      },
    };
  },
  props : [
    'src',
    'highlights',
  ],
  emits : [
    'selected',
  ],
  setup : function() {
  },
  watch : {
    // upon highlights change, flush out the old display list and rebuild it
    // to look like the given highlights but then in pixel coordinates
    highlights : {
      handler : function(new_highlights) {
        let highlights = [];

        new_highlights.forEach((h) => {
          switch (h.what) {
            case 'all':
                break;
            case 'point' : 
                highlights.push({
                  'what' : 'point',
                  'at' : this.delogicalize_coords(h.at.x, h.at.y),
                });
                break;
            case 'range' : 
                highlights.push({
                  'what' : 'range',
                  'from' : this.delogicalize_coords(h.from.x, h.from.y),
                  'to' : this.delogicalize_coords(h.to.x, h.to.y),
                });
                break;
            default:
                console.log(`error: unknown type of highlight "${h.what}"`);
          }
        });
        this.display.highlights = highlights;
        this.redraw();
      },
      // no need to deep-follow, we need list changes, not item changes
      deep : false,
    },
  },
  mounted : function() {

    // upon mousedown, merely record where/when the last mousedown happened
    // and start recording a selection, we'll consider it a range now and
    // if it turns out to be a click rather than a drag, patch it to be a point
    // afterwards
    this.$refs.selection_layer.addEventListener('mousedown', (event) => {
      let where = this.normalize_mouse_coords(event.clientX, event.clientY);

      // remember state
      this.last_mousedown = {
        at : Date.now(),
        x : where.x,
        y : where.y
      };
      this.display.selection = {
        what  : 'range',
        from : {
          x : where.x,
          y : where.y,
        },
        to : {
          x : where.x,
          y : where.y,
        },
      };

      this.redraw();
    });

    // upon mousemove, if there is a drag in process, note down to where we're
    // dragging now
    this.$refs.selection_layer.addEventListener('mousemove', (event) => {
      if (!this.last_mousedown) {
        // not an error, but there was no drag in process
        return;
      }

      let selection = this.display.selection;
      let where = this.normalize_mouse_coords(event.clientX, event.clientY);

      if (selection.what != 'range') {
        console.log(`error: expected dragging context to be "range", not "${selection.what}"`);
        return;
      }

      selection.to.x = where.x;
      selection.to.y = where.y;

      this.redraw();
    });

    // upon click (doubling as mouseup), see how long we've been dragging, and:
    //  - if it's less than MIN_DRAGGING_TIME (and mouse didn't move), consider it a
    //    a click (and change the current 'range' selection to a 'point' selection)
    //  - else, consider it a proper drag, just note down the last location as it's 'to'
    // and emit an event accordingly
    this.$refs.selection_layer.addEventListener('click', (event) => {
      // sanity
      if (!this.last_mousedown) {
        console.log("error: click without a last_mousedown");
        return;
      }
      if (!this.display.selection) {
        console.log("error: click without a display");
        return;
      }

      let selection = this.display.selection;
      let where = this.normalize_mouse_coords(event.clientX, event.clientY);
      let mouse_down_time = Date.now() - this.last_mousedown.at;
      let mouse_moved = (where.x != this.last_mousedown.x) ||
        (where.y != this.last_mousedown.y);

      if ((mouse_down_time < MIN_DRAGGING_TIME) && !mouse_moved) {
        // didn't reach MIN_DRAGGING_TIME and no movement, it's a point click, over-
        // write any existing drag
        this.display.selection = {
          what : 'point',
          at : {
            x : where.x,
            y : where.y,
          },
        };
        this.$emit('selected', {
          what : 'point',
          at : this.logicalize_coords(where.x, where.y),
        });
      } else {
        // let it remain a range selection (drag)
        selection.to.x = where.x;
        selection.to.y = where.y;
        this.$emit('selected', {
          what : 'range',
          from : this.logicalize_coords(selection.from.x, selection.from.y),
          to : this.logicalize_coords(selection.to.x, selection.to.y),
        });
      }

      // don't forget to clear the drag state
      this.last_mousedown = null;

      this.redraw();
    });
  },
  methods : {
    // when the image is loaded, resize the containing div so that
    // it (and the canvas) fit
    image_loaded : function() {
      let container = this.$refs.image_container;
      let image = this.$refs.actual_image;
      let selection = this.$refs.selection_layer;

      container.setAttribute('style', `width: ${image.clientWidth}px; height: ${image.clientHeight}px`);
      selection.width = image.clientWidth;
      selection.height = image.clientHeight;
    },

    // rebase mouse event coordinates (window pixels) to the selection layer's
    // point of origin (canvas pixels)
    normalize_mouse_coords : function(eX, eY) {
      let coords = this.$refs.selection_layer.getBoundingClientRect();
      return {
        x : eX - coords.left,
        y : eY - coords.top,
      };
    },

    // make [0-1] values out of canvas pixels
    logicalize_coords : function(eX, eY) {
      let image = this.$refs.actual_image;
      return {
        x : eX / image.clientWidth,
        y : eY / image.clientHeight,
      };
    },

    // make canvas pixels out of [0-1] values
    delogicalize_coords : function(eX, eY) {
      let image = this.$refs.actual_image;
      return {
        x : parseInt(eX * image.clientWidth),
        y : parseInt(eY * image.clientHeight),
      };
    },

    redraw: function() {
      let ctx = this.$refs.selection_layer.getContext('2d');
      let ctx_w = this.$refs.selection_layer.width;
      let ctx_h = this.$refs.selection_layer.height;

      // clear it all first
      ctx.clearRect(0, 0, ctx_w, ctx_h);

      function draw(something) {
        // draw a point or a range
        if (something.what == 'point') {
          ctx.beginPath();
          ctx.arc(something.at.x, something.at.y, 8, 0, 2*Math.PI);
          ctx.fill();
          ctx.stroke();
        } else if (something.what == 'range') {
          ctx.fillRect(something.from.x, something.from.y,
            something.to.x - something.from.x,
            something.to.y - something.from.y);
          ctx.strokeRect(something.from.x, something.from.y,
            something.to.x - something.from.x,
            something.to.y - something.from.y);
        }
      };

      // draw the highlights, if any
      let highlights = this.display.highlights;
      if (highlights) {
        // relevant style
        ctx.fillStyle = FILL_STYLE_HIGHLIGHT;
        ctx.strokeStyle = STROKE_STYLE_HIGHLIGHT;
        ctx.lineWidth = 2;

        for (let i = 0; i < highlights.length; i++) {
          let h = highlights[i];
          draw(h);
        }
      }

      // draw the selection, if any
      // (and over the highlights, if any)
      let selection = this.display.selection;
      if (selection) {
        // relevant style
        ctx.fillStyle = FILL_STYLE;
        ctx.strokeStyle = STROKE_STYLE;
        ctx.lineWidth = 2;

        // draw a point or a range
        draw(selection);
      }

    },
  },
};
</script>

<style scoped>
#image_container {
  position: relative;
}
#actual_image {
  width: 100%;
  position: absolute;
}
#selection_layer {
  width: 100%;
  height: 100%;
  position: absolute;
}
</style>
