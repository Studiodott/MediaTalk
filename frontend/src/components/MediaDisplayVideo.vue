<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
    <video
      id="actual_video"
      ref="actual_video"
      controls>
      <source
        v-bind:src="src">
      No browser support for video :-(
    </video>
    {{ duration }}
    <div
      id="timing_container">
      <img
        id="timing_waveform"
        ref="timing_waveform"
        v-if="waveform.length > 0"
        :src="waveform"
        @load="image_loaded">
      <canvas
        ref="timing_timeline"
        id="timing_timeline"/>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';

const FPS = 25;
const FILL_STYLE_SELECTION = 'rgba(255, 165, 0, 0.3)';
const STROKE_STYLE_SELECTION = 'rgb(255, 165, 0)';
const FILL_STYLE_HIGHLIGHT = 'rgba(165, 255, 0, 0.3)';
const STROKE_STYLE_HIGHLIGHT = 'rgb(165, 255, 0)';
const FILL_STYLE = 'rgba(165, 255, 166, 0.3)';
const STROKE_STYLE = 'rgb(165, 255, 166)';

export default {
  name : 'MediaDisplayVideo',
  data : function() {
    return {
      duration : undefined,
      playing_ctx : undefined,
      display : {
        highlights : [],
        selection : null,
      },
    };
  },
  props : [
    'src',
    'waveform',
    'selection',
    'highlights',
  ],
  emits : [
    'selected',
    'advanced'
  ],
  setup : function() {
  },
  watch : {
    // upon highlights change, flush out the old display list and rebuild it
    // to look like the given highlights but then in pixel coordinates
    highlights : {
      handler : function(new_highlights) {
        let highlights = [];

        // build up a new list & install it
        new_highlights.forEach((h) => {
          switch (h.what) {
            case 'all':
                break;
            case 'point' : 
                highlights.push({
                  'what' : 'point',
                  'at' : this.delogicalize_timestamp(h.at),
                });
                break;
            case 'range' : 
                highlights.push({
                  'what' : 'range',
                  'from' : this.delogicalize_timestamp(h.from),
                  'to' : this.delogicalize_timestamp(h.to),
                });
                break;
            default:
                console.log(`error: unknown type of highlight "${h.what}"`);
          }
        });
        this.display.highlights = highlights;

        // if there is a first, jump towards it
        if (new_highlights && new_highlights.length) {
          let first = new_highlights[0];
          switch (first.what) {
            case 'all':
                break;
            case 'point':
                this.set_position(parseFloat(first.at));
                break;
            case 'range':
                this.set_position(parseFloat(first.from));
                break;
            default:
                console.log(`error: don't know how to handle highlight of type "${first.what}"`);
                break;
          }
        }

        this.redraw();
      },
      // no need to deep-follow, we need list changes, not item changes
      deep : false,
    },
    // same for the selection, but take care that it could be a range with
    // the endpoint unspecified (id est, still being decided by user)
    selection : {
      handler : function(new_selection) {
        if (!new_selection) {
          this.display.selection = null;
          return;
        }

        switch (new_selection.what) {
          case 'all':
              break;
          case 'point':
              this.display.selection = {
                what : 'point',
                at : this.delogicalize_timestamp(new_selection.at),
              };
              break;
          case 'range':
              this.display.selection = {
                what : 'range',
                from : new_selection.from ? this.delogicalize_timestamp(new_selection.from) : null,
                to : new_selection.to ? this.delogicalize_timestamp(new_selection.to) : null,
              };
              break;
          default:
              console.log(`error: don't know how to handle selection of type "${new_selection.what}"`);
              break;
        }
      },
      // but we want to see all changes here, might be some timestamp changed
      deep : true,
    },
  },
  mounted : function() {
    // follow the video player's actions
    this.$refs.actual_video.addEventListener('durationchange', (e) => {
      this.duration = e.target.duration;
    });
    this.$refs.actual_video.addEventListener('playing', (e) => {
      this.started_playing();
    });
    this.$refs.actual_video.addEventListener('pause', (e) => {
      this.stopped_playing();
    });
    // timeline clicks update the video position
    this.$refs.timing_timeline.addEventListener('click', (e) => {
      let when = this.timeline_resolve_click(event.clientX, event.clientY);
      this.set_position(when);
    });
  },
  methods : {
    // when the image is loaded, resize the containing div so that
    // it (and the canvas) fit
    image_loaded : function() {
      let waveform = this.$refs.timing_waveform;
      let timeline = this.$refs.timing_timeline;
      timeline.width = waveform.clientWidth;
      timeline.height = waveform.clientHeight;
    },
    // set the video's position, and fire off the updating handler
    set_position : function(when) {
      this.$refs.actual_video.currentTime = when;
      this.update_position();
    },
    // upon position update, fire off the advanced event and redraw
    update_position : function() {
      let when = this.$refs.actual_video.currentTime;
      this.$emit('advanced', {
        'what' : 'point',
        'at' : when,
      });
      this.redraw();
    },
    // when we start playing, we start an interval timer to update the
    // position at FPS
    started_playing : function() {
      this.playing_ctx = setInterval(() => {
        this.update_position();
      }, 1000 / FPS);
    },
    // and when we stop playing, we stop the interval timer
    stopped_playing : function() {
      clearInterval(this.playing_ctx);
    },
    // turn a click event's clientX/Y on the timeline into a timestamp
    timeline_resolve_click : function(mouse_x, mouse_y) {
      if (this.duration == undefined) {
        // we have no known duration, do nothing yet
        return;
      }
      let canvas_pos = this.$refs.timing_timeline.getBoundingClientRect();
      mouse_x -= canvas_pos.left;
      mouse_y -= canvas_pos.top;
      return (mouse_x / canvas_pos.width) * this.duration;
    },
    // translate a timestamp to a pixel offset in the timeline
    delogicalize_timestamp : function(ts) {
      if (this.duration == undefined) {
        // we have no known duration, do nothing yet
        return;
      }
      let w = this.$refs.timing_timeline.width;
      let pos = parseInt((parseFloat(ts) / this.duration) * w);
      return pos;
    },
    // main drawing logic
    redraw : function() {
      if (this.duration == undefined) {
        // we have no known duration, do nothing yet
        return;
      }
      let w = this.$refs.timing_timeline.width;
      let h = this.$refs.timing_timeline.height;

      let when = this.$refs.actual_video.currentTime;
      let pos = parseInt((when / this.duration) * w);

      let ctx = this.$refs.timing_timeline.getContext('2d');

      ctx.clearRect(0, 0, w, h);

      function draw(something) {
        if (something.what == 'point') {
          let pos = something.at;
          ctx.beginPath();
          ctx.moveTo(pos, 0);
          ctx.lineTo(pos, h);
          ctx.stroke();
        } else if (something.what == 'range') {
          let from = something.from;
          let to = something.to;
          ctx.fillRect(from, 0, to-from, h);
          ctx.strokeRect(from, 0, to-from, h);
        }
      }

      // the highlights
      let highlights = this.display.highlights;
      if (highlights) {
        ctx.strokeStyle = STROKE_STYLE_HIGHLIGHT;
        ctx.fillStyle = FILL_STYLE_HIGHLIGHT;
        ctx.lineWidth = 2;

        for (let i = 0; i < highlights.length; i++) {
          let h = highlights[i];
          draw(h);
        }
      }

      // the selection
      let selection = this.display.selection;
      if (selection) {
        // relevant style
        ctx.fillStyle = FILL_STYLE_SELECTION;
        ctx.strokeStyle = STROKE_STYLE_SELECTION;
        ctx.lineWidth = 2;

        // draw a point or a range
        if (selection.what == 'point') {
          draw(selection);
        } else if (selection.what == 'range') {
          draw({
            what : 'range',
            from : selection.from,
            to : selection.to || pos,
          });
        }
      }

      // the current position
      ctx.strokeStyle = STROKE_STYLE;
      ctx.fillStyle = FILL_STYLE;
      ctx.lineWidth = 2;

      draw({
        what : 'point',
        at : pos,
      });
    },
  },
};
</script>

<style scoped>
#timing_container {
  width: 100%;
  height: 64px;
  position: relative;
}
#timing_waveform {
  width: 100%;
  height: 100%;
  position: absolute;
}
#timing_timeline {
  width: 100%;
  height: 100%;
  position: absolute;
}
</style>
