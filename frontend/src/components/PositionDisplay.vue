<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <span
    v-if="position.what == 'timestamp'">
    {{ rounded(position.time_seconds) }} seconds
  </span>
</template>

<script>
export default {
  name : 'PositionDisplay',
  data : function() {
    return {
    };
  },
  props : [
    'position',
  ],
  methods : {
    rounded : function(f) {
      return f.toFixed(2);
    },
  },
  mounted : function() {
    console.log("mounted");
  },
};
</script>
