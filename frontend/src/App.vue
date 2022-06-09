<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <section
    class="login-screen section"
    v-if="store.logged_in == false">
    <div
      class="flex is-justify-content-center is-align-items-center login-box">
      <div
        class="box">
        <div class="field">
          <label
            class="label">
            Your email address?
          </label>
          <div class="control">
            <input
              v-model="auth.email"
              class="input"
              type="text">
          </div>
        </div>
        <o-button
          @click="try_auth"
          variant="primary">Let me in!</o-button>
      </div>
    </div>
  </section>

  <section
    class="section"
    v-if="store.logged_in">
    <div
      v-if="store.logged_in"
      class="container">
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
import { api_target } from '@/config.js';
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
      boon : this.store.boon,
      auth : {
        email : '',
      },
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
    user_created : function(data) {
      this.store.add_user(data);
    },
    tagging_created : function(data) {
      console.log(`TAGGING data=${data}`);
      this.store.add_tagging(data);
    },
  },
  mounted : function() {
    this.$socket.emit('debug', 'new client');
  },
  methods : {
    foob : async function() {
      await fetch(api_target + '/api/login', { method : 'POST' });
    },
    try_auth : async function() {
      this.auth.trying = true;
      await this.store.try_auth(this.auth.email);
      this.auth.trying = false;
    },
  },
};
</script>

<style scoped>
.login-screen {
  height: 100%;
}
</style>
