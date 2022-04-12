<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <o-field label="Choose a tag:">
    <o-inputitems
      autocomplete
      v-model="chosenTags"
      :data="filteredTags"
      field="name"
      :allow-new="true"
      @typing="filterTags">
    </o-inputitems>
  </o-field>
</template>

<script>
import { tagStore } from '@/store/tag.js';

export default {
  name : 'TagChooser',
  data : function() {
    return {
      chosenTags : [],
      filteredTags : [],
    };
  },
  setup : function() {
    const tag_store = tagStore();
    return { tag_store };
  },
  mounted : function() {
    this.filteredTags = this.tag_store.tags;
  },
  methods : {
    filterTags : function(search) {
      this.filteredTags = this.tag_store.tags.filter(tag => {
        return tag.name.toLowerCase()
          .indexOf(search.toLowerCase()) >= 0;
      });
    },
  },
};
</script>
