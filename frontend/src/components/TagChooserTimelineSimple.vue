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
        v-model="mode"
        native-value="all">
        the entire document
      </o-radio>
    </div>
    <div
      class="field">
      <o-radio
        :disabled="!advance"
        v-model="mode"
        native-value="timed">
        <button
          class="button is-fullwidth is-primary"
          ref="selection_button">
          this part
        </button>
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
import { Store } from '@/store/store.js';
import PositionDisplay from '@/components/PositionDisplay.vue';

const CLICK_MS = 300;

export default {
  name : 'TagChooserTimelineSimple',
  components : {
    PositionDisplay,
  },
  data : function() {
    return {
      chosenTags : [],
      comment : '',
      filteredTags : this.store.tags,

      mode : 'all',

      selected : undefined,
      selected_at : undefined,
      selected_from : undefined,
      selected_to : undefined,

      press_ctx : undefined,
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
    advance : {
      type : Object,
      required : false,
      default() {
        return undefined;
      },
    },
  },
  emits : [
    'selected',
  ],
  setup : function() {
    const store = Store();
    return { store };
  },
  mounted : function() {
    this.$refs.selection_button.addEventListener('mousedown', (e) => {

      // don't, if we've never seen an advance
      if (!this.advance)
        return;

      this.mode = 'timed';

      // consider it a point until we've hit the click timeout
      this.selected = 'point';
      this.selected_at = this.advance.at.toFixed(2);

      this.press_ctx = setTimeout(() => {
        // after the timeout, the click turns into a long click,
        // signifying the user wants a range rather than a point
        this.selected = 'range';
        this.selected_from = this.selected_at;
        this.selected_to = null;

        this.press_ctx = undefined;

        this.emit_selected();
      }, CLICK_MS);

      this.emit_selected();

    });
    this.$refs.selection_button.addEventListener('mouseup', (e) => {

      // don't, if we've never seen an advance
      if (!this.advance)
        return;

      if (this.press_ctx) {
        // click timeout still running, this is a click
        if (this.selected != 'point') {
          console.log(`inconcistency; timing indicates point selection but I have ${this.selection}`);
        }
        clearTimeout(this.press_ctx);
        this.press_ctx = undefined;
      } else {
        // the timer expired, turning this click into a long click
        // nothing to do but note the end time
        if (this.selected != 'range') {
          console.log(`inconcistency; timing indicates range selection but I have ${this.selection}`);
        }
        this.selected_to = this.advance.at.toFixed(2);
      }

      this.emit_selected();
    });
  },
  watch : {
    mode : function(new_mode) {
      this.emit_selected();
    },
  },
  methods : {
    emit_selected() {
      let arg = undefined;

      if (this.mode == 'timed') {
        if (this.selected == 'point') {
          arg = {
            what : 'point',
            at : this.selected_at,
          };
        } else if (this.selected == 'range') {
          arg = {
            what : 'range',
            from : this.selected_from,
            to : this.selected_to,
          };
        }
      }

      this.$emit('selected', arg);
    },
    getFilteredTags(search) {
      this.filteredTags = this.store.live.tags.filter(tag => {
        return (
          tag.name.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },
    reset() {
      this.chosenTags = [];
      this.comment = '';
      this.mode = 'all';
      this.selected = undefined;
      this.selected_at = undefined;
      this.selected_to = undefined;
      this.selected_from = undefined;
      this.emit_selected();
    },
    async commit() {
      let tag_handles = [];

      // for each chosen tag, look up the tag handle, creating
      // the tag if need be
      for (let i = 0; i < this.chosenTags.length; i++) {
        let chosen_tag = this.chosenTags[i];
        if (typeof chosen_tag === 'string') {
          let new_tag = await this.store.create_tag(chosen_tag, '');
          tag_handles.push(new_tag.handle);
        } else {
          tag_handles.push(chosen_tag.handle);
        }
      }

      // build a transmittable position object
      let position = {};
      if (this.mode == 'all') {
        position['what'] = 'all';
      } else {
        if (this.selected == 'point') {
          position['what'] = 'point';
          position['at'] = this.selected_at;
        } else if (this.selected == 'range') {
          position['what'] = 'range';
          position['from'] = this.selected_from;
          position['to'] = this.selected_to;
        }
      }

      // tag them all on this media at this position
      await Promise.all(tag_handles.map(async (tag_handle) => {
        let tagging = this.store.create_tagging(this.media_handle,
          tag_handle, position, this.comment);
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
