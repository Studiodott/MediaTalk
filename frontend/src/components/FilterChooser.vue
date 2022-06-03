<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box">
    <o-field
      label="Show only">
      <o-checkbox
        v-for="mt in available_media_types"
        v-model="chosen_media_types"
        :native-value="mt">
        {{ mt.toLowerCase() }}
      </o-checkbox>
    </o-field>
    <o-field
      label="And only tags">
      <o-inputitems
        v-model="chosen_tags"
        :data="filtered_tags"
        autocomplete
        :allow-new="false"
        :open-on-focus="true"
        field="name"
        @typing="get_filtered_tags"/>
    </o-field>
    <o-button
      variant="primary"
      @click="update">
      Apply
    </o-button>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';

export default {
  name : 'FilterChooser',
  data : function() {
    return {
      available_media_types : [ 'TEXT', 'VIDEO', 'AUDIO', 'IMAGE' ],
      chosen_media_types : [ 'TEXT', 'VIDEO', 'AUDIO', 'IMAGE' ],
      chosen_tags : [],
      filtered_tags : this.store.live.tags,
    };
  },
  props : [
  ],
  setup : function() {
    const store = Store();
    return { store };
  },
  methods : {
    update : function() {
      this.store.search(this.chosen_media_types, this.chosen_tags.map(t => t.handle));
    },
    get_filtered_tags : function(search) {
      this.filtered_tags = this.store.live.tags.filter(tag => {
        return (
          tag.name.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },

  },
};
</script>
