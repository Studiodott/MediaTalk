<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column">
      <h2
        class="subtitle">
        Hello admin
      </h2>
      <o-button
        @click="sync_gdrive">Synchronise from drive
      </o-button>
    </div>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';

export default {
  name : 'Admin',
  components : {
  },
  data : function() {
    return {
    };
  },
  props : [
  ],
  setup : function() {
    const store = Store();
    return { store };
  },
  mounted : function() {
  },
  methods : {
    sync_gdrive : function() {
      console.log("ordering sync");
      this.store.admin_request_sync();
    },
  },
  computed : {
  },
};
</script>

<style scoped>

</style>
