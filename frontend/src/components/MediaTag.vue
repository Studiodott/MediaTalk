<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    class="box">
    <div
      class="is-flex is-flex-direction-row is-justify-content-space-between is-align-items-center pb-4">
      <o-icon
        :icon="get_icon_for_type()"
        size="large">
      </o-icon>
      <span
        class="is-size-4">
        {{ description }}
      </span>

      <div
        v-if="store.get_is_admin()">

        <o-button
          @click="modal_open">
          <o-icon
            icon="pen">
          </o-icon>
        </o-button>
        <o-modal
          v-model:active="modal_admin_active">
          <div
            class="modal-card">
            <header
              class="modal-card-head">
              <p class="modal-card-title">Edit media</p>
            </header>
            <section
              class="modal-card-body">
              <o-field
                horizontal
                label="Filename">
                <p>
                  {{ filename }}
                </p>
              </o-field>
              <o-field
                horizontal
                label="Description">
                <o-input
                  v-model="modal_description"
                  @input="modal_is_changed = true"
                  expanded>
                </o-input>
              </o-field>

              <o-field
                horizontal>
                <o-button
                  @click="admin_save"
                  :disabled="!modal_is_changed"
                  :class="(modal_is_saving == true) ? 'is-loading' : ''"
                  variant="primary">
                  Save
                </o-button>
              </o-field>

              <hr/>
              <o-field
                label="Remove media"
                horizontal>
                <o-button
                  @click="admin_remove"
                  variant="danger">
                  Remove
                </o-button>
              </o-field>

            </section>
            <footer
              class="modal-card-foot is-justify-content-end">
              <o-button
                @click="modal_close">
                Close
              </o-button>
            </footer>
          </div>
        </o-modal>
      </div>

    </div>
    <div
      class="columns">
      <div
        class="column is-two-thirds is-flex is-flex-direction-column is-align-items-stretch">
        <div
          v-if="media_type == 'VIDEO'">
          <MediaTagVideo
            ref="tagger"
            :selection_colour="store.get_my_colour()"
            @advanced="advanced_by_media"
            :highlights="highlights_for_media"
            :selection="selection_for_media"
            :src="url_original"
            :waveform="url_description"/>
        </div>
        <div
          v-else-if="media_type == 'AUDIO'">
          <MediaTagAudio
            ref="tagger"
            :selection_colour="store.get_my_colour()"
            @advanced="advanced_by_media"
            :highlights="highlights_for_media"
            :selection="selection_for_media"
            :src="url_original"
            :waveform="url_description"/>
        </div>
        <div
          v-else-if="media_type == 'IMAGE'">
          <MediaTagImage
            ref="tagger"
            :selection_colour="store.get_my_colour()"
            :highlights="highlights_for_media"
            @selected="selected_by_media"
            v-bind:src="url_original"/>
        </div>
        <div
          v-else-if="media_type == 'TEXT'">
          <MediaTagText
            ref="tagger"
            :selection_colour="store.get_my_colour()"
            :highlights="highlights_for_media"
            @selected="selected_by_media"
            v-bind:src="url_original"/>
        </div>
      </div>
      <div
        class="column is-one-third is-flex is-flex-direction-column is-justify-content-end">
        <div
          v-if="media_type == 'VIDEO' || media_type == 'AUDIO'">
          <div
            class="box">
            <p>new:</p>
            <TagChooserTimelineSimple
              :advance="advance_for_tagchooser"
              @selected="selected_by_tagchooser"
              :media_handle="handle"/>
          </div>
        </div>
        <div
          v-if="media_type == 'IMAGE'">
          <TagChooserStatic
            :selection="selection_for_tagchooser"
            @cleared="cleared_by_tagchooser"
            :media_handle="handle"/>
        </div>
        <div
          v-if="media_type == 'TEXT'">
          <!--
            on text, selecting a point makes no sense
          -->
          <TagChooserStatic
            :allowed_selections="['ALL','RANGE']"
            :selection="selection_for_tagchooser"
            @cleared="cleared_by_tagchooser"
            :media_handle="handle"/>
        </div>

      </div>
    </div>
    <div
      class="columns">
      <div
        class="column">
        <TagList
          :show_comments="false"
          :media_handle="handle"
          @select="highlight_taggings"
          collection="live"/>
      </div>
    </div>
  </div>
</template>

<script>
import { Store } from '@/store/store.js';
import TagList from '@/components/TagList.vue';
import TagChooserStatic from '@/components/TagChooserStatic.vue';
import TagChooserTimeline from '@/components/TagChooserTimeline.vue';
import TagChooserTimelineSimple from '@/components/TagChooserTimelineSimple.vue';
import MediaTagText from '@/components/MediaTagText.vue';
import MediaTagVideo from '@/components/MediaTagVideo.vue';
import MediaTagAudio from '@/components/MediaTagAudio.vue';
import MediaTagImage from '@/components/MediaTagImage.vue';
import PositionDisplay from '@/components/PositionDisplay.vue';

export default {
  name : 'MediaTag',
  data : function() {
    return {
      modal_admin_active : false,
      modal_is_saving : false,
      modal_is_changed : false,
      modal_description : undefined,
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
    TagChooserTimelineSimple,
    MediaTagText,
    MediaTagVideo,
    MediaTagAudio,
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
    // the tagchooser cleared the selection
    cleared_by_tagchooser : function() {
      this.$refs.tagger.clear_selection();
    },
    // a nice icon for this media type
    get_icon_for_type : function() {
      switch (this.media_type) {
        case 'VIDEO':
            return 'video';
            break;
        case 'AUDIO':
            return 'microphone';
            break;
        case 'TEXT':
            return 'file-lines';
            break;
        case 'IMAGE':
            return 'camera';
            break;
        default:
            return 'question';
            break;
      }
    },
    // admin changed details about this media, this will trigger a websocket
    // message from server causing the store to refresh it
    admin_save : function() {
      this.modal_is_saving = true;
      this.store.media_change(this.handle, this.modal_description)
        .then(() => { this.modal_is_saving = false; this.modal_is_changed = false; })
        .catch(() => { this.modal_is_saving = false; });
    },
    // admin wants to remove this media, this'll trigger a websocket
    // message from server causing the store to remove it
    admin_remove : function() {
      this.store.media_delete(this.handle);
      // close this "removed" media's modal
      this.modal_close();
    },
    // admin wants to see the modal with per-media options, copy some
    // values to modal-specific places so edits don't touch the main scope
    modal_open : function() {
      this.modal_description = this.description;
      this.modal_admin_active = true;
    },
    // close the modal
    modal_close : function() {
      this.modal_admin_active = false;
    }
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
