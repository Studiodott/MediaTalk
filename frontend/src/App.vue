<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <NavBar
    v-if="store.logged_in"/>
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
                :filter_string="filter_string"
                @set_printable="set_report_printable"
                class="column is-full mb-6"
                />
              <UserList
                :users="store.search_results.users"/>
              <MediaPrint
                v-if="report_printable"
                class="column is-full mb-6"
                v-for="(media, media_index) in store.search_results.media"
                :key="media_index"
                v-bind="media"/>
              <MediaDisplay
                v-if="!report_printable"
                class="column is-full mb-6"
                v-for="(media, media_index) in store.search_results.media"
                :key="media_index"
                v-bind="media"/>
            </o-tab-item>

            <o-tab-item
              value="metatags"
              label="Metatags">
              <MetaTagList/>
            </o-tab-item>

            <o-tab-item
              v-if="store.get_is_admin()"
              value="admin"
              label="Admin">
              <Admin/>
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
import MediaPrint from "./components/MediaPrint.vue";
import FilterChooser from '@/components/FilterChooser.vue';
import NavBar from '@/components/NavBar.vue';
import UserList from '@/components/UserList.vue';
import MetaTagList from '@/components/MetaTagList.vue';
import Admin from '@/components/Admin.vue';

const ARG_EQ = '=';
const ARG_SEP = ',';

export default {
  name : 'App',
  components : {
    Test,
    MediaTag,
    MediaDisplay,
    MediaPrint,
    FilterChooser,
    NavBar,
    UserList,
    MetaTagList,
    Admin,
  },
  data : function() {
    return {
      active_tab : "tagging",
      report_printable : false,
      filter_string : '',
      boon : this.store.boon,
      auth : {
        email : '',
      },
    };
  },
  setup : function() {
    const store = Store();
    return {
      store,
    };
  },
  mounted : function() {
    if (this.store.logged_in) {
      this.load_world();
    }
  },
  methods : {
    set_report_printable : function(p) {
      console.log(`printable was=${this.report_printable} is=${p}`);
      this.report_printable = p;
    },
    process_hash : function() {
      let h = location.hash;
      if (h && h.length) {
        // skip over '#'
        h = h.substr(1);

        h.split(ARG_SEP).forEach((arg) => {
          let k, v;
          [ k, v ] = arg.split(ARG_EQ);
          switch (k) {
            case 'report':
                this.filter_string = v;
                this.active_tab = 'reporting';
                break;
            default:
                console.log(`error; unknown hash argument ${k}`);
                break;
          }
        });
      }
    },
    load_world : async function() {
      this.store.load().then(() => {
        // store load was fine, hookup websockets
        this.sockets.subscribe('tag_created', (data) => {
          this.store.tag_added(data);
        });
        this.sockets.subscribe('media_created', (data) => {
          this.store.media_added(data);
        });
        this.sockets.subscribe('user_created', (data) => {
          this.store.user_added(data);
        });
        this.sockets.subscribe('tagging_created', (data) => {
          this.store.tagging_added(data);
        });
        this.sockets.subscribe('tagging_removed', (data) => {
          this.store.tagging_removed(data);
        });
        this.sockets.subscribe('tag_removed', (data) => {
          this.store.tag_removed(data);
        });
        this.sockets.subscribe('metatag_created', (data) => {
          this.store.metatag_added(data);
        });
        this.sockets.subscribe('metatag_changed', (data) => {
          this.store.metatag_changed(data);
        });
        this.sockets.subscribe('metatag_removed', (data) => {
          this.store.metatag_removed(data);
        });
      }).then(() => {
        this.process_hash();
      }).catch((e) => {
        // TODO show, allow retry
      });
    },
    try_auth : async function() {
      this.store.try_auth(this.auth.email).then(() => {
        this.load_world();
      }).catch((e) => {
        // TODO show, allow retry
      });
    },
  },
};
</script>

<style scoped>
.login-screen {
  height: 100%;
}
</style>
