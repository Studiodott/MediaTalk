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
        v-bind:src="waveform">
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
  ],
  emits : [
    'current_position',
  ],
  setup : function() {
    const tag_store = tagStore();
    return { tag_store };
  },
  mounted : function() {
    this.$refs.actual_video.addEventListener('durationchange', (e) => {
      this.duration = e.target.duration;
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

    nextTick(() => {
      this.$emit('current_position', {
        'what' :' timestamp',
        'time_seconds' : 0.0,
      });
    });
  },
  methods : {
    set_position : function(when) {
      console.log("setting time to "+when);
      this.$refs.actual_video.currentTime = when;
      this.update_position();
    },
    update_position : function() {
      let when = this.$refs.actual_video.currentTime;
      this.marker_set(when);
      this.$emit('current_position', {
        'what' : 'point',
        'time_seconds' : when,
      });
    },
    started_playing : function() {
      this.playing_ctx = setInterval(() => {
        this.update_position();
      }, 1000 / FPS);
    },
    stopped_playing : function() {
      clearInterval(this.playing_ctx);
      console.log("STOP");
    },
    timeline_resolve_click : function(mouse_x, mouse_y) {
      if (this.duration == undefined) {
        // we have no known duration, do nothing yet
        return;
      }
      console.log("click at x="+mouse_x+" y="+mouse_y);
      let canvas_pos = this.$refs.timing_timeline.getBoundingClientRect();
      mouse_x -= canvas_pos.left;
      mouse_y -= canvas_pos.top;
      console.log("click at x="+mouse_x+" y="+mouse_y+ " adjusted");
      let when = (mouse_x / canvas_pos.width) * this.duration;
      console.log("="+when + " of "+this.duration);
      return when;
    },
    marker_set : function(when) {
      if (this.duration == undefined) {
        // we have no known duration, do nothing yet
        return;
      }
      let w = this.$refs.timing_timeline.width;
      let h = this.$refs.timing_timeline.height;

      let pos = parseInt((when / this.duration) * w);

      let ctx = this.$refs.timing_timeline.getContext('2d');

      ctx.clearRect(0, 0, w, h);
      ctx.fillRect(pos, 0, 1, h);

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
