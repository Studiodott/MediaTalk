<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
    <div style="padding-top: 30px; width: 50%;">
      <p>This is {{ media_type }} with handle {{ handle }}</p>
      <p><i>{{ description }}</i></p>
      <p>Existing tags:</p>
      <ul>
        <li
          v-for="(ti, ti_index) in tagging_store.getForMedia(handle)"
          :key="ti_index">
          {{ tag_store.get(ti.tag_handle).name }} at position {{ ti.position }}
        </li>
      </ul>
      <TagChooser/>
    </div>
  </div>
</template>

<script>
import { tagStore } from '@/store/tag.js';
import { taggingStore } from '@/store/tagging.js';
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
  setup : function() {
    const tagging_store = taggingStore();
    const tag_store = tagStore();
    return { tagging_store, tag_store };
  },
  props : [ 'handle', 'media_type', 'description' ],
  mounted : function() {
    console.log("mounted");
  },
};
</script>
