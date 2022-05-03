<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <o-field
    label="Choose tags">
    <o-inputitems
      v-model="chosenTags"
      autocomplete
      :allow-new="true"
      :data="filteredTags"
      field="name"
      @typing="getFilteredTags">
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
      filteredTags : this.tag_store.tags,
      //chosenTag : this.tag_store.tags[0],
    };
  },
  setup : function() {
    const tag_store = tagStore();
    return { tag_store };
  },
  mounted : function() {
  },
  methods : {
    getFilteredTags(search) {
      this.filteredTags = this.tag_store.tags.filter(tag => {
        return (
          tag.name.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },
  },
};
</script>
