<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    v-if="users.length"
    class="box columns">
    <div
      class="column">
      <p>
        Users:
      </p>
      <div
        class="tags">
        <div
          v-for="(user, user_index) in users"
          class="tag"
          :style="'background: ' + user.colour">
          {{ user.key }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name : 'UserList',
  data : function() {
    return {
    };
  },
  props : [
    'users',
  ],
  setup : function() {
  },
  mounted : function() {
  },
  methods : {
  },
};
</script>

<style scoped>

</style>
