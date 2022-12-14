<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="is-flex is-flex-direction-column is-flex-align-items-stretch">
    <div
      hidden
      id="video_container">
      <video
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
    <div
    class="content"
      id="description">
      <ul>
        <li
          v-for="(highlight, highlight_index) in highlights.taggings">
          <span
            v-if="highlight.position.what == 'range'">
            From {{ highlight.position.from }}sec to {{ highlight.position.to }}sec.
          </span>
          <span
            v-if="highlight.position.what == 'point'">
            At {{ highlight.position.at }}sec.
          </span>
          <span
            v-if="highlight.position.what == 'all'">
            Entire clip.
          </span>
          <span
            v-if="highlight.comment && highlight.comment.length">
            Comment: <b>"{{ highlight.comment }}"</b>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { nextTick, watch } from 'vue';
import { Store } from '@/store/store.js';

const FPS = 25;

export default {
  name : 'MediaPrintVideo',
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
        this.process_highlights(new_highlights);
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
              highlights.push({
                'what' : 'range',
                'from' : this.delogicalize_timestamp(0.0),
                'to' : this.delogicalize_timestamp(this.duration),
                'colour' : h.colour,
                'emphasized' : emp.length ? emp.includes(h.handle) : true,
              });
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
      this.process_highlights(this.highlights);
      this.redraw();
    });

    this.$nextTick(() => {
      this.process_highlights(this.highlights);
      this.redraw();
    });
  },
  methods : {
    // given new highlights, distill them into a list the rest
    // of the code can visualize
    process_highlights : function(new_highlights) {
      let highlights = [];
      let emp = new_highlights.emphasis;

      // build up a new list & install it
      new_highlights.taggings.forEach((h) => {
        let p = h.position;
        switch (p.what) {
          case 'all':
              highlights.push({
                'what' : 'range',
                'from' : this.delogicalize_timestamp(0),
                'to' : this.delogicalize_timestamp(this.duration),
                'colour' : h.colour,
                'emphasized' : emp.length ? emp.includes(h.handle) : true,
              });
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
  display: hidden;
}
#stubbed_video {
  top: 0px;
  left: 0px;
  width: 100%;
  height: 100%;
  position: absolute;
}
</style>
