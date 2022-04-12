<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
    <div style="padding-top: 30px; width: 50%;">
      <p>This is {{ media_type }} with handle {{ handle }}</p>
      <p><i>{{ description }}</i></p>
      <TagChooser/>
    </div>
  </div>
</template>

<script>
import TagChooser from '@/components/TagChooser.vue';

export default {
  name : 'Media',
  data : function() {
    return {
    };
  },
  components : {
    TagChooser,
  },
  props : [ 'handle', 'media_type', 'description' ],
  mounted : function() {
    console.log("mounted");
  },
};
</script>
