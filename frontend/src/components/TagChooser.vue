<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <o-field
    label="At">
    <PositionDisplay
      v-if="current_position"
      :position="current_position"/>
  </o-field>
  <o-field
    label="Apply these tags">
    <o-inputitems
      v-model="chosenTags"
      autocomplete
      :allow-new="true"
      :data="filteredTags"
      field="name"
      :allowDuplicates="true"
      @typing="getFilteredTags">
    </o-inputitems>
  </o-field>
  <o-field
    label="With comment">
    <o-input
      :disabled="chosenTags.length == 0"
      v-model="comment"/>
  </o-field>
  <o-button
    :disabled="chosenTags.length == 0 || current_position == null"
    @click="commit">
    Save!
  </o-button>
</template>

<script>
import { tagStore } from '@/store/tag.js';
import { taggingStore } from '@/store/tagging.js';
import PositionDisplay from '@/components/PositionDisplay.vue';

export default {
  name : 'TagChooser',
  components : {
    PositionDisplay,
  },
  data : function() {
    return {
      chosenTags : [],
      comment : '',
      filteredTags : this.tag_store.tags,
    };
  },
  props : [
    'current_position',
    'media_handle',
  ],
  setup : function() {
    const tag_store = tagStore();
    const tagging_store = taggingStore();
    return { tag_store, tagging_store };
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
    async commit() {
      let tag_handles = [];

      // for each chosen tag, look up the tag handle, creating
      // the tag if need be
      for (let i = 0; i < this.chosenTags.length; i++) {
        let chosen_tag = this.chosenTags[i];
        if (typeof chosen_tag === 'string') {
          let new_tag = await this.tag_store.create(chosen_tag, '');
          tag_handles.push(new_tag.handle);
        } else {
          tag_handles.push(chosen_tag.handle);
        }
      }

      // tag them all on this media at this position
      await Promise.all(tag_handles.map(async (tag_handle) => {
        let tagging = this.tagging_store.create(this.media_handle,
          tag_handle, this.current_position);
        console.log(tagging);
      }));

    },
  },
};
</script>
