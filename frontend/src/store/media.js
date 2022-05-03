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
			});
		},
		add(media) {
			this.media.splice(0, 0, media);
			//this.media.push(media);
		},
	}
});
