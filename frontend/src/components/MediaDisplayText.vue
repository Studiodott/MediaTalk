<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <!--
  <textarea
    readonly
    autocomplete="off"
    autocorrect="off"
    spellcheck="off"
    ref="actual_text"
    id="actual_text">
  </textarea>
  -->
  <div
    contenteditable
    ref="actual_text"
    id="actual_text">
  </div>
</template>

<script>
export default {
  name : 'MediaDisplayText',
  data : function() {
    return {
      original_text : '',
      selection : null,
      regions : [],
    };
  },
  props : [
    'src',
    'highlights',
    'selection_colour',
  ],
  emits : [
    'selected',
  ],
  setup : function() {
  },
  mounted : async function() {
    this.$refs.actual_text.spellcheck = false;
    this.$refs.actual_text.addEventListener('mouseup', (event) => {
      let sel = document.getSelection();
      let range = sel.getRangeAt(0);
      let first_region_seen = undefined;
      let last_region_seen = undefined;
      for (let i = 0; i < this.regions.length; i++) {
        let included = sel.containsNode(this.regions[i].span, true);
        if (included) {
          if (first_region_seen == undefined) {
            first_region_seen = i;
          }
          last_region_seen = i;
        }
      }
      if (sel.type == 'Caret') {
        /*
        this.selection = {
          what : 'point',
          at : sel.anchorOffset + this.regions[first_region_seen].offset,
        };
        */
        // TODO while point doesn't work here
        this.selection = {
          what : 'range',
          from : sel.anchorOffset + this.regions[first_region_seen].offset,
          to : sel.focusOffset + this.regions[last_region_seen].offset,
        };
        this.$emit('selected', this.selection);
      } else if (sel.type == 'Range') {
        this.selection = {
          what : 'range',
          from : sel.anchorOffset + this.regions[first_region_seen].offset,
          to : sel.focusOffset + this.regions[last_region_seen].offset,
        };
        this.$emit('selected', this.selection);
      }
      this.redraw();
    });
    this.$refs.actual_text.addEventListener('select', (event) => {
    });
    this.$refs.actual_text.addEventListener('selectionchange', (event) => {
    });

    await window.fetch(this.src)
    .then((resp) => resp.text())
    .then((text) => {
      this.original_text = text;
      this.redraw();
    });
  },
  watch : {
    highlights : {
      handler : function(new_highlights) {
        if (this.original_text.length)
          this.redraw();
      },
      deep : false,
    },
  },
  methods : {
    redraw() {
      //this.$refs.actual_text.value = this.original_text;
      let output = '';

      let dest = this.$refs.actual_text;

      while (dest.firstChild)
        dest.removeChild(dest.firstChild);

      function buildSpan(offset, length, text, trim) {
        let span = document.createElement('span');
        let t = text.slice(offset, offset + length);

        if (trim) {
          let keep_start = 2;
          let keep_end = 2;
          let lines = t.split('\n');
          if (offset == 0) {
            // don't keep the starting lines
            keep_start = 0;
          }
          if ((offset + length) == text.length) {
            // don't keep the ending lines
            keep_end = 0;
          }
          if (lines.length < (keep_start + keep_end)) {
            // too little to start snipping
          } else {
            // cut out everything between start+keep and end-keep
            lines.splice(keep_start, lines.length - (keep_start + keep_end));
            lines.splice(keep_start, 0, '...');
          }
          t = lines.join('\n');
        }

        let content = document.createTextNode(t);
        span.appendChild(content);
        return span;
      }

      this.regions = [
        {
          offset : 0,
          length : this.original_text.length,
          which : [],
          span : undefined,
        },
      ];

      // splits the regions at the mark
      // assumes there is an existing region in which the mark will fall
      function splice_regions_around(regions, mark) {
        // first find the region in which the mark occurs
        let found = undefined;

        for (let i = 0; i < regions.length; i++) {
          let r = regions[i];

          if ((r.offset <= mark) && (mark <= (r.offset + r.length))) {
            found = i;
          }
        }
        if (mark == regions[found].offset) {
          // no need for a new region, just return this one
          return found;
        } else {
          // splice region into two parts

          let new_offset = mark;
          let new_length = regions[found].length - (mark - regions[found].offset);

          if (new_length) {
            // only do this if this is a non-zero length region (might not be at end boundary)

            // add a new region [mark + found.stop]
            regions.splice(found + 1, 0, {
              offset : new_offset,
              length : new_length,
              which : [...regions[found].which],
            })

            // cap the original region
            regions[found].length = mark - regions[found].offset;
          }

          return found + 1;
        }
      };

      function splice_range(regions, a_range, meta) {
        if (a_range.what != 'range')
          return;
        let first_region = splice_regions_around(regions, a_range.from);
        let last_region = splice_regions_around(regions, a_range.to);

        for (let i = first_region; i < last_region; i++) {
          regions[i].which.push(meta);
        }
      }

      if (this.highlights && this.highlights.taggings &&  this.highlights.taggings.length) {
        // a localized copy of highlights which is from-ascending
        let highlights = [...this.highlights.taggings];
        highlights.sort((l, r) => {
          let l_val = (l.position.what == 'point') ? l.position.at : l.position.from;
          let r_val = (r.position.what == 'point') ? r.position.at : r.position.from;
          return r_val - l_val;
        });

        for (let i = 0; i < highlights.length; i++) {
          let c = highlights[i].colour;
          let important = false;

          if (this.highlights.emphasis.length == 0  || this.highlights.emphasis.includes(highlights[i].handle)) {
            c += 'ff';
            important = true;
          } else {
            c += '7f';
          }
          splice_range(this.regions, highlights[i].position, { colour : c, jump : important });
        }
      }

      if (this.selection && this.selection.what == 'range') {
        splice_range(this.regions, this.selection, { colour : this.selection_colour, jump : false });
      }

      for (let i = 0; i < this.regions.length; i++) {
        let r = this.regions[i];
        r.span = buildSpan(r.offset, r.length, this.original_text, r.which.length == 0);
        r.span.dataset.offset = r.offset;
        r.which.forEach((m) => { r.span.style = `background: ${m.colour};`; });
        this.$refs.actual_text.appendChild(r.span);
        if (r.which.find((m) => m.jump == true) != undefined) {
          console.log("scrolling");
          r.span.scrollIntoView({ behaviour : 'smooth', block : 'nearest' });
        }
      }

    },
  },
};
</script>

<style>
#actual_text {
  overflow-y: scroll;
  white-space: pre-wrap;
  height: 300px;
}
.selection {
  background: #aabbcc;
}
.highlight {
  background: #ccbbaa;
}
</style>
