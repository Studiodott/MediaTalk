<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section class="section">
    <div class="container">
      <div class="columns">
        <div
          class="column is-three-quarters is-flex is-flex-direction-column is-align-items-stretch">
          <o-tabs
            position="centered"
            v-model="active_tab">
            <o-tab-item
              value="tagging"
              label="Tagging">

              <MediaTag
                class="column is-full mb-6"
                v-for="(media, media_index) in store.live.media"
                :key="media_index"
                v-bind="media"/>

            </o-tab-item>

            <o-tab-item
              value="reporting"
              label="Reporting">
              <FilterChooser
                class="column is-full mb-6"
                />
              <MediaDisplay
                class="column is-full mb-6"
                v-for="(media, media_index) in store.search_results.media"
                :key="media_index"
                v-bind="media"/>

            </o-tab-item>
          </o-tabs>
        </div>
        <div
          class="column is-one-quarter">
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { Store } from '@/store/store.js';
import Test from "./components/Test.vue";
import MediaTag from "./components/MediaTag.vue";
import MediaDisplay from "./components/MediaDisplay.vue";
import FilterChooser from '@/components/FilterChooser.vue';
export default {
  name : 'App',
  components : {
    Test,
    MediaTag,
    MediaDisplay,
    FilterChooser,
  },
  data : function() {
    return {
      active_tab : "tagging",
    };
  },
  setup : function() {
    const store = Store();
    store.load();
    return {
      store,
    };
  },
  sockets: {
    tag_created : function(data) {
      this.store.add_tag(data);
    },
    media_created : function(data) {
      this.store.add_media(data);
    },
    tagging_created : function(data) {
      this.store.add_tagging(data);
    },
  },
  mounted : function() {
    this.$socket.emit('debug', 'new client');
  },
};
</script>

<style>
</style>
