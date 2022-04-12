<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <o-field
    label="select a tag">
    <o-select
      v-model="chosenTag">
      <option
        v-for="(tag, tag_index) in tag_store.tags"
        :key="tag_index">
        {{ tag.name }} <i>{{ tag.description }}</i>
      </option>
    </o-select>
  </o-field>
</template>

<script>
import { tagStore } from '@/store/tag.js';

export default {
  name : 'TagChooser',
  data : function() {
    return {
      chosenTag : this.tag_store.tags[0],
    };
  },
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
