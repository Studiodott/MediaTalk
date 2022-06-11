<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column is-two-thirds is-flex is-flex-direction-column is-align-items-stretch">
      <div
        v-if="media_type == 'VIDEO'">
        <MediaTagVideo
          @advanced="advanced_by_media"
          :highlights="highlights_for_media"
          :selection="selection_for_media"
          :src="url_original"
          :waveform="url_description"/>
      </div>
      <div
        v-else-if="media_type == 'AUDIO'">
        <audio
          controls
          v-bind:src="url_original">
          No browser support for video :-(
        </audio>
        <img
          v-if="url_description.length > 0"
          v-bind:src="url_description">
      </div>
      <div
        v-else-if="media_type == 'IMAGE'">
        <MediaTagImage
          :highlights="highlights_for_media"
          @selected="selected_by_media"
          v-bind:src="url_original"/>
      </div>
      <div
        v-else-if="media_type == 'TEXT'">
        <MediaTagText
          :highlights="highlights_for_media"
          @selected="selected_by_media"
          v-bind:src="url_original"/>
      </div>
    </div>
    <div
      class="column is-one-third">
      <TagChooserTimeline
        v-if="media_type == 'VIDEO' || media_type == 'AUDIO'"
        :advance="advance_for_tagchooser"
        @selected="selected_by_tagchooser"
        :media_handle="handle"/>
      <TagChooserStatic
        v-if="media_type == 'TEXT' || media_type == 'IMAGE'"
        :selection="selection_for_tagchooser"
        :media_handle="handle"/>
      <hr/>
      <TagList
        :media_handle="handle"
        @select="highlight_taggings"
        collection="live"/>
    </div>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';
import TagList from '@/components/TagList.vue';
import TagChooserStatic from '@/components/TagChooserStatic.vue';
import TagChooserTimeline from '@/components/TagChooserTimeline.vue';
import MediaTagText from '@/components/MediaTagText.vue';
import MediaTagVideo from '@/components/MediaTagVideo.vue';
import MediaTagImage from '@/components/MediaTagImage.vue';
import PositionDisplay from '@/components/PositionDisplay.vue';

export default {
  name : 'MediaTag',
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
    MediaTagText,
    MediaTagVideo,
    MediaTagImage,
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
    highlight_taggings : function(l) {
      this.highlights_for_media = l;
    },
  },
  computed : {
    getTagsForMedia() {
      let taggings = this.store.get_taggings_for_media(this.handle);
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
