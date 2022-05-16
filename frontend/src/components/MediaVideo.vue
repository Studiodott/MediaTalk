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
import { tagStore } from '@/store/tag.js';

const FPS = 25;
const FILL_STYLE = 'rgba(255, 165, 0, 0.3)';
const STROKE_STYLE = 'rgb(255, 165, 0)';
const FILL_STYLE_HIGHLIGHT = 'rgba(165, 255, 0, 0.3)';
const STROKE_STYLE_HIGHLIGHT = 'rgb(165,255, 0)';


export default {
  name : 'MediaVideo',
  data : function() {
    return {
      duration : undefined,
      playing_ctx : undefined,
    };
  },
  props : [
    'src',
    'waveform',
    'highlight',
  ],
  emits : [
    'selected',
    'advanced'
  ],
  setup : function() {
    const tag_store = tagStore();
    return { tag_store };
  },
  watch : {
    highlight : {
      handler : function(new_highlight) {
       console.log(new_highlight);
       console.log("REDRAWING");
       if (new_highlight && new_highlight.what == 'point') {
         this.set_position(parseFloat(new_highlight.at));
       } else if (new_highlight && new_highlight.what == 'range') {
         this.set_position(parseFloat(new_highlight.from));
       }
       this.redraw();
      },
      deep : true,
    },
  },
  mounted : function() {
    this.$refs.actual_video.addEventListener('durationchange', (e) => {
      this.duration = e.target.duration;
      console.log("GOT TIME");
    });
    this.$refs.actual_video.addEventListener('playing', (e) => {
      this.started_playing();
    });
    this.$refs.actual_video.addEventListener('pause', (e) => {
      this.stopped_playing();
    });
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
    set_position : function(when) {
      this.$refs.actual_video.currentTime = when;
      this.update_position();
    },
    update_position : function() {
      let when = this.$refs.actual_video.currentTime;
      this.redraw();
      this.$emit('advanced', {
        'what' : 'point',
        'at' : when,
      });
    },
    started_playing : function() {
      this.playing_ctx = setInterval(() => {
        this.update_position();
      }, 1000 / FPS);
    },
    stopped_playing : function() {
      console.log("STOP");
      clearInterval(this.playing_ctx);
    },
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

      // the highlight
      ctx.strokeStyle = STROKE_STYLE_HIGHLIGHT;
      ctx.fillStyle = FILL_STYLE_HIGHLIGHT;
      if (this.highlight) {
        if (this.highlight.what == 'point') {
          let pos = parseInt((parseFloat(this.highlight.at) / this.duration) * w);
          console.log("pos="+pos);
          ctx.fillRect(pos, 0, 1, h);
        } else if (this.highlight.what == 'range') {
          let from = (parseFloat(this.highlight.from) / this.duration) * w;
          let to = (parseFloat(this.highlight.to) / this.duration) * w;
          console.log(`from=${from} to=${to}`);
          from = parseInt(from);
          to = parseInt(to);
          ctx.fillRect(from, 0, to-from, h);
          ctx.strokeRect(from, 0, to-from, h);
        }
      }

      // the current position
      ctx.strokeStyle = STROKE_STYLE;
      ctx.fillStyle = FILL_STYLE;
      ctx.fillRect(pos, 0, 2, h);
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
