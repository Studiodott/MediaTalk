<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section>
    <o-field
      label="At">
      <div hidden></div>
    </o-field>
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
        :disabled="!last_advance"
        v-model="selected"
        native-value="point">
        <div
          class="is-flex is-flex-direction-row is-justify-content-space-around">
          <div
            class="is-flex is-flex-direction-column is-align-items-center is-fullwidth">
            <p>at precisely</p>
            <p>{{ selected_at }}</p>
            <o-button
              :class="{ 'is-light' : selected_at_locked }"
              class="is-small is-primary is-fullwidth"
              @click="toggle_lock_point_at">
              {{ selected_at_locked ? 'unlock' : 'lock' }}
            </o-button>
          </div>
        </div>
      </o-radio>
    </div>
    <div
      class="field">
      <o-radio
        :disabled="!last_advance"
        v-model="selected"
        native-value="range">
        <div
          class="is-flex is-flex-direction-row is-justify-content-space-around">
          <div
            class="is-flex is-flex-direction-column is-align-items-center is-fullwidth">
            <p>from</p>
            <p>{{ selected_from }}</p>
            <o-button
              :class="{ 'is-light' : selected_from_locked }"
              class="is-small is-primary is-fullwidth"
              @click="toggle_lock_range_from">
              {{ selected_from_locked ? 'unlock' : 'lock' }}
            </o-button>
          </div>
          <div
            class="is-flex is-flex-direction-column is-align-items-center is-fullwidth">
            <p>to</p>
            <p>{{ selected_to }}</p>
            <o-button
              :class="{ 'is-light' : selected_to_locked }"
              class="is-small is-primary"
              @click="toggle_lock_range_to">
              {{ selected_to_locked ? 'unlock' : 'lock' }}
            </o-button>
          </div>
        </div>
      </o-radio>
    </div>
  </section>
  <o-field>
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

      selected : 'all',
      selected_at : undefined,
      selected_at_locked : false,
      selected_to : undefined,
      selected_to_locked : false,
      selected_from : undefined,
      selected_from_locked : false,
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
    last_advance : {
      type : Object,
      required : false,
      default() {
        return undefined;
      },
    },
  },
  setup : function() {
    const tag_store = tagStore();
    const tagging_store = taggingStore();
    return { tag_store, tagging_store };
  },
  mounted : function() {
  },
  watch : {
    last_advance : {
      handler : function(new_advance) {
        if (!new_advance) {
          this.selected = 'all';
          this.selected_at_locked = false;
          this.selected_from_locked = false;
          this.selected_to_locked = false;
        }
        if (!this.selected_at_locked) {
          this.selected_at = new_advance.at.toFixed(2);
        }
        if (!this.selected_from_locked) {
          this.selected_from = new_advance.at.toFixed(2);
        }
        if (!this.selected_to_locked) {
          this.selected_to = new_advance.at.toFixed(2);
        }
      },
      deep : true,
    },
  },

  methods : {
    toggle_lock_point_at() {
      this.selected_at_locked = !this.selected_at_locked;
      this.selected = 'point';
    },
    toggle_lock_range_from() {
      this.selected_from_locked = !this.selected_from_locked;
      this.selected = 'range';
    },
    toggle_lock_range_to() {
      this.selected_to_locked = !this.selected_to_locked;
      this.selected = 'range';
    },
    getFilteredTags(search) {
      this.filteredTags = this.tag_store.tags.filter(tag => {
        return (
          tag.name.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },
    reset() {
      this.chosenTags = [];
      this.comment = '';
      this.selected = 'all';
      this.selected_at_locked = false;
      this.selected_from_locked = false;
      this.selected_to_locked = false;
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

      // build a transmittable position object
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
        let tagging = this.tagging_store.create(this.media_handle,
          tag_handle, position);
        console.log(tagging);
      }));

      this.reset();
    },
  },
};
</script>

<style>
span.control-label {
  width: 100%;
}
.radio {
  width: 100%;
}
</style>
