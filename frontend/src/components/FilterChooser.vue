<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column">
      <div
        class="is-flex is-flex-direction-row is-justify-content-space-between">
        <o-field
          label="Show only">
          <o-checkbox
            v-for="mt in available_media_types"
            v-model="chosen_media_types"
            :native-value="mt">
            {{ mt.toLowerCase() }}
          </o-checkbox>
        </o-field>
        <o-button
          variant="info"
          @click="show_link">
          Share this filter
        </o-button>
      </div>
      <o-field
        label="And only metatags">
        <o-inputitems
          v-model="chosen_metatags"
          :data="filtered_metatags"
          autocomplete
          :allow-new="false"
          :open-on-focus="true"
          field="name"
          @typing="get_filtered_metatags"/>
      </o-field>

      <o-field
        label="And only tags">
        <o-inputitems
          v-model="chosen_tags"
          :data="filtered_tags"
          autocomplete
          :allow-new="false"
          :open-on-focus="true"
          field="name"
          @typing="get_filtered_tags"/>
      </o-field>
      <div
        class="is-flex is-flex-direction-row is-justify-content-end">
        <o-field>
          <o-switch
            v-model="tag_handles_and">
            Only show media with all of these
          </o-switch>
        </o-field>
      </div>
      <o-field
        label="Tagged by">
        <o-inputitems
          v-model="chosen_users"
          :data="filtered_users"
          autocomplete
          :allow-new="false"
          :open-on-focus="true"
          field="key"
          @typing="get_filtered_users"/>
      </o-field>
      <div
        class="is-flex is-flex-direction-row is-justify-content-end">
        <o-field>
          <o-switch
            v-model="user_handles_and">
            Only show media with all of these
          </o-switch>
        </o-field>
      </div>
      <o-field>
        <o-switch
          @input="$emit('set_printable', !printable)"
          v-model="printable">
          Printable
        </o-switch>
      </o-field>
      <div
        class="is-flex is-flex-direction-row is-justify-content-end">
        <o-button
          variant="primary"
          @click="update">
          Apply
        </o-button>
      </div>

      <o-modal
        :active="showing_link"
        contentClass="modal-card"
        @close="showing_link = false">
        <header
          class="modal-card-head">
          <p
            class="modal-card-title">
            Share this report
          </p>
        </header>
        <section
          class="modal-card-body">
          <div
            class="field">
            <p>
              Everyone with access can see this selection with this link
            </p>
            <div
              class="control">
              <input class="input" type="text" :value="current_link"/>
            </div>
          </div>
        </section>
        <footer
          class="modal-card-foot">
          <o-button
            @click="showing_link = false">
            Got it!
          </o-button>
        </footer>
      </o-modal>
    </div>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';

const FILTER_STRING_EQ = ':';
const FILTER_STRING_SEP = ';';

export default {
  name : 'FilterChooser',
  data : function() {
    return {
      available_media_types : [ 'TEXT', 'VIDEO', 'AUDIO', 'IMAGE' ],
      chosen_media_types : [ 'TEXT', 'VIDEO', 'AUDIO', 'IMAGE' ],
      chosen_tags : [],
      filtered_tags : this.store.live.tags,
      chosen_metatags : [],
      filtered_metatags : this.store.live.metatags,
      chosen_users : [],
      filtered_users : this.store.live.users,
      tag_handles_and : false,
      user_handles_and : false,
      printable : false,
      showing_link : false,
      current_link : '',
    };
  },
  emits : [
    'set_printable',
  ],
  props : [
    'filter_string',
  ],
  watch : {
    filter_string : function(f) {
      let seen_media_type = false;
      let tags = [];
      let metatags = [];
      let users = [];

      try {
        f.split(FILTER_STRING_SEP).forEach((arg) => {
          let k, v;
          [ k, v ] = arg.split(FILTER_STRING_EQ);

          switch (k) {
            case 'mt':
                if (!seen_media_type) {
                  // if we start seeing these, we need to start with
                  // a fresh slate
                  this.chosen_media_types = [];
                  seen_media_type = true;
                }
                this.chosen_media_types.push(v);
                break;
            case 't':
                let t = this.store.get_tag(v);
                tags.push(t);
                break;
            case 'mtt':
                let mtt = this.store.get_metatag(v);
                metatags.push(mtt);
                break;
            case 'u':
                let u = this.store.get_user(v);
                users.push(u);
                break;
            case 'p':
                this.printable = v == 'true';
                this.$emit('set_printable', this.printable);
                break;
            case 'ta':
                this.tag_handles_all = v == 'true';
                break;
            case 'ua':
                this.tag_handles_all = v == 'true';
                break;
            default:
                console.log(`error; don't know filtering argument ${k}`);
                break;
          }
        });
      } catch (e) {
        console.log(`error; while processing filters: ${e}`);
      }

      // Oruga's inputlist doesn't notice pushed, so xchg entire list
      if (users.length) {
        this.chosen_users = users;
      }
      if (tags.length) {
        this.chosen_tags = tags;
      }
      if (metatags.length) {
        this.chosen_metatags = metatags;
      }

      // and get results
      this.update();
    },
  },
  setup : function() {
    const store = Store();
    return { store };
  },
  methods : {
    build_filter_string : function() {
      let out = [];
      out = out.concat(this.chosen_media_types.map((mt) => `mt${FILTER_STRING_EQ}${mt}`));
      out = out.concat(this.chosen_tags.map((t) => `t${FILTER_STRING_EQ}${t.handle}`));
      out = out.concat(this.chosen_metatags.map((t) => `mtt${FILTER_STRING_EQ}${t.handle}`));
      out = out.concat(this.chosen_users.map((u) => `u${FILTER_STRING_EQ}${u.handle}`));
      out.push(`p${FILTER_STRING_EQ}${this.printable ? 'true' : 'false'}`);
      out.push(`ta${FILTER_STRING_EQ}${this.tag_handles_all ? 'true' : 'false'}`);
      out.push(`ua${FILTER_STRING_EQ}${this.user_handles_all ? 'true' : 'false'}`);
      return out.join(FILTER_STRING_SEP);
    },
    show_link : function() {
      let link = `${location.origin}${location.pathname}#report=${this.build_filter_string()}`;
      this.current_link = link;
      this.showing_link = true;
    },
    update : function() {
      let tags = [].concat(this.chosen_tags.map(t => t.handle));
      this.chosen_metatags.forEach((mtt) => {
        tags = tags.concat(mtt.tag_handles);
      });

      this.store.search(this.chosen_media_types,
        tags,
        this.chosen_users.map(u => u.handle),
        this.tag_handles_and,
        this.user_handles_and);
    },
    get_filtered_tags : function(search) {
      this.filtered_tags = this.store.live.tags.filter(tag => {
        return (
          tag.name.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },
    get_filtered_metatags : function(search) {
      this.filtered_metatags = this.store.live.metatags.filter(metatag => {
        return (
          metatag.name.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },
    get_filtered_users : function(search) {
      this.filtered_users = this.store.live.users.filter(user => {
        return (
          user.key.toString().toLowerCase().indexOf(search.toLowerCase()) >= 0
        );
      });
    },
  },
};
</script>
