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
			this.tags = this.tags.filter((e_tag) => {
				return tag.handle != e_tag.handle;
			});
			this.tags.splice(0, 0, tag);
		},
		get(handle) {
			console.log("handle="+handle);
			for (let i = 0; i < this.tags.length; i++) {
				if (handle == this.tags[i].handle)
					return this.tags[i];
			}
			console.log("null!");
			return null;
		},
		async create(name, description='') {
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
	}
});
