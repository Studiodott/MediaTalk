<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section>
    <o-collapse
      class="card"
      animation="slide"
      v-for="(taggings, tag_handle, tag_index) in getTaggingsForMedia"
      :key="tag_index"
      @open="collapse_open_on = tag_index; select_taggings(taggings)"
      @close="select_taggings([])"
      :open="collapse_open_on == tag_index">
      <template #trigger="props">
        <div
          class="card-header"
          role="button"
          :aria-controls="'contentIdForA11y5-' + tag_index"
          :aria-expanded="collapse_open_on">
          <p
              class="card-header-title">
            {{ store.get_tag(tag_handle).name }}
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
              @click="select_taggings([ tagging ])"
              class="tag tagging">
              {{ 'icon' }}
            </span>
            <template v-slot:content>
              by {{ tagging.user_handle }}
              at {{ tagging.created_at }}
            </template>
          </o-tooltip>
        </div>

      </div>
    </o-collapse>
  </section>
</template>

<script>
import { Store } from '@/store/store.js';

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
      this.$emit('select', taggings.map(ti => ti.position));
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
