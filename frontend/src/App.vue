<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section class="section">
    <div class="container">
      <div class="columns">
        <div
          class="column is-three-quarters is-flex is-flex-direction-column is-align-items-stretch">
          <Media
            class="column is-full mb-6"
            v-for="(media, media_index) in media_store.media"
            :key="media_index"
            v-bind="media"/>
        </div>
        <div
          class="column is-one-quarter">
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { tagStore } from '@/store/tag.js';
import { taggingStore } from '@/store/tagging.js';
import { mediaStore } from '@/store/media.js';
import Test from "./components/Test.vue";
import Media from "./components/Media.vue";
export default {
  name : 'App',
  components : {
    Test,
    Media
  },
  setup : function() {
    const media_store = mediaStore();
    media_store.load();
    const tag_store = tagStore();
    tag_store.load();
    const tagging_store = taggingStore();
    tagging_store.load();
    return {
      tag_store,
      media_store,
      tagging_store,
    };
  },
  sockets: {
    tag_created : function(data) {
      this.tag_store.add(data);
    },
    media_created : function(data) {
      this.media_store.add(data);
    },
    tagging_created : function(data) {
      this.tagging_store.add(data);
    },
  },
  mounted : function() {
    this.$socket.emit('debug', 'new client');
  },
};
</script>

<style>
</style>
