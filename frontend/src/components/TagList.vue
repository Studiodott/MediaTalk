<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section>

    <!--
      modal to show tagging details, shared over taggings (stuffed before opening)
    -->
    <o-modal
      v-model:active="modal_is_open">

      <div
        class="modal-card">
        <header
          class="modal-card-head">
          <p class="modal-card-title">Edit tagging</p>
        </header>
        <section
          class="modal-card-body">
          <o-field
            horizontal
            label="Created">
            <p>
              {{ get_time_ago(modal_ctx.created_at) }}
            </p>
          </o-field>
          <o-field
            horizontal
            label="By">
            <p>
              {{ get_user_key(modal_ctx.user_handle) }}
            </p>
          </o-field>
          <o-field
            horizontal
            label="Comment">
            <o-input
              @input="modal_is_changed = true"
              v-model="modal_ctx.comment">
            </o-input>
          </o-field>
          <o-field
            horizontal>
            <o-button
              :class="(modal_is_saving == true) ? 'is-loading' : ''"
              :disabled="!modal_is_changed"
              @click="modal_save"
              variant="primary">
              Save
            </o-button>
          </o-field>

          <hr/>

          <o-field
            label="Remove this tagging"
            horizontal>
            <o-button
              @click="remove_tagging(modal_ctx.handle)"
              icon-left="trash-can"
              variant="danger">
              Remove this tagging
            </o-button>
          </o-field>
          <o-field
            label="Remove entire tag (and all taggings)"
            horizontal>
            <o-button
              @click="remove_tag(modal_ctx.tag_handle)"
              icon-left="trash-can"
              variant="danger">
              Remove entire tag
            </o-button>
          </o-field>
        </section>
        <footer
          class="modal-card-foot is-justify-content-end">
          <o-button
            @click="modal_close">
            Close
          </o-button>
        </footer>
      </div>
    </o-modal>

    <o-collapse
      class="card"
      animation="slide"
      v-for="(taggings, tag_handle, tag_index) in getTaggingsForMedia"
      :key="tag_index"
      @open="collapse_open_on = tag_index; highlight(taggings, []); tag_removal_safety[tag_handle] = true;"
      @close="highlight([], [])"
      :open="collapse_open_on == tag_index">
      <template #trigger="props">
        <div
          class="card-header"
          role="button"
          :aria-controls="'contentIdForA11y5-' + tag_index"
          :aria-expanded="collapse_open_on">
          <a
            class="card-header-icon">
            <o-icon
              :icon="props.open ? 'caret-up' : 'caret-down'">
            </o-icon>
          </a>
          <p
            class="card-header-title">
            {{ get_tag_name(tag_handle) }}
          </p>
        </div>
      </template>
      <div class="card-content">
        <div
          class="content field is-grouped is-grouped-multiline tagging-box">

          <!-- tagging list -->
          <div
            class="control"
            v-for="(tagging, tagging_index) in taggings">

            <!-- individual taggings -->
            <div
              class="tags has-addons">
              <!-- each tagging is it's name -->
              <span
                class="tag"
                @click="highlight(taggings, [ tagging.handle ])"
                :style="'background: ' + tagging.colour + ';'">
                <o-icon
                  icon="tag"
                  size="small">
                </o-icon>
                <o-icon
                  v-if="tagging.comment && tagging.comment.length"
                  icon="comment"
                  size="small">
                </o-icon>
                <span
                  v-if="show_comments && tagging.comment">
                  {{ get_tag_name(tag_handle) }} <i>("{{ tagging.comment }}")</i>
                </span>
                <span
                  v-else>
                  {{ get_tag_name(tag_handle) }}
                </span>

              </span>
              <!-- and a dropdown for options -->
              <div
                class="tag">
                <o-icon
                  icon="pen"
                  size="small"
                  @click="modal_open(tagging)">
                </o-icon>

              </div> <!-- class="tag" -->

            </div> <!-- individual tags, class="tags has-addons" -->

          </div> <!-- tagging list -->
        </div> <!-- tagging-box -->

      </div> <!-- card content -->
    </o-collapse>
  </section>
</template>

<script>
import { Store } from '@/store/store.js';
import * as timeago from 'timeago.js';

export default {
  name : 'TagList',
  data : function() {
    return {
      modal_is_open : false,
      modal_is_changed : false,
      modal_is_saving : false,
      modal_ctx : {},
      collapse_open_on : null,
      tag_removal_safety : {},
    };
  },
  components : {
  },
  setup : function() {
    const store = Store();
    return { store };
  },
  props : [
    'media_handle',
    'collection',
    'show_comments',
  ],
  emits : [
    'select',
  ],
  mounted() {
    console.log(`taglist media_handle=${this.media_handle} collection=${this.collection}`);
  },
  methods : {
    modal_open : function(tagging) {
      let keys = [ 'comment', 'created_at', 'user_handle', 'handle', 'tag_handle' ];
      this.modal_ctx = {};
      keys.forEach((k) => {
        this.modal_ctx[k] = tagging[k];
      });
      this.modal_is_open = true;
    },
    modal_close : function() {
      this.modal_is_open = false;
      this.modal_ctx = {};
    },
    modal_save : function() {
      this.modal_is_saving = true;
      this.store.tagging_change(this.modal_ctx.handle, this.modal_ctx.comment)
        .then(() => { this.modal_is_saving = false; this.modal_is_changed = false; })
        .catch(() => { this.modal_is_saving = false; });
    },
    select_taggings : function(taggings) {
      console.log(`selected ${taggings.length} taggings`);
      this.$emit('select', taggings); //.map(ti => ti.position));
    },
    highlight: function(taggings, emphasis) {
      this.$emit('select', { taggings : taggings, emphasis: emphasis });
    },

    get_tag_name : function(tag_handle) {
      let tag = this.store.get_tag(tag_handle);
      if (!tag) {
        console.log(`oddity, can't find tag for handle=${tag_handle}`);
        return 'not found';
      }
      return tag.name;
    },
    get_user_key : function(user_handle) {
      let user = this.store.get_user(user_handle);
      if (!user) {
        console.log(`oddity, can't find user keyfor handle=${user_handle}`);
        return 'not found';
      }
      return user.key;
    },
    get_time_ago : function(ts) {
      return timeago.format(ts);
    },
    remove_tagging : function(handle) {
      this.store.remove_tagging(handle);
      this.modal_close();
    },
    remove_tag : function(handle) {
      this.store.remove_tag(handle);
      this.modal_close();
      this.highlight([], []);
    },
  },
  computed : {
    getTaggingsForMedia() {
      let taggings = [];
      let taggings_by_tag_handle = {};

      if (this.collection == 'live')
        taggings = this.store.get_taggings_for_media(this.media_handle);
      else if (this.collection == 'search')
        taggings = this.store.search_results_get_taggings_for_media(this.media_handle);

      taggings.forEach((ti) => {
        if (!(ti.tag_handle in taggings_by_tag_handle)) {
          taggings_by_tag_handle[ti.tag_handle] = [];
        }
        taggings_by_tag_handle[ti.tag_handle].push(ti);
      });

      return taggings_by_tag_handle;
    },
  },
};
</script>

<style scoped>
.tagging {
  margin-left: 0.275rem;
  margin-bottom: calc(0.275rem - 1px);
  font-size: 0.9em;
  height: calc(2em - 1px);
}
.tagging-box {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}
.card-content {
  padding: 0;
}
</style>
