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

export default {
  name : 'MediaPrintImage',
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
    'selection_colour',
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
        this.parse_highlights(new_highlights);
        this.redraw();
      },
      deep : false,
    },
  },
  mounted : function() {
  },
  methods : {
    // re-parse the highlights to build our own list of visual things
    parse_highlights : function(new_highlights) {
      let highlights = [];
      let emp = new_highlights.emphasis;

      new_highlights.taggings.forEach((h) => {
        let p = h.position;
        switch (p.what) {
          case 'all':
              highlights.push({
                'what' : 'range',
                'from' : this.delogicalize_coords(0, 0),
                'to' : this.delogicalize_coords(1.0, 1.0),
                'colour' : h.colour,
                'emphasized' : emp.length ? emp.includes(h.handle) : true,
              });
              break;
          case 'point' : 
              highlights.push({
                'what' : 'point',
                'at' : this.delogicalize_coords(p.at.x, p.at.y),
                'colour' : h.colour,
                'emphasized' : emp.length ? emp.includes(h.handle) : true,
              });
              break;
          case 'range' : 
              highlights.push({
                'what' : 'range',
                'from' : this.delogicalize_coords(p.from.x, p.from.y),
                'to' : this.delogicalize_coords(p.to.x, p.to.y),
                'colour' : h.colour,
                'emphasized' : emp.length ? emp.includes(h.handle) : true,
              });
              break;
          default:
              console.log(`error: unknown type of highlight "${p.what}"`);
        }
      });
      this.display.highlights = highlights;
      this.redraw();
    },
    // when the image is loaded, resize the containing div so that
    // it (and the canvas) fit
    image_loaded : function() {
      let container = this.$refs.image_container;
      let image = this.$refs.actual_image;
      let selection = this.$refs.selection_layer;

      container.setAttribute('style', `width: ${image.clientWidth}px; height: ${image.clientHeight}px`);

      selection.width = image.clientWidth;
      selection.height = image.clientHeight;

      this.parse_highlights(this.highlights);
      this.redraw();
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
        if (something.emphasized)
          ctx.fillStyle = something.colour + '9f';
        else
          ctx.fillStyle = something.colour + '5f';


        ctx.strokeStyle = something.colour + 'ff';
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
