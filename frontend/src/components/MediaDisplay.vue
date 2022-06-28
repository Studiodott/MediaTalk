<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column is-two-thirds is-flex is-flex-direction-column is-align-items-stretch">
      <div
        v-if="media_type == 'VIDEO'">
        <MediaDisplayVideo
          :selection_colour="store.get_my_colour()"
          @advanced="advanced_by_media"
          :highlights="highlights_for_media"
          :selection="selection_for_media"
          :src="url_original"
          :waveform="url_description"/>
      </div>
      <div
        v-else-if="media_type == 'AUDIO'">
        <MediaDisplayAudio
          :selection_colour="store.get_my_colour()"
          @advanced="advanced_by_media"
          :highlights="highlights_for_media"
          :selection="selection_for_media"
          :src="url_original"
          :waveform="url_description"/>
      </div>
      <div
        v-else-if="media_type == 'IMAGE'">
        <MediaDisplayImage
          :selection_colour="store.get_my_colour()"
          :highlights="highlights_for_media"
          @selected="selected_by_media"
          v-bind:src="url_original"/>
      </div>
      <div
        v-else-if="media_type == 'TEXT'">
        <MediaDisplayText
          :selection_colour="store.get_my_colour()"
          :highlights="highlights_for_media"
          @selected="selected_by_media"
          v-bind:src="url_original"/>
      </div>
    </div>
    <div
      class="column is-one-third">
      <TagList
        :media_handle="handle"
        @select="highlight_taggings"
        collection="search"/>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';
import { Store } from '@/store/store.js';
import TagList from '@/components/TagList.vue';
import TagChooserStatic from '@/components/TagChooserStatic.vue';
import TagChooserTimeline from '@/components/TagChooserTimeline.vue';
import MediaDisplayText from '@/components/MediaDisplayText.vue';
import MediaDisplayVideo from '@/components/MediaDisplayVideo.vue';
import MediaDisplayAudio from '@/components/MediaDisplayAudio.vue';
import MediaDisplayImage from '@/components/MediaDisplayImage.vue';
import PositionDisplay from '@/components/PositionDisplay.vue';

export default {
  name : 'MediaDisplay',
  data : function() {
    return {
      selection_for_tagchooser : undefined,
      selection_for_media : undefined,
      highlights_for_media : undefined,
      advance_for_tagchooser : undefined,
    };
  },
  components : {
    TagList,
    TagChooserStatic,
    TagChooserTimeline,
    MediaDisplayText,
    MediaDisplayVideo,
    MediaDisplayAudio,
    MediaDisplayImage,
    PositionDisplay,
  },
  setup : function() {
    const store = Store();
    return { store };
  },
  props : [
    'handle',
    'filename',
    'media_type',
    'description',
    'url_original',
    'url_description',
  ],
  methods : {
    // the media called a time advancement, propagate to tagchooser
    advanced_by_media : function(p) {
      this.advance_for_tagchooser = p;
    },
    // the media called a selection, propagate to tagchooser
    selected_by_media(selection) {
      console.log(selection);
      this.selection_for_tagchooser = selection;
    },
    // the tagchooser called a selection, propagate to media
    selected_by_tagchooser(selection) {
      this.selection_for_media = selection;
    },
    // we ourselves want a tagging list highlighted, propagate to media
    highlight_taggings : function(t) {
      console.dir(t);
      this.highlights_for_media = t;
    },
  },
  computed : {
    getTagsForMedia() {
      let taggings = this.store.search_results_get_taggings_for_media(this.handle);
      let as_dict = {};

      taggings.forEach((ti) => {
        let tag = this.store.get_tag(ti.tag_handle);
        if (tag) {
          if (!(tag.name in as_dict)) {
            as_dict[tag.name] = [];
          }
          as_dict[tag.name].push({
            position : ti.position,
            tagging : ti,
            user : this.store.live.users.find((u) => u.handle == ti.user_handle),
          });
          if (!as_dict[tag.name][as_dict[tag.name].length-1].user) {
            console.log('BLOW UP');
          }
        }
      });
      return as_dict;
    },
  },
};
</script>
