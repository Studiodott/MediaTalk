<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section>
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
                <span>
                  {{ get_tag_name(tag_handle) }}
                </span>
              </span>
              <!-- and a dropdown for options -->
              <div
                class="tag">
                <o-dropdown
                  aria-role="list">
                  <template
                    v-slot:trigger>
                    <o-icon
                      icon="caret-down"
                      size="small">
                    </o-icon>
                  </template>
                  <o-dropdown-item
                    aria-role="listitem">{{ get_time_ago(tagging.created_at) }} by {{ get_user_key(tagging.user_handle) }}</o-dropdown-item>
                  <o-dropdown-item
                    v-if="tagging.comment && tagging.comment.length"
                    aria-role="listitem">comment <i>"{{ tagging.comment }}"</i></o-dropdown-item>
                  <o-dropdown-item
                    aria-role="listitem"></o-dropdown-item>
                  <o-dropdown-item
                    aria-role="listitem">
                    <o-button
                      size="small"
                      class="is-fullwidth"
                      icon-left="trash-can"
                      variant="danger"
                      @click="remove_tagging(tagging.handle)">
                      remove tagging
                    </o-button>
                  </o-dropdown-item>
                </o-dropdown>
              </div> <!-- class="tag" -->

            </div> <!-- individual tags, class="tags has-addons" -->

          </div> <!-- tagging list -->
        </div> <!-- tagging-box -->

        <!-- general options for this tag -->
        <div
          class="content field is-flex is-flex-direction-row is-justify-content-flex-end p-2">
          <o-button
            size="small"
            class="p-2"
            :class="tag_removal_safety[tag_handle] == true ? 'is-light' : ''"
            icon-left="trash-can"
            variant="danger"
            @click="remove_tag(tag_handle)">
            remove entire tag
          </o-button>
        </div>

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
  ],
  emits : [
    'select',
  ],
  mounted() {
    console.log(`taglist media_handle=${this.media_handle} collection=${this.collection}`);
  },
  methods : {
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
    },
    remove_tag : function(handle) {
      if (this.tag_removal_safety[handle] == true) {
        this.tag_removal_safety[handle] = false;
        return;
      }
      this.store.remove_tag(handle);
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
