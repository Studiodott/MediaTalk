import { defineStore } from 'pinia';
import { api_target } from '@/config.js';

export const tagStore = defineStore('tag', {
	state: () => ({
		tags : [],
	}),
	actions: {
		async load() {
			window.fetch(api_target + '/api/tag')
			.then(resp => resp.json())
			.then(tags => {
				this.tags = tags.tags;
			});
		},
		add(tag) {
			this.tags.push(tag);
		},
	}
});
