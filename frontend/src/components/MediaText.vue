<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <pre
    id="actual_text">
  </pre>
</template>

<script>
import { tagStore } from '@/store/tag.js';

export default {
  name : 'MediaText',
  data : function() {
    return {
    };
  },
  props : [
    'src',
  ],
  setup : function() {
    const tag_store = tagStore();
    return { tag_store };
  },
  mounted : function() {
  },
  methods : {
  },
};
</script>
