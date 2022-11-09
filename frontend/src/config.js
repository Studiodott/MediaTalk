let api_target = location.origin;
if (import.meta.env.VITE_API_TARGET != undefined) {
  api_target = import.meta.env.VITE_API_TARGET;
}

const tagging_fps = 25;
const tagging_primary_colour = '#00d1b2';
export { api_target, tagging_fps, tagging_primary_colour };
