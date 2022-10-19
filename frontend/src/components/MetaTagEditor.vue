<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
    <div
      class="is-flex is-justify-content-space-between">
      <h3
        class="title">
        {{ metatag.name }}
      </h3>
      <o-button
        @click="remove_metatag(metatag.handle)"
        variant="danger">
        <o-icon
          icon="trash-can">
        </o-icon>
      </o-button>
    </div>

    <div
      class="content field is-grouped is-grouped-multiline">
      <div
        class="control"
        v-for="(tag, tag_index) in get_tags_existing">
        <div
          class="tags has-addons">
          <span
            class="tag is-primary is-light">
            <o-icon
              icon="tag"
              size="small">
            </o-icon>
            <span>
              {{ tag.name }}
           </span>
          </span>
          <span
            class="tag">
            <o-icon
              @click="store.metatag_remove_tag(metatag.handle, tag.handle)"
              icon="trash-can"
              size="small">
            </o-icon>
          </span>
        </div>
      </div>
    </div>

    <div
      class="content field is-grouped is-grouped-multiline">
      <div
        class="control"
        v-for="(tag, tag_index) in get_tags_remaining">
        <div
          class="tags has-addons">
          <span
            class="tag is-light">
            <o-icon
              icon="tag"
              size="small">
            </o-icon>
            <span>
              {{ tag.name }}
           </span>
          </span>
          <span
            class="tag">
            <o-icon
              @click="store.metatag_add_tag(metatag.handle, tag.handle)"
              icon="plus"
              size="small">
            </o-icon>
          </span>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { Store } from '@/store/store.js';

function cmp_strings(l, r) {
  if (l == r)
    return 0;
  if (l < r)
    return -1;
  return 1;
}

export default {
  name : 'MetaTagEditor',
  data : function() {
    return {
    };
  },
  props : [
    'metatag',
  ],
  setup : function() {
    const store = Store();
    return { store };
  },
  mounted : function() {
  },
  methods : {
    remove_metatag(handle) {
      this.store.remove_metatag(handle);
    },
  },
  computed: {
    get_tags_existing() {
      return this.store.live.tags.slice().sort((l, r) => { return cmp_strings(l.name, r.name); }).filter((e_tag) => this.metatag.tag_handles.includes(e_tag.handle));
    },
    get_tags_remaining() {
      return this.store.live.tags.slice().sort((l, r) => { return cmp_strings(l.name, r.name); }).filter((e_tag) => !this.metatag.tag_handles.includes(e_tag.handle));
    },
  },
};
</script>

<style scoped>

</style>
