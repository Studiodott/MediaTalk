import { defineStore } from 'pinia';
import { api_target } from '@/config.js';

export const taggingStore = defineStore('tagging', {
	state: () => ({
		taggings : [],
	}),
	actions: {
		async load() {
			window.fetch(api_target + '/api/tagging')
			.then(resp => resp.json())
			.then(taggings => {
				this.taggings = taggings.taggings;
			});
		},
		add(tagging) {
			this.taggings = this.taggings.filter((e_tagging) => {
				return tagging.handle != e_tagging.handle;
			});
			this.taggings.splice(0, 0, tagging);
		},
		async create(media_handle, tag_handle, position, comment) {
			let t = await window.fetch(api_target + '/api/tagging', {
				method : 'POST',
				headers : { 'Content-Type' : 'application/json' },
				body : JSON.stringify({
					media_handle : media_handle,
					tag_handle : tag_handle,
					'position' : JSON.stringify(position),
					comment : comment,
				}),
			}).then(resp => resp.json())
			.catch((error) => {
				console.log("error while creating tagging: " + error);
			});
			return t;
		},
		getForMedia(media_handle) {
			let filtered = this.taggings.filter((tagging) => {
				return tagging.media_handle == media_handle;
			});
			return filtered;
		},
	}
});
