import { defineStore } from 'pinia';
import { api_target } from '@/config.js';

export const Store = defineStore('Store', {
	state: () => ({
		search_results : {
			media : [],
			tags : [],
			taggings : [],
		},
		live : {
			media : [],
			tags : [],
			taggings : [],
		},
	}),
	actions: {
		async load() {
			window.fetch(api_target + '/api/media')
			.then(resp => resp.json())
			.then(data => {
				this.live.media.splice(0);
				data.media.forEach((e) => { this.live.media.push(e); });
			});
			window.fetch(api_target + '/api/tag')
			.then(resp => resp.json())
			.then(data => {
				this.live.tags.splice(0);
				data.tags.forEach((e) => { this.live.tags.push(e); });
			});
			window.fetch(api_target + '/api/tagging')
			.then(resp => resp.json())
			.then(data => {
				this.live.taggings.splice(0);
				data.taggings.forEach((e) => { this.live.taggings.push(e); });
			});
		},
		async search(media_types, tag_handles) {
			let p = new URLSearchParams();
			media_types.forEach((mt) => {
				p.append('media_type', mt);
			});
			tag_handles.forEach((mt) => {
				p.append('tag_handle', mt);
			});

			window.fetch(api_target + '/api/search?' + p.toString())
			.then(resp => resp.json())
			.then(data => {
				this.search_results.media.splice(0);
				data.media.forEach((e) => { this.search_results.media.push(e); });
				this.search_results.tags.splice(0);
				data.tags.forEach((e) => { this.search_results.tags.push(e); });
				this.search_results.taggings.splice(0);
				data.taggings.forEach((e) => { this.search_results.taggings.push(e); });
			});
		},
		add_media(media) {
			this.live.media = this.live.media.filter((e_media) => {
				return media.handle != e_media.handle;
			});
			this.live.media.splice(0, 0, media);
		},
		add_tag(tag) {
			this.live.tags = this.live.tags.filter((e_tag) => {
				return tag.handle != e_tag.handle;
			});
			this.live.tags.splice(0, 0, tag);
		},
		add(tagging) {
			this.live.taggings = this.live.taggings.filter((e_tagging) => {
				return tagging.handle != e_tagging.handle;
			});
			this.live.taggings.splice(0, 0, tagging);
		},
		async create_tag(name, description='') {
			let t = await window.fetch(api_target + '/api/tag', {
				method : 'POST',
				headers : { 
					'Content-Type' : 'application/json',
				},
				body : JSON.stringify({
					'name' : name,
					'description' : description,
				}),
			})
			.then(resp => resp.json())
			.catch((error) => {
				console.log("error while creating tag: " + error);
			});
			return t;
		},
		async create_tagging(media_handle, tag_handle, position, comment) {
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

		get_taggings_for_media(media_handle) {
			let filtered = this.live.taggings.filter((tagging) => {
				let add = true;
				if (tagging.media_handle != media_handle)
					add = false;
				return add;
			});
			return filtered;
		},
		search_results_get_taggings_for_media(media_handle) {
			let filtered = this.search_results.taggings.filter((tagging) => {
				let add = true;
				if (tagging.media_handle != media_handle)
					add = false;
				return add;
			});
			return filtered;
		},

		get_tag(handle) {
			console.log("handle="+handle);
			for (let i = 0; i < this.live.tags.length; i++) {
				if (handle == this.live.tags[i].handle)
					return this.live.tags[i];
			}
			console.log("null!");
			return null;
		},
	},
});
