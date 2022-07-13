<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column is-flex is-flex-direction-column is-align-items-stretch">
      <div
        v-for="(taggings, tag_handle, tag_index) in getTaggingsForMedia">
        <p>
          Tag "<b>{{ get_tag_name(tag_handle) }}</b>"
        </p>
        <div
          v-if="media_type == 'VIDEO'">
          <MediaPrintVideo
            :selection_colour="store.get_my_colour()"
            :highlights="{ 'taggings' : taggings, 'emphasis' : [] }"
            :selection="selection_for_media"
            :src="url_original"
            :waveform="url_description"/>
        </div>
        <div
          v-else-if="media_type == 'AUDIO'">
          <MediaPrintAudio
            :selection_colour="store.get_my_colour()"
            :highlights="{ 'taggings' : taggings, 'emphasis' : [] }"
            :selection="selection_for_media"
            :src="url_original"
            :waveform="url_description"/>
        </div>
        <div
          v-else-if="media_type == 'IMAGE'">
          <MediaPrintImage
            :selection_colour="store.get_my_colour()"
            :highlights="{ 'taggings' : taggings, 'emphasis' : [] }"
            v-bind:src="url_original"/>
        </div>
        <div
          v-else-if="media_type == 'TEXT'">
          <MediaPrintText
            :selection_colour="store.get_my_colour()"
            :highlights="{ 'taggings' : taggings, 'emphasis' : [] }"
            v-bind:src="url_original"/>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';
import { Store } from '@/store/store.js';
import TagList from '@/components/TagList.vue';
import TagChooserStatic from '@/components/TagChooserStatic.vue';
import TagChooserTimeline from '@/components/TagChooserTimeline.vue';
import MediaPrintText from '@/components/MediaPrintText.vue';
import MediaPrintVideo from '@/components/MediaPrintVideo.vue';
import MediaPrintAudio from '@/components/MediaPrintAudio.vue';
import MediaPrintImage from '@/components/MediaPrintImage.vue';
import PositionDisplay from '@/components/PositionDisplay.vue';

export default {
  name : 'MediaPrint',
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
    MediaPrintText,
    MediaPrintVideo,
    MediaPrintAudio,
    MediaPrintImage,
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
    get_tag_name : function(tag_handle) {
      let tag = this.store.get_tag(tag_handle);
      if (!tag) {
        console.log(`oddity, can't find tag for handle=${tag_handle}`);
        return 'not found';
      }
      return tag.name;
    },

  },
  computed : {
    getTaggingsForMedia() {
      let taggings = [];
      let taggings_by_tag_handle = {};

      taggings = this.store.search_results_get_taggings_for_media(this.handle);

      taggings.forEach((ti) => {
        if (!(ti.tag_handle in taggings_by_tag_handle)) {
          taggings_by_tag_handle[ti.tag_handle] = [];
        }
        taggings_by_tag_handle[ti.tag_handle].push(ti);
      });

      return taggings_by_tag_handle;
    },

  },
};
</script>
