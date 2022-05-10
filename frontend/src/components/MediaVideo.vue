<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <video
    id="actual_video"
    ref="actual_video"
    controls>
    <source
      v-bind:src="src">
    No browser support for video :-(
  </video>
  <img
    id="waveform"
    v-if="waveform.length > 0"
    v-bind:src="waveform">

</template>

<script>
import { nextTick } from 'vue';
import { tagStore } from '@/store/tag.js';

export default {
  name : 'MediaVideo',
  data : function() {
    return {
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
    this.$refs.actual_video.addEventListener('timeupdate', (e) => {
      this.$emit('current_position', {
        'what' : 'timestamp',
        'time_seconds' : e.target.currentTime,
      });
    });

    nextTick(() => {
      this.$emit('current_position', {
        'what' :' timestamp',
        'time_seconds' : 0.0,
      });
    });
  },
  methods : {
  },
};
</script>
