<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box columns">
    <div
      class="column is-two-thirds is-flex is-flex-direction-column is-align-items-stretch">
      <div
        v-if="media_type == 'VIDEO'">
        <MediaVideo
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
        <MediaImage
          :highlights="highlights_for_media"
          @selected="selected_by_media"
          v-bind:src="url_original"/>
      </div>
      <div
        v-else-if="media_type == 'TEXT'">
        <MediaText
          :highlights="highlights_for_media"
          @selected="selected_by_media"
          v-bind:src="url_original"/>
      </div>
    </div>
    <div
      class="column is-one-third">
      <!--
      <TagChooserTimeline
        :selection="selection"
        :advance_for_tagchooser="advance_for_tagchooser"
        :media_handle="handle"/>
      -->
      <TagChooserTimeline
        v-if="media_type == 'VIDEO' || media_type == 'AUDIO'"
        :advance="advance_for_tagchooser"
        @selected="selected_by_tagchooser"
        :media_handle="handle"/>
      <TagChooserStatic
        v-if="media_type == 'TEXT' || media_type == 'IMAGE'"
        :selection="selection_for_tagchooser"
        :media_handle="handle"/>
      <p>Existing tags:</p>
      <ul>
        <li
          v-for="(tagging_positions, tag_name) in getTagsForMedia">
          <a
            @click="highlight_taggings(tagging_positions)">
            {{ tag_name }}
          </a>
          <ul>
            <li v-for="p in tagging_positions">
              <a @click="highlight_taggings([ p ])">here</a>
            </li>
          </ul><!--<PositionDisplay v-for="p in tagging_positions" :position="p" />-->
        </li>
        <!--
        <li
          v-for="(ti, ti_index) in tagging_store.getForMedia(handle)"
          :key="ti_index">
          {{ tag_store.get(ti.tag_handle).name }} at position {{ ti.position }}
        </li>
        -->
      </ul>
    </div>
  </div>
</template>

<script>
import { tagStore } from '@/store/tag.js';
import { taggingStore } from '@/store/tagging.js';
import TagChooser from '@/components/TagChooser.vue';
import TagChooserStatic from '@/components/TagChooserStatic.vue';
import TagChooserTimeline from '@/components/TagChooserTimeline.vue';
import MediaText from '@/components/MediaText.vue';
import MediaVideo from '@/components/MediaVideo.vue';
import MediaImage from '@/components/MediaImage.vue';
import PositionDisplay from '@/components/PositionDisplay.vue';

export default {
  name : 'Media',
  data : function() {
    return {
      selection_for_tagchooser : undefined,
      selection_for_media : undefined,
      highlights_for_media : undefined,
      advance_for_tagchooser : undefined,
    };
  },
  components : {
    TagChooser,
    TagChooserStatic,
    TagChooserTimeline,
    MediaText,
    MediaVideo,
    MediaImage,
    PositionDisplay,
  },
  setup : function() {
    const tagging_store = taggingStore();
    const tag_store = tagStore();
    return { tagging_store, tag_store };
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
      let taggings = this.tagging_store.getForMedia(this.handle);
      let as_dict = {};

      taggings.forEach((ti) => {
        let tag = this.tag_store.get(ti.tag_handle);
        if (tag) {
          if (!(tag.name in as_dict)) {
            as_dict[tag.name] = [];
          }
          as_dict[tag.name].push(JSON.parse(ti.position));
        }
      });
      return as_dict;
    },
  },
};
</script>
