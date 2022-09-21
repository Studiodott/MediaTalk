<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <o-field
    horizontal
    label="Drive folder ID">
    <o-input
      v-model="config.DRIVE_FOLDER_ID"/>
  </o-field>
  <o-field
    horizontal
    label="Drive API key">
    <o-input
      v-model="config.DRIVE_API_KEY"/>
  </o-field>
  <o-field
    horizontal
    label="S3 access key ID">
    <o-input
      v-model="config.S3_ACCESS_KEY_ID"/>
  </o-field>
  <o-field
    horizontal
    label="S3 secret access key">
    <o-input
      v-model="config.S3_SECRET_ACCESS_KEY"/>
  </o-field>
  <o-field
    horizontal
    label="S3 endpoint URL">
    <div
      class="is-flex is-flex-direction-column">
      <o-input
        class="w-full"
        v-model="config.S3_URL"/>
      <p>For example:
        <ul>
          <li><i>https://s3.eu-central-1.amazonaws.com</i></li>
          <li><i>https://s3.eu-central-1.wasabisys.com</i></li>
        </ul>
      </p>
    </div>
  </o-field>
  <o-field
    horizontal
    label="S3 bucket">
    <o-input
      v-model="config.S3_BUCKET"/>
  </o-field>
  <div
    class="is-flex is-justify-content-end">
    <o-button
      variant="primary"
      :disabled="!validated"
      @click="save()">
      Save
    </o-button>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';

export default {
  name : 'AdminConfig',
  components : {
  },
  data : function() {
    return {
      config : {
        DRIVE_FOLDER_ID : undefined,
        DRIVE_API_KEY : undefined,
        S3_BUCKET : undefined,
        S3_URL: undefined,
        S3_ACCESS_KEY_ID : undefined,
        S3_SECRET_ACCESS_KEY : undefined,
      },
    };
  },
  props : [
  ],
  setup : function() {
    const store = Store();
    return { store };
  },
  mounted : function() {
    this.load();
  },
  methods : {
    load : function() {
      this.store.admin_config_get().then(c => this.config = c);
    },
    save : function() {
      console.log("save");
      Object.keys(this.config).forEach((k) => {
        this.store.admin_config_set(k, this.config[k]);
      });
    },
  },
  computed : {
    validated : function() {
      let r = true;
      Object.keys(this.config).forEach((k) => {
        if (!this.config[k] || this.config[k].length == 0) {
          console.log(k);
          r = false;
        }
      });
      return r;
    },
  },
};
</script>

<style scoped>

</style>
