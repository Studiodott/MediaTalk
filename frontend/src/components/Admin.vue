<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column">
      <section>
        <h2
          class="subtitle">
          Users
        </h2>
        <o-notification>
          These are your users, you can promote them to administrator (just like yourself) here.
        </o-notification>
        <div
          class="is-flex is-flex-direction-column mb-2">
          <div
            v-for="u in store.live.users">
            <div
              :style="'background: ' + u.colour + ';'"
              class="mt-2 p-2 is-flex is-flex-direction-row is-justify-content-space-between is-align-items-baseline">
              <span
                :style="'background: ' + u.colour + ';'">
                {{ u.key }}
              </span>
              <div
                v-if="u.key != store.get_login_key()">
                <o-button
                  v-if="u.admin"
                  @click="admin_user_admin_disable(u.key)">
                  unmake admin
                </o-button>
                <o-button
                  v-else
                  @click="admin_user_admin_enable(u.key)">
                  make admin
                </o-button>
              </div>
              <div
                v-else>
                (that's you!)
              </div>
            </div>

          </div>
        </div>
      </section>
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
    admin_user_admin_enable : function(key) {
      this.store.admin_user_set(key, true);
    },
    admin_user_admin_disable : function(key) {
      this.store.admin_user_set(key, false);
    },
  },
  computed : {
  },
};
</script>

<style scoped>

</style>
