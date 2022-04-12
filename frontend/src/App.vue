<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    v-for="(m, m_index) in media_store.media" :key="m_index">
    <Media v-bind="m"/>
  </div>
</template>

<script>
import { tagStore } from '@/store/tag.js';
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
    const tag_store = tagStore();
    tag_store.load();
    const media_store = mediaStore();
    media_store.load();
    return {
      tag_store,
      media_store,
    };
  },
  sockets: {
    tag_created : function(data) {
      console.log('tag_created(data='+data+')');
      this.tag_store.add(data);
    },
    media_created : function(data) {
      this.media_store.add(data);
    },
  },
  mounted : function() {
    this.$socket.emit('debug', 'new client');
  },
};
</script>

<style>
</style>
