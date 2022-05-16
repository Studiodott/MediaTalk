<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="is-flex is-flex-direction-column">
    <div
      class="is-flex is-flex-direction-row is-align-items-baseline">
      <o-button
        @click="set_selection_all"
        class="is-small is-light is-primary is-fullwidth">
        entire document
      </o-button>
    </div>
    <div
      class="is-flex is-flex-direction-row is-align-items-baseline mt-2">
      <o-button
        @click="set_selection_point"
        :disabled="current_position == undefined"
        class="is-small is-light is-primary is-fullwidth">
        exactly here
      </o-button>
    </div>
    <div
      class="is-flex is-flex-direction-row is-align-items-baseline mt-2">
      <o-button
        @click="set_selection_range_start"
        :disabled="current_position == undefined"
        class="is-small is-light is-primary is-fullwidth">
        between here
      </o-button>
      <o-button
        @click="set_selection_range_stop"
        :disabled="current_position == undefined"
        class="is-small is-light is-danger is-fullwidth">
        and here
      </o-button>
    </div>

  </div>

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
  <div
    class="is-flex is-flex-direction-row is-justify-content-space-between">
    <o-button
      class="is-primary"
      :disabled="chosenTags.length == 0 || current_position == null"
      @click="commit">
      save tag
    </o-button>
    <o-button
      class="is-danger"
      :disabled="chosenTags.length == 0 || current_position == null"
      @click="commit">
      reset
    </o-button>
  </div>

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
      chosenPoint : 'none',
      chosenTags : [],
      comment : '',
      filteredTags : this.tag_store.tags,
    };
  },
  props : {
    current_position : {
      type : Object,
      default() {
        return undefined;
      }
    },
    media_handle : {
      type : String,
      required : true,
    },
  },
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
