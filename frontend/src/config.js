let api_target = location.origin;
if (import.meta.env.VITE_API_TARGET != undefined) {
  api_target = import.meta.env.VITE_API_TARGET;
}


export { api_target };
