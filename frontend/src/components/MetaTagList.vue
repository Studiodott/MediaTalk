<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column">
      <h2
        class="subtitle">
        Create a metatag:
      </h2>
      <div>
        <MetaTagNew/>
      </div>
      <h2
        class="subtitle">
        Existing metatags:
      </h2>
      <div
        v-for="(mt, mt_index) in all_metatags"
        :key="mt_index"
        :metatag="mt">
        <MetaTagEditor
          :metatag="mt"/>
      </div>
    </div>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';
import MetaTagEditor from '@/components/MetaTagEditor.vue';
import MetaTagNew from '@/components/MetaTagNew.vue';

export default {
  name : 'MetaTagList',
  components : {
    MetaTagEditor,
    MetaTagNew,
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
  },
  computed : {
    all_metatags() {
      return this.store.live.metatags.slice().sort((l, r) => {
        if (l.name == r.name)
          return 0;
        if (l.name < r.name)
          return -1;
        return 1;
      });
    },
  },
};
</script>

<style scoped>

</style>
