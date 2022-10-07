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
			metatags : [],
			users : [],
		},
		last_load : undefined,
		logged_in : localStorage.access_token != undefined,
		runtime : {
			audio_volume : 50,
			sticky_tags : false,
		},
		feature_removal_affects_search : true,
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
				this.log_in(auth.access_token, email, auth.colour, auth.admin);
				this.load();
			})
			.catch((error) => {
				console.log("error while logging in: " + error);
			});
		},

		log_in(v, key, colour, admin) {
			this.logged_in = true;
			localStorage.access_token = v;
			localStorage.access_key = key;
			localStorage.access_my_colour = colour;
			console.log("admin="+admin);
			console.log(typeof admin);
			localStorage.access_is_admin = admin;
		},

		log_out() {
			this.logged_in = false;
			localStorage.removeItem('access_token');
			localStorage.removeItem('access_key');
			localStorage.removeItem('access_my_colour');
			localStorage.removeItem('access_is_admin');
		},

		get_login_key() {
			return this.logged_in ? localStorage.access_key : undefined;
		},

		get_my_colour() {
			return this.logged_in ? localStorage.access_my_colour : undefined;
		},

		get_is_admin() {
			return this.logged_in ? localStorage.access_is_admin == "true" : undefined;
		},

		async load() {
			let std_opts = {
				method : 'GET',
				headers : {
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			};

			let p = [];

			p.push(window.fetch(api_target + '/api/media', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.media.splice(0);
				data.media.forEach((e) => { this.live.media.push(e); });
			})
			.catch((error) => {
				this.log_out();
			}));

			p.push(window.fetch(api_target + '/api/tag', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.tags.splice(0);
				data.tags.forEach((e) => { this.live.tags.push(e); });
			})
			.catch((error) => {
				this.log_out();
			}));

			p.push(window.fetch(api_target + '/api/user', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.users.splice(0);
				data.users.forEach((e) => { this.live.users.push(e); });
			})
			.catch((error) => {
				this.log_out();
			}));

			p.push(window.fetch(api_target + '/api/metatag', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.metatags.splice(0);
				data.metatags.forEach((e) => { this.live.metatags.push(e); });
			})
			.catch((error) => {
				this.log_out();
			}));

			p.push(window.fetch(api_target + '/api/tagging', std_opts)
			.then(resp => resp.json())
			.then(data => {
				this.live.taggings.splice(0);
				data.taggings.forEach((e) => {
					e.position = JSON.parse(e.position);
					this.live.taggings.push(e);
				});
			})
			.catch((error) => {
				this.log_out();
			}));

			this.last_load = Promise.all(p);
			console.log("LOADED");
			return this.last_load;

		},
		async search(media_types, tag_handles, user_handles, tag_handles_and, user_handles_and) {
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
			if (tag_handles_and)
				p.append('tag_handles_and', true);
			if (user_handles_and)
				p.append('user_handles_and', true);
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
				data.taggings.forEach((e) => {
					e.position = JSON.parse(e.position);
					this.search_results.taggings.push(e);
				});
			})
			.catch((error) => {
				console.log(`error performing search: ${error}`);
				this.log_out();
			});
		},
		media_added(media) {
			this.live.media = this.live.media.filter((e_media) => {
				return media.handle != e_media.handle;
			});
			this.live.media.splice(0, 0, media);
		},
		user_added(user) {
			this.live.users = this.live.users.filter((e_user) => {
				return user.handle != e_user.handle;
			});
			this.live.users.splice(0, 0, user);
		},
		tag_added(tag) {
			this.live.tags = this.live.tags.filter((e_tag) => {
				return tag.handle != e_tag.handle;
			});
			this.live.tags.splice(0, 0, tag);
		},
		tagging_added(tagging) {
			tagging.position = JSON.parse(tagging.position);
			this.live.taggings = this.live.taggings.filter((e_tagging) => {
				return tagging.handle != e_tagging.handle;
			});
			this.live.taggings.splice(0, 0, tagging);
		},
		metatag_added(metatag) {
			this.live.metatags = this.live.metatags.filter((e_metatag) => {
				return metatag.handle != e_metatag.handle;
			});
			this.live.metatags.splice(0, 0, metatag);
		},
		tag_removed(handle) {
			this.live.tags = this.live.tags.filter((e_tag) => {
				return handle != e_tag.handle;
			});
			this.live.taggings = this.live.taggings.filter((e_tagging) => {
				return handle != e_tagging.tag_handle;
			});

			if (this.feature_removal_affects_search) {
				this.search_results.tags = this.search_results.tags.filter((e_tag) => {
					return handle != e_tag.handle;
				});
				this.search_results.taggings = this.search_results.taggings.filter((e_tagging) => {
					return handle != e_tagging.tag_handle;
				});
			}

		},
		tagging_removed(handle) {
			this.live.taggings = this.live.taggings.filter((e_tagging) => {
				return handle != e_tagging.handle;
			});

			if (this.feature_removal_affects_search) {
				this.search_results.taggings = this.search_results.taggings.filter((e_tagging) => {
					return handle != e_tagging.handle;
				});
			}
		},
		metatag_removed(handle) {
			this.live.metatags = this.live.metatags.filter((e_metatag) => {
				return handle != e_metatag.handle;
			});
		},
		metatag_changed(changed_metatag) {
			this.metatag_removed(changed_metatag.handle);
			this.metatag_added(changed_metatag);
		},
		async remove_tagging(handle) {
			let t = await window.fetch(api_target + `/api/tagging/${handle}`, {
				method : 'DELETE',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			}).catch((error) => {
				console.log("error while deleting tag: " + error);
				this.logout();
			});
			return t;
		},
		async remove_tag(handle) {
			let t = await window.fetch(api_target + `/api/tag/${handle}`, {
				method : 'DELETE',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			}).catch((error) => {
				console.log("error while deleting tag: " + error);
				this.logout();
			});
			return t;
		},
		async remove_metatag(handle) {
			let t = await window.fetch(api_target + `/api/metatag/${handle}`, {
				method : 'DELETE',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			}).catch((error) => {
				console.log("error while deleting metatag: " + error);
				this.logout();
			});
			return t;
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
				this.log_out();
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
				this.log_out();
			});

			return t;
		},
		async create_metatag(name) {
			let t = await window.fetch(api_target + '/api/metatag', {
				method : 'POST',
				headers : { 
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
				body : JSON.stringify({
					'name' : name,
				}),
			})
			.then(resp => resp.json())
			.catch((error) => {
				console.log("error while creating metatag: " + error);
				this.log_out();
			});
			return t;
		},

		async metatag_remove_tag(metatag_handle, tag_handle) {
			let u = `/api/metatag/${metatag_handle}/${tag_handle}`
			let t = await window.fetch(api_target + u, {
				method : 'DELETE',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			}).catch((error) => {
				console.log("error while tagi from metatag: " + error);
				this.logout();
			});
			return t;
		},

		async metatag_add_tag(metatag_handle, tag_handle) {
			let u = `/api/metatag/${metatag_handle}/${tag_handle}`
			let t = await window.fetch(api_target + u, {
				method : 'POST',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			}).catch((error) => {
				console.log("error while tagi from metatag: " + error);
				this.logout();
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
			for (let i = 0; i < this.live.tags.length; i++) {
				if (handle == this.live.tags[i].handle)
					return this.live.tags[i];
			}
			return null;
		},

		get_metatag(handle) {
			for (let i = 0; i < this.live.metatags.length; i++) {
				if (handle == this.live.metatags[i].handle)
					return this.live.metatags[i];
			}
			return null;
		},

		get_user(handle) {
			for (let i = 0; i < this.live.users.length; i++) {
				if (handle == this.live.users[i].handle)
					return this.live.users[i];
			}
			return null;
		},

		async admin_request_sync() {
			let u = `/api/admin/sync`;
			let t = await window.fetch(api_target + u, {
				method : 'POST',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			}).catch((error) => {
				console.log("error requesting sync: " + error);
				this.logout();
			});
			return t;
		},

		async admin_config_get() {
			let u = `/api/admin/config`;
			let t = await window.fetch(api_target + u, {
				headers : {
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			})
			.then(resp => resp.json())
			.catch((error) => {
				console.log("error loading config: " + error);
				this.logout();
			});
			return t;
		},

		async admin_config_set(k, v) {
			let u = `/api/admin/config`;
			let t = await window.fetch(api_target + u, {
				method : 'POST',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
				body : JSON.stringify({
					'key' : k,
					'value' : v,
				}),
			})
			.then(resp => resp.json())
			.catch((error) => {
				console.log("error loading config: " + error);
				this.logout();
			});
			return t;
		},

		async admin_user_get(key) {
			let u = `/api/admin/user/${key}`;
			let t = await window.fetch(api_target + u, {
				headers : {
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
			})
			.then(resp => resp.json())
			.catch((error) => {
				console.log("error loading config: " + error);
				this.logout();
			});
			return t;
		},
		async admin_user_set(key, admin) {
			let u = `/api/admin/user/${key}`;
			let t = await window.fetch(api_target + u, {
				method : 'POST',
				headers : {
					'Content-Type' : 'application/json',
					'Authorization' : `Bearer ${localStorage.access_token}`,
				},
				body : JSON.stringify({
					'admin' : admin,
				}),
			})
			.then(resp => resp.json())
			.catch((error) => {
				console.log("error loading config: " + error);
				this.logout();
			});
			return t;
		},

	},
});
