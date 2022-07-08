<!-- vim: set ts=2 sw=2 expandtab : -->
<template>

  <section>
    <div
      class="field">
      <o-radio
        v-model="selected"
        native-value="all">
        the entire document
      </o-radio>
    </div>
    <div
      class="field">
      <o-radio
        :disabled="!(selected_at)"
        v-model="selected"
        native-value="point">
        <p
          v-if="selected_at">
          the selected point
        </p>
        <p
          v-else>
          please select a specific point
        </p>
      </o-radio>
    </div>
    <div
      class="field">
      <o-radio
        :disabled="!(selected_from && selected_to)"
        v-model="selected"
        native-value="range">
        <p
          v-if="selected_from && selected_to">
          the selected range
        </p>
        <p
          v-else>
          please select a specific range
        </p>
      </o-radio>
    </div>
  </section>
  <o-field
    label="Apply these tags">
    <o-inputitems
      v-model="chosenTags"
      autocomplete
      :allow-new="true"
      :data="filteredTags"
      field="name"
      :allowDuplicates="false"
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
      :disabled="chosenTags.length == 0"
      @click="commit">
      save tag
    </o-button>
    <o-button
      class="is-danger"
      @click="reset">
      reset
    </o-button>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';
import PositionDisplay from '@/components/PositionDisplay.vue';

export default {
  name : 'TagChooserStatic',
  components : {
    PositionDisplay,
  },
  data : function() {
    return {
      chosenPoint : 'none',
      chosenTags : [],
      comment : '',
      filteredTags : this.store.live.tags,
      selected : 'all',
      selected_at : undefined,
      selected_from : undefined,
      selected_to : undefined,
    };
  },
  emits : [
    'cleared',
  ],
  props : {
    selection : {
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
    const store = Store();
    return { store };
  },
  mounted : function() {
  },
  watch : {
    selection : {
      handler : function(new_selected) {
        this.update_selected(new_selected);
      },
      deep : true,
    },
  },
  methods : {
    update_selected(new_selected) {
      if (new_selected == undefined || new_selected.what == 'all') {
        this.selected = 'all';
        this.selected_at = undefined;
        this.selected_from = undefined;
        this.selected_to = undefined;
      } else if (new_selected.what == 'point') {
        console.log("received point");
        this.selected = 'point';
        this.selected_at = new_selected.at;
        this.selected_from = undefined;
        this.selected_to = undefined;
      } else if (new_selected.what == 'range') {
        console.log("received range");
        this.selected = 'range';
        this.selected_from = new_selected.from;
        this.selected_to = new_selected.to;
        this.selected_at = undefined;
      }
    },
    getFilteredTags(search) {
      this.filteredTags = this.store.live.tags.filter(tag => {
        return (
          tag.name.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },
    reset() {
      this.update_selected(undefined);
      if (!this.store.runtime.sticky_tags)
        this.chosenTags = [];
      this.comment = '';
      this.$emit('cleared', undefined);
    },
    async commit() {
      let tag_handles = [];

      // for each chosen tag, look up the tag handle, creating
      // the tag if need be
      for (let i = 0; i < this.chosenTags.length; i++) {
        let chosen_tag = this.chosenTags[i];
        if (typeof chosen_tag === 'string') {
          let tag = this.store.live.tags.find((t) => t.name.toLowerCase() == chosen_tag.toLowerCase());
          if (!tag) {
            // actually a real tag
            console.log(`creating new tag for ${chosen_tag}`);
            tag = await this.store.create_tag(chosen_tag, '');
          }
          tag_handles.push(tag.handle);
        } else {
          tag_handles.push(chosen_tag.handle);
        }
      }

      let position = {};
      if (this.selected == 'all') {
        position['what'] = 'all';
      } else if (this.selected == 'point') {
        position['what'] = 'point';
        position['at'] = this.selected_at;
      } else if (this.selected == 'range') {
        position['what'] = 'range';
        position['from'] = this.selected_from;
        position['to'] = this.selected_to;
      }

      // tag them all on this media at this position
      await Promise.all(tag_handles.map(async (tag_handle) => {
        let tagging = this.store.create_tagging(this.media_handle,
          tag_handle, position, this.comment);
        console.log(tagging);
      }));

      this.reset();
    },
  },
};
</script>
