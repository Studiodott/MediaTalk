<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="is-flex is-flex-direction-column is-align-items-center">
    <audio
      id="actual_audio"
      ref="actual_audio">
      <source
        v-bind:src="src">
      No browser support for audio :-(
    </audio>
    <div
      id="stubbed_video"
      ref="stubbed_video"
      class="is-flex is-flex-direction-row is-justify-content-center">
    <svg
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
      width="96"
      height="96">
      <path
        v-if="!playing_ctx"
        d="M 16 16 V 80 L 80 48 Z"
        fill="white"/>
      <rect
        v-if="playing_ctx"
        style="fill: white"
        x="16"
        y="16"
        width="21"
        height="64"/>
      <rect
        v-if="playing_ctx"
        style="fill: white"
        x="58"
        y="16"
        width="21"
        height="64"/>
    </svg>
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
  name : 'MediaTagAudio',
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
    const store = Store();
    return { store };
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

        let jump_target = undefined;

        if (emp.length) {
          jump_target = new_highlights.taggings.find((h) => h.handle == emp[0]);
        } else {
          if (new_highlights.taggings.length) {
            jump_target = new_highlights.taggings[0];
          }
        }

        if (jump_target) {
          switch (jump_target.position.what) {
            case 'point':
                this.set_position(parseFloat(jump_target.position.at));
                break;
            case 'range':
                this.set_position(parseFloat(jump_target.position.from));
                break;
          }
          this.$refs.actual_audio.play();
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

        // pause if needs be
        if (new_selection.what == 'range') {
          if (new_selection.from && new_selection.to) {
            this.$refs.actual_audio.pause();
          }
        }

        this.redraw();
      },
      // but we want to see all changes here, might be some timestamp changed
      deep : true,
    },
  },
  mounted : function() {
    // follow the video player's actions
    this.$refs.actual_audio.addEventListener('durationchange', (e) => {
      this.duration = e.target.duration;
    });
    this.$refs.actual_audio.addEventListener('playing', (e) => {
      this.started_playing();
    });
    this.$refs.actual_audio.addEventListener('pause', (e) => {
      this.stopped_playing();
    });
    this.$refs.actual_audio.addEventListener('ended', (e) => {
      this.stopped_playing();
    });
    this.$refs.actual_audio.addEventListener('error', (e) => {
      this.stopped_playing();
    });
    this.$refs.stubbed_video.addEventListener('click', (e) => {
      let audio = this.$refs.actual_audio;
      if (audio.paused) {
        audio.play();
      } else {
        audio.pause();
      }
    });
    // timeline clicks update the video position
    this.$refs.timing_timeline.addEventListener('click', (e) => {
      let when = this.timeline_resolve_click(event.clientX, event.clientY);
      this.set_position(when);
    });

    // follow volume changes
    this.update_volume(this.store.runtime.audio_volume);
    watch(this.store.runtime, (rt) => {
      this.update_volume(rt.audio_volume);
    });
  },
  methods : {
    // update volume
    update_volume : function(pct) {
      this.$refs.actual_audio.volume = pct / 100.0;
    },
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
      this.$refs.actual_audio.currentTime = when;
      this.update_position();
    },
    // upon position update, fire off the advanced event and redraw
    update_position : function() {
      let when = this.$refs.actual_audio.currentTime;
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

      let when = this.$refs.actual_audio.currentTime;
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
#stubbed_video {
  width: 100%;
  background: #909090;
}
</style>
