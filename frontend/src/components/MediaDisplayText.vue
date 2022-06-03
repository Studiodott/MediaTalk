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
  ],
  emits : [
    'selected',
  ],
  setup : function() {
  },
  mounted : async function() {
    console.log(this.$refs.actual_text);
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
      console.log(sel);
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
      console.log(event);
    });
    this.$refs.actual_text.addEventListener('selectionchange', (event) => {
      console.log(event);
    });

    await window.fetch(this.src)
    .then((resp) => resp.text())
    .then((text) => {
      //text = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
      this.original_text = text;
      this.redraw();
    });
  },
  watch : {
    highlights : {
      handler : function(new_highlights) {
        this.redraw();
      },
      deep : false,
    },
  },
  methods : {
    redraw() {
      //this.$refs.actual_text.value = this.original_text;
      console.log("redraw");
      let output = '';

      let dest = this.$refs.actual_text;

      while (dest.firstChild)
        dest.removeChild(dest.firstChild);

      function buildSpan(offset, length, text) {
        let span = document.createElement('span');
        let content = document.createTextNode(text.slice(offset, offset+length));
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

      // assumes there is an existing region in which the mark will fall
      function splice_regions_around(regions, mark) {

        // first find the region in which the mark occurs
        let found = undefined;

        for (let i = 0; i < regions.length; i++) {
          let r = regions[i];

          if ((r.offset <= mark) && (mark < (r.offset + r.length))) {
            found = i;
          }
        }
        if (mark == regions[found].offset) {
          // no need for a new region, just return this one
          return found;
        } else {
          // splice region into two parts

          // add a new region [mark + found.stop]
          regions.splice(found + 1, 0, {
            offset : mark,
            length : regions[found].length - (mark - regions[found].offset),
            which : [...regions[found].which],
          })

          // cap the original region
          regions[found].length = mark - regions[found].offset;

          // the newly created one is the relevant one
          return found + 1;
        }
      }

      function splice_range(regions, a_range, meta) {
        let first_region = splice_regions_around(regions, a_range.from);
        let last_region = splice_regions_around(regions, a_range.to);

        for (let i = first_region; i < last_region; i++) {
          regions[i].which.push(meta);
        }
      }


      if (this.highlights && this.highlights.length) {
        // a localized copy of highlights which is from-ascending
        let highlights = [...this.highlights];
        highlights.sort((l, r) => {
          let l_val = (l.what == 'point') ? l.at : l.from;
          let r_val = (r.what == 'point') ? r.at : r.from;
          return r_val - l_val;
        });

        for (let i = 0; i < highlights.length; i++) {
          splice_range(this.regions, highlights[i], 'highlight');
        }
      }

      console.dir(this.selection);
      if (this.selection && this.selection.what == 'range') {
        splice_range(this.regions, this.selection, 'selection');
      }

      console.dir(this.regions);
      for (let i = 0; i < this.regions.length; i++) {
        let r = this.regions[i];
        r.span = buildSpan(r.offset, r.length, this.original_text);
        r.span.dataset.offset = r.offset;
        r.which.forEach((c) => { r.span.classList.add(c); });
        this.$refs.actual_text.appendChild(r.span);
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
