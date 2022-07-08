<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="is-flex is-flex-direction-column is-flex-align-items-stretch">
    <div
      id="video_container">
      <video
        @load="console.log('LOAD')"
        id="actual_video"
        ref="actual_video">
        <source
          v-bind:src="src">
        No browser support for video :-(
      </video>
      <div
        id="stubbed_video"
        ref="stubbed_video"
        class="is-flex is-flex-direction-column is-justify-content-center is-align-items-center">
        <svg
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          width="96"
          height="96">
          <path
            v-if="!playing_ctx"
            d="M 16 16 V 80 L 80 48 Z"
            fill="white"/>
        </svg>
      </div>
    </div>
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
import { nextTick, watch } from 'vue';
import { Store } from '@/store/store.js';

const FPS = 25;

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
    'selection_colour',
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
        let emp = new_highlights.emphasis;

        // build up a new list & install it
        new_highlights.taggings.forEach((h) => {
          let p = h.position;
          switch (p.what) {
            case 'all':
                break;
            case 'point' : 
                highlights.push({
                  'what' : 'point',
                  'at' : this.delogicalize_timestamp(p.at),
                  'colour' : h.colour,
                  'emphasized' : emp.length ? emp.includes(h.handle) : true,
                });
                break;
            case 'range' : 
                highlights.push({
                  'what' : 'range',
                  'from' : this.delogicalize_timestamp(p.from),
                  'to' : this.delogicalize_timestamp(p.to),
                  'colour' : h.colour,
                  'emphasized' : emp.length ? emp.includes(h.handle) : true,
                });
                break;
            default:
                console.log(`error: unknown type of highlight "${p.what}"`);
          }
        });
        this.display.highlights = highlights;

        // if there is a first, jump towards it
        if (new_highlights && new_highlights.taggings && new_highlights.taggings.length) {
          let first = new_highlights.taggings[0].position;
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
      deep : false,
    },
    // same for the selection, but take care that it could be a range with
    // the endpoint unspecified (id est, still being decided by user)
    selection : {
      handler : function(new_selection) {
        if (!new_selection) {
          this.display.selection = null;
          this.redraw();
          return;
        }

        switch (new_selection.what) {
          case 'all':
              break;
          case 'point':
              this.display.selection = {
                what : 'point',
                at : this.delogicalize_timestamp(new_selection.at),
                colour : this.selection_colour,
              };
              break;
          case 'range':
              this.display.selection = {
                what : 'range',
                from : new_selection.from ? this.delogicalize_timestamp(new_selection.from) : null,
                to : new_selection.to ? this.delogicalize_timestamp(new_selection.to) : null,
                colour : this.selection_colour,
              };
              break;
          default:
              console.log(`error: don't know how to handle selection of type "${new_selection.what}"`);
              break;
        }

        this.redraw();
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
    this.$refs.actual_video.addEventListener('ended', (e) => {
      this.stopped_playing();
    });
    this.$refs.actual_video.addEventListener('error', (e) => {
      this.stopped_playing();
    });
    this.$refs.actual_video.addEventListener('click', (e) => {
      if (event.target.paused) {
        event.target.play();
      } else {
        event.target.pause();
      }
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
      // clear any running context
      if (this.playing_ctx)
        clearInterval(this.playing_ctx);
      this.playing_ctx = setInterval(() => {
        this.update_position();
      }, 1000 / FPS);
    },
    // and when we stop playing, we stop the interval timer
    stopped_playing : function() {
      clearInterval(this.playing_ctx);
      this.playing_ctx = undefined;
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
        if (something.emphasized)
          ctx.fillStyle = something.colour + '9f';
        else
          ctx.fillStyle = something.colour + '5f';

        ctx.strokeStyle = something.colour + 'ff';
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
        ctx.lineWidth = 2;

        // draw a point or a range
        if (selection.what == 'point') {
          draw(selection);
        } else if (selection.what == 'range') {
          draw({
            what : 'range',
            from : selection.from,
            to : selection.to || pos,
            colour : selection.colour,
          });
        }
      }

      // the current position
      ctx.lineWidth = 2;

      draw({
        what : 'point',
        colour : this.selection_colour,
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
#video_container {
  width: 100%;
  position: relative;
}
#stubbed_video {
  top: 0px;
  left: 0px;
  width: 100%;
  height: 100%;
  position: absolute;
}
</style>
