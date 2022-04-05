<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
    <Test />
  </div>
</template>

<script>
import Test from "./components/Test.vue";
export default {
  name : 'App',
  components : {
    Test
  },
  mounted : function() {
    this.$socket.emit('debug', 'new client');
  },
};
</script>

<style>
</style>
