import { createApp } from "vue";
import App from "./App.vue";
import VueSocketIO from "vue-3-socket.io";

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

app.mount('#app');
