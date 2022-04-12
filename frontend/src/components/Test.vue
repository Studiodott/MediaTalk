<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
  <button @click="clicked">push something to every client</button>
  <ul>
    <li v-for="(tag, tag_index) in tags" :key="tag_index">
      {{ tag }}
    </li>
  </ul>
  </div>
</template>

<script>
export default {
  name : 'Test',
  data : function() {
    return {
      tags : [],
    };
  },
  methods : {
    clicked() {
      this.$socket.emit('debug', 'new_tag');
    }
  },
  mounted : function() {
    console.log("mounted");
  },
};
</script>
