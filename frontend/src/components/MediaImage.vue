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
import { tagStore } from '@/store/tag.js';

const MIN_DRAGGING_TIME = 500;
const FILL_STYLE = 'rgba(255, 165, 0, 0.3)';
const STROKE_STYLE = 'rgb(255, 165, 0)';

export default {
  name : 'MediaImage',
  data : function() {
    return {
      last_mousedown : undefined,
      display : undefined,
    };
  },
  props : [
    'src',
    'highlight',
  ],
  emits : [
    'selected',
  ],
  setup : function() {
    const tag_store = tagStore();
    return { tag_store };
  },
  watch : {
    highlight : {
      handler : function(new_highlight) {
        if (!this.display) {
          this.display = {};
        }
        if (!new_highlight || new_highlight.what == 'all') {
          this.display.what = 'nothing';
        }
        if (new_highlight.what == 'point') {
          this.display.what = 'point';
          this.display.stop = this.delogicalize_coords(new_highlight.at.x, new_highlight.at.y);
        } else if (new_highlight.what == 'range') {
          this.display.what = 'range';
          this.display.start = this.delogicalize_coords(new_highlight.from.x, new_highlight.from.y);
          this.display.stop = this.delogicalize_coords(new_highlight.to.x, new_highlight.to.y);
        }
        this.redraw_selection();
      },
      deep : true,
    },
  },
  mounted : function() {
    this.$refs.selection_layer.addEventListener('mousedown', (event) => {
      let where = this.normalize_mouse_coords(event.clientX, event.clientY);
      this.last_mousedown = {
        at : Date.now(),
        x : where.x,
        y : where.y
      };
      this.display = {
        what  : 'range',
        start : {
          x : where.x,
          y : where.y,
        },
        stop : {
          x : where.x,
          y : where.y,
        },
      };
      console.log(`mousedown at x=${where.x} y=${where.y}`);
      this.redraw_selection();
    });
    this.$refs.selection_layer.addEventListener('mousemove', (event) => {
      if (this.last_mousedown == undefined || this.display == undefined) {
        return;
      }
      let where = this.normalize_mouse_coords(event.clientX, event.clientY);
      this.display.stop.x = where.x;
      this.display.stop.y = where.y;
      console.log("move");
      this.redraw_selection();
    });
    this.$refs.selection_layer.addEventListener('click', (event) => {
      if (this.last_mousedown == undefined) {
        console.log("error: click without a last_mousedown");
        return;
      }
      if (this.display == undefined) {
        console.log("error: click without a display");
        return;
      }

      let where = this.normalize_mouse_coords(event.clientX, event.clientY);
      let mouse_down_time = Date.now() - this.last_mousedown.at;
      let mouse_moved = (where.x != this.last_mousedown.x) ||
        (where.y != this.last_mousedown.y);

      if ((mouse_down_time < MIN_DRAGGING_TIME) && !mouse_moved) {
        console.log("a click");
        this.display.what = 'point';
        this.display.stop.x = where.x;
        this.display.stop.y = where.y;
        this.$emit('selected', {
          what : 'point',
          at : this.logicalize_coords(where.x, where.y),
        });
      } else {
        console.log("a drag");
        this.display.what = 'range';
        this.display.stop.x = where.x;
        this.display.stop.y = where.y;
        this.$emit('selected', {
          what : 'range',
          from : this.logicalize_coords(this.display.start.x, this.display.start.y),
          to : this.logicalize_coords(where.x, where.y),
        });
      }
      console.log(mouse_down_time);
      this.last_mousedown = undefined;
      this.redraw_selection();
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
    normalize_mouse_coords : function(eX, eY) {
      let coords = this.$refs.selection_layer.getBoundingClientRect();
      return {
        x : eX - coords.left,
        y : eY - coords.top,
      };
    },
    logicalize_coords : function(eX, eY) {
      let image = this.$refs.actual_image;
      return {
        x : eX / image.clientWidth,
        y : eY / image.clientHeight,
      };
    },
    delogicalize_coords : function(eX, eY) {
      let image = this.$refs.actual_image;
      return {
        x : parseInt(eX * image.clientWidth),
        y : parseInt(eY * image.clientHeight),
      };
    },
    redraw_selection : function() {
      /*
      if (this.display == undefined) {
        return;
      }
      */
      let ctx = this.$refs.selection_layer.getContext('2d');
      let ctx_w = this.$refs.selection_layer.width;
      let ctx_h = this.$refs.selection_layer.height;

      ctx.clearRect(0, 0, ctx_w, ctx_h);
      ctx.fillStyle = FILL_STYLE;
      ctx.strokeStyle = STROKE_STYLE;
      ctx.lineWidth = 2;

      if (this.display.what == 'point') {
        console.log("drawing a point at "+this.display.stop.x+"/"+this.display.stop.y);
        ctx.beginPath();
        ctx.arc(this.display.stop.x, this.display.stop.y, 8, 0, 2*Math.PI);
        ctx.fill();
        ctx.stroke();
      } else if (this.display.what == 'range') {
        console.log("drawing a range at "+this.display.stop.x+"/"+this.display.stop.y);
        ctx.fillRect(this.display.start.x, this.display.start.y,
          this.display.stop.x - this.display.start.x,
          this.display.stop.y - this.display.start.y);
        ctx.strokeRect(this.display.start.x, this.display.start.y,
          this.display.stop.x - this.display.start.x,
          this.display.stop.y - this.display.start.y);

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
