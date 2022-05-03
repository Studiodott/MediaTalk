<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
    <div>
      <div
        v-if="media_type == 'VIDEO'">
        <video
          controls>
          <source
            v-bind:src="url_original">
          No browser support for video :-(
        </video>
        <img
          v-if="url_description.length > 0"
          v-bind:src="url_description">
      </div>
      <div
        v-if="media_type == 'AUDIO'">
        <audio
          controls
          v-bind:src="url_original">
          No browser support for video :-(
        </audio>
        <img
          v-if="url_description.length > 0"
          v-bind:src="url_description">
      </div>
      <div
        v-if="media_type == 'IMAGE'">
        <img
          v-bind:src="url_original">
      </div>

      <p>{{ filename }}</p>
      <p><i>{{ description }}</i></p>
      <p>Existing tags:</p>
      <ul>
        <li
          v-for="(ti, ti_index) in tagging_store.getForMedia(handle)"
          :key="ti_index">
          {{ tag_store.get(ti.tag_handle).name }} at position {{ ti.position }}
        </li>
      </ul>
      <TagChooser/>
    </div>
  </div>
</template>

<script>
import { tagStore } from '@/store/tag.js';
import { taggingStore } from '@/store/tagging.js';
import TagChooser from '@/components/TagChooser.vue';

export default {
  name : 'Media',
  data : function() {
    return {
    };
  },
  components : {
    TagChooser,
  },
  setup : function() {
    const tagging_store = taggingStore();
    const tag_store = tagStore();
    return { tagging_store, tag_store };
  },
  props : [
    'handle',
    'filename',
    'media_type',
    'description',
    'url_original',
    'url_description',
  ],
  mounted : function() {
    console.log("mounted");
  },
};
</script>
