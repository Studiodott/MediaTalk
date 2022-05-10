import { defineStore } from 'pinia';
import { api_target } from '@/config.js';

export const mediaStore = defineStore('media', {
	state: () => ({
		media : [],
	}),
	actions: {
		async load() {
			window.fetch(api_target + '/api/media')
			.then(resp => resp.json())
			.then(media => {
				this.media = media.media;
				console.log("loaded "+this.media.length);
			});
		},
		add(media) {
			this.media = this.media.filter((e_media) => {
				return media.handle != e_media.handle;
			});
			this.media.splice(0, 0, media);
		},
	}
});
