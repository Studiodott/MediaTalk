<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section>
    <o-collapse
      class="card"
      animation="slide"
      v-for="(taggings, tag_handle, tag_index) in getTaggingsForMedia"
      :key="tag_index"
      @open="collapse_open_on = tag_index; highlight(taggings, [])"
      @close="highlight([], [])"
      :open="collapse_open_on == tag_index">
      <template #trigger="props">
        <div
          class="card-header"
          role="button"
          :aria-controls="'contentIdForA11y5-' + tag_index"
          :aria-expanded="collapse_open_on">
          <p
              class="card-header-title">
            {{ get_tag_name(tag_handle) }}
          </p>
          <a
            class="card-header-icon">
            <o-icon
              :icon="props.open ? 'caret-up' : 'caret-down'">
            </o-icon>
          </a>
        </div>
      </template>
      <div class="card-content">
        <div class="content is-flex is-flex-direction-row is-flex-wrap-wrap tagging-box">
          <o-tooltip
            v-for="(tagging, tagging_index) in taggings"
            variant="primary"
            multiline>
            <span
              @click="highlight(taggings, [ tagging.handle ])"
              class="tag tagging"
              :style="'background: '+ tagging.colour + ';'">
              <o-icon icon="tag" size="small"></o-icon>
              <o-icon v-if="tagging.comment && tagging.comment.length" icon="comment" size="small"></o-icon>
            </span>
            <template v-slot:content>
              {{ get_time_ago(tagging.created_at) }} by {{ get_user_key(tagging.user_handle) }}
              <b
                v-if="tagging.comment && tagging.comment.length">
                comment "{{ tagging.comment }}"
              </b>
            </template>
          </o-tooltip>
        </div>

      </div>
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
