<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
    <o-field
      :variant="error.length > 0 ? 'danger' : ''"
      :message="error"
      label="New metatag name">
      <o-input
        @input="error = ''"
        v-model="name">
      </o-input>
    </o-field>
    <div
      class="is-flex is-justify-content-end">
      <o-button
        @click="add_metatag"
        variant="primary">
        create
      </o-button>
    </div>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';

export default {
  name : 'MetaTagNew',
  data : function() {
    return {
      name : '',
      error : '',
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
    async add_metatag(e) {
      if (!this.name.length) {
        this.error = "Please fill in a name";
      } else if (this.store.live.metatags.find((mt) => mt.name == this.name)) {
        this.error = "Another metatag has this name already";
      } else {
        this.error = '';
      }

      if (this.error.length) {
        return;
      }

      this.store.create_metatag(this.name).then(() => {
        this.reset();
      });

    },
    reset() {
      this.name = '';
      this.error = '';
    },
  },
  computed: {
  },
};
</script>

<style scoped>

</style>
