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
			this.taggings.push(tagging);
		},
		async create(media_handle, tag_handle, position, comment) {
			window.fetch(`{api_target}/api/tagging/`, {
				method : 'POST',
				headers : { 'Content-Type' : 'application/json' },
				body : JSON.stringify({
					media_handle : media_handle,
					tag_handle : tag_handle,
					comment : comment,
				}),
			}).then(resp => resp.json())
			.then(tagging => {
				this.taggings.push(tagging);
			});
		},
		getForMedia(media_handle) {
			let filtered = this.taggings.filter((tagging) => {
				return tagging.media_handle == media_handle;
			});
			return filtered;
		},
	}
});
