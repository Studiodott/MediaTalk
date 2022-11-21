<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <NavBar
    @show="show"
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
          :disabled="auth.email.length == 0"
          variant="primary">Let me in!</o-button>
      </div>
    </div>
  </section>

  <section
    class="section"
    v-if="store.logged_in">
    <div
      class="container">

      <div
        class="columns is-multiline">

        <o-collapse
          v-if="active_pane == 'tagging'"
          class="card column is-full mt-6 fake-columns"
          animation="slide"
          :open="media_collection_open"
          @open="media_collection_open = true"
          @close="media_collection_open = false">
          <template #trigger="props">
            <div
              class="card-header"
              role="button">
              <a
                class="card-header-icon">
                <o-icon
                  :icon="media_collection_open ? 'caret-up' : 'caret-down'">
                </o-icon>
              </a>
              <p
                class="card-header-title">
                Media collection
              </p>
            </div>
          </template>
          <div
            class="card-content">
            <div
              class="content">
              <div
                class="field is-grouped is-grouped-multiline">
                <div
                  class="control"
                  v-for="(media, media_index) in store.live.media">
                  <div
                    @click="scroll_to_media(media_index)"
                    class="tags has-addons are-medium">
                    <span
                      class="tag">
                      <o-icon
                        :icon="get_icon_for_type(media.media_type)">
                      </o-icon>
                    </span>
                    <span
                      class="tag">
                      {{ media.description }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </o-collapse>

        <MediaTag
          v-if="active_pane == 'tagging'"
          class="column is-full mt-6 fake-columns"
          v-for="(media, media_index) in store.live.media"
          ref="media"
          :key="media.handle"
          v-bind="media"/>

        <FilterChooser
          v-if="active_pane == 'reporting'"
          :filter_string="filter_string"
          @set_printable="set_report_printable"
          class="column is-full mt-6"
          />
        <UserList
          class="column is-full mt-6"
          v-if="active_pane == 'reporting'"
          :users="store.search_results.users"/>
        <MediaPrint
          v-if="active_pane == 'reporting' && report_printable"
          class="column is-full mt-6 fake-columns"
          v-for="(media, media_index) in store.search_results.media"
          :key="media.handle"
          v-bind="media"/>
        <MediaDisplay
          v-if="active_pane == 'reporting' && !report_printable"
          class="column is-full mt-6 fake-columns"
          v-for="(media, media_index) in store.search_results.media"
          :key="media.handle"
          v-bind="media"/>

        <MetaTagList
          v-if="active_pane == 'metatags'"
          value="metatags"
          class="column is-full mt-6"
          label="Metatags">
        </MetaTagList>

        <Admin
          v-if="active_pane == 'admin' && store.get_is_admin()"
          value="admin"
          class="column is-full mt-6"
          label="Admin">
        </Admin>

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
      active_pane : "tagging",
      media_collection_open : false,
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
    scroll_to_media : function(i) {
      this.$refs.media[i].$el.scrollIntoView({ behavior : 'smooth', block : 'end' });
    },
    // a nice icon for this media type
    get_icon_for_type : function(media_type) {
      console.log(`media_type=${media_type}`);
      switch (media_type) {
        case 'VIDEO':
            return 'video';
            break;
        case 'AUDIO':
            return 'microphone';
            break;
        case 'TEXT':
            return 'file-lines';
            break;
        case 'IMAGE':
            return 'camera';
            break;
        default:
            return 'question';
            break;
      }
    },
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
        this.sockets.subscribe('media_changed', (data) => {
          this.store.media_changed(data);
        });
        this.sockets.subscribe('media_removed', (data) => {
          this.store.media_removed(data);
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
        this.sockets.subscribe('tagging_changed', (data) => {
          this.store.tagging_changed(data);
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
    show : function(what) {
      console.log("want me to show "+what);
      this.active_pane = what;
    },
  },
};
</script>

<style scoped>
.login-screen {
  height: 100%;
}
.fake-columns {
  margin-left: -0.75rem;
  margin-right: -0.75rem;
  margin-top: -0.75rem;
}
</style>
