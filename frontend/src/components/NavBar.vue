<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <nav
    class="navbar"
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
        class="navbar-end">
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
