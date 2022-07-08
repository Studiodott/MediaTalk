<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <nav
    class="navbar is-fixed-top"
    role="navigation"
    aria-label="main navigation">
    <div
      class="navbar-brand">
      <a
        class="navbar-item"
        href="/">
        <img
          src="https://api.lorem.space/image/furniture?w=112&h=28"
          width="112"
          height="38">
      </a>
      <a
        role="button"
        class="navbar-burger"
        aria-label="menu"
        aria-expanded="false"
        data-target="mainNavBar">
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>

    <div
      id="mainNavBar"
      class="navbar-menu">
      <div
        class="navbar-start">
      </div>
      <div
        class="navbar-end is-flex is-flex is-align-items-center">
        <div
          class="navbar-item">
          <o-field>
            <o-switch
              v-model="store.runtime.sticky_tags">
              Sticky tags
            </o-switch>
          </o-field>
        </div>
        <div
          style="width: 150px;"
          class="navbar-item">
          <o-icon
            class="pr-2"
            icon="volume-high">
          </o-icon>
          <o-slider
            :max="100"
            :min="0"
            :tooltip="false"
            size="large"
            v-model="store.runtime.audio_volume"
            class="is-fullwidth">
          </o-slider>
        </div>
        <div
          class="navbar-item">
          <div
            class="buttons">
            <a
              @click="log_out"
              class="button is-light"
              :style="'background: ' + store.get_my_colour() + ';'">
              Log out {{ store.get_login_key() }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { Store } from '@/store/store.js';
export default {
  name : 'NavBar',
  data : function() {
    return {
    };
  },
  props : [
  ],
  setup : function() {
    const store = Store();
    return {
      store,
    };
  },
  methods : {
    log_out : function() {
      console.log('logging out');
      this.store.log_out();
      location.reload();
    },
  },
  mounted : function() {
  },
};
</script>
