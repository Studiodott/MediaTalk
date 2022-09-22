<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column">
      <section>
        <h2
          class="subtitle">
          Configuration
        </h2>
        <o-notification>
          These are the configuration values which I'll use, both for Google Drive (to find files) and S3 (to store files).
        </o-notification>
        <AdminConfig/>
      </section>
      <section>
        <h2
          class="subtitle">
          Manual sync
        </h2>
        <o-notification>
          Synchronisation automatically occurs at midnight, you can trigger a manual one by pressing this button. Be careful! Syncing often in a short time will cause Google to put me in the time-out room.
        </o-notification>
        <o-notification
          v-if="sync_status"
          :variant="sync_status.error ? 'danger' : 'success'">
          {{ sync_status.message }}
        </o-notification>
        <o-button
          variant="primary"
          class="is-pulled-right"
          @click="sync_gdrive">Manual sync
        </o-button>
      </section>
    </div>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';
import AdminConfig from '@/components/AdminConfig.vue';

export default {
  name : 'Admin',
  components : {
    AdminConfig,
  },
  data : function() {
    return {
      sync_status : undefined,
    };
  },
  props : [
  ],
  setup : function() {
    const store = Store();
    return { store };
  },
  mounted : function() {
    this.sockets.subscribe('sync_status', (data) => {
      this.sync_status = data;
    });
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
