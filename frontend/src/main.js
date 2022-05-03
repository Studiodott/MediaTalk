import { createApp } from "vue";
import { createPinia, defineStore } from 'pinia';
import Oruga from '@oruga-ui/oruga-next';
import { bulmaConfig } from '@oruga-ui/theme-bulma';
import App from "./App.vue";
import VueSocketIO from "vue-3-socket.io";
//import '@oruga-ui/oruga-next/dist/oruga-full.css';
import '@oruga-ui/theme-bulma/dist/bulma.css';

let ws_target = location.origin.replace(/^http/, 'ws');
if (import.meta.env.VITE_WS_TARGET != undefined) {
  ws_target = import.meta.env.VITE_WS_TARGET;
}
console.log(`ws_target=${ws_target}`);

const app_ws = new VueSocketIO({
  debug : true,
  connection : ws_target,
  options : { transports : [ 'websocket', 'polling' ] },
});

const app = createApp(App);
app.use(app_ws);
app.use(createPinia());
app.use(Oruga, bulmaConfig);

app.mount('#app');
