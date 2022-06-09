import { defineStore } from 'pinia';
import { api_target } from '@/config.js';

export const Store = defineStore('Store', {
	state: () => ({
		search_results : {
			media : [],
			tags : [],
			taggings : [],
			users : [],
		},
		live : {
			media : [],
			tags : [],
			taggings : [],
			users : [],
		},
		logged_in : localStorage.access_token != undefined,
	}),
	actions: {
		async try_auth(email) {
			let t = await window.fetch(api_target + '/api/login', {
				method : 'POST',
				headers : { 
					'Content-Type' : 'application/json',
				},
				body : JSON.stringify({
					'key' : email,
				}),
			})
			.then(resp => resp.json())
			.then(auth => {
				this.set_access_token(auth.access_token);
				this.load();
			})
			.catch((error) => {
				console.log("error while logging in: " + error);
			});
		},

		set_access_token(v) {
			if (v != undefined) {
				this.logged_in = true;
				localStorage.access_token = v;
			} else {
				this.logged_in = false;
				localStorage.removeItem('access_token');
			}
		},

		async load() {
			let std_opts = {
				method : 'GET',
				headers : {
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			};

			window.fetch(api_target + '/api/media', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.media.splice(0);
				data.media.forEach((e) => { this.live.media.push(e); });
			})
			.catch((error) => {
				this.set_access_token(undefined);
			});

			window.fetch(api_target + '/api/tag', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.tags.splice(0);
				data.tags.forEach((e) => { this.live.tags.push(e); });
			})
			.catch((error) => {
				this.set_access_token(undefined);
			});

			window.fetch(api_target + '/api/user', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.users.splice(0);
				data.users.forEach((e) => { this.live.users.push(e); });
			})
			.catch((error) => {
				this.set_access_token(undefined);
			});

			window.fetch(api_target + '/api/tagging', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.taggings.splice(0);
				data.taggings.forEach((e) => { this.live.taggings.push(e); });
			})
			.catch((error) => {
				this.set_access_token(undefined);
			});

		},
		async search(media_types, tag_handles, user_handles) {
			let p = new URLSearchParams();
			media_types.forEach((mt) => {
				p.append('media_type', mt);
			});
			tag_handles.forEach((t) => {
				p.append('tag_handle', t);
			});
			user_handles.forEach((u) => {
				p.append('user_handle', u);
			});
			window.fetch(api_target + '/api/search?' + p.toString(), {
				headers : {
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			})
			.then(resp => resp.json())
			.then(data => {
				this.search_results.media.splice(0);
				data.media.forEach((e) => { this.search_results.media.push(e); });
				this.search_results.tags.splice(0);
				data.tags.forEach((e) => { this.search_results.tags.push(e); });
				this.search_results.users.splice(0);
				data.users.forEach((e) => { this.search_results.users.push(e); });
				this.search_results.taggings.splice(0);
				data.taggings.forEach((e) => { this.search_results.taggings.push(e); });
			})
			.catch((error) => {
				console.log(`error performing search: ${error}`);
				this.set_access_token(undefined);
			});
		},
		add_media(media) {
			this.live.media = this.live.media.filter((e_media) => {
				return media.handle != e_media.handle;
			});
			this.live.media.splice(0, 0, media);
		},
		add_user(user) {
			this.live.users = this.live.users.filter((e_user) => {
				return user.handle != e_user.handle;
			});
			this.live.users.splice(0, 0, user);
		},
		add_tag(tag) {
			this.live.tags = this.live.tags.filter((e_tag) => {
				return tag.handle != e_tag.handle;
			});
			this.live.tags.splice(0, 0, tag);
		},
		add_tagging(tagging) {
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
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
				body : JSON.stringify({
					'name' : name,
					'description' : description,
				}),
			})
			.then(resp => resp.json())
			.catch((error) => {
				console.log("error while creating tag: " + error);
				this.set_access_token(undefined);
			});
			return t;
		},
		async create_tagging(media_handle, tag_handle, position, comment) {
			let t = await window.fetch(api_target + '/api/tagging', {
				method : 'POST',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
				body : JSON.stringify({
					media_handle : media_handle,
					tag_handle : tag_handle,
					'position' : JSON.stringify(position),
					comment : comment,
				}),
			}).then(resp => resp.json())
			.catch((error) => {
				console.log("error while creating tagging: " + error);
				this.set_access_token(undefined);
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
