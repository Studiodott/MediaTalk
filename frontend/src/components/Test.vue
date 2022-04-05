<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div>
  <button @click="clicked">count is: {{ count }}</button>
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
      count : 0,
      tags : [],
    };
  },
  sockets: {
    new_tag : function(data) {
      console.log('new_tag(data='+data+')');
      this.tags.push(data);
    },
  },
  methods : {
    clicked() {
      this.$socket.emit('debug', 'new_tag');
      this.count++;
    }
  }
};
</script>
