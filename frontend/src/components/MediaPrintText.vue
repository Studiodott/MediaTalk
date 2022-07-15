<!-- vim: set ts=2 sw=2 expandtab : -->
<template>
  <div
    ref="actual_text"
    id="actual_text">
  </div>
</template>

<script>
export default {
  name : 'MediaPrintText',
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
        span.classList.add('quote');
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

          if (this.highlights.emphasis.length == 0  || this.highlights.emphasis.includes(highlights[i].handle)) {
            c += 'ff';
          } else {
            c += '7f';
          }
          splice_range(this.regions, highlights[i].position, {
            colour : c,
            comment : highlights[i].comment,
          });
        }
      }

      if (this.selection && this.selection.what == 'range') {
        splice_range(this.regions, this.selection, {
          colour : this.selection_colour,
          comment : '',
        });
      }

      // go over the regions, turn them into spans
      for (let i = 0; i < this.regions.length; i++) {
        let r = this.regions[i];

        // if this span does not contain any metadata (it is boring text),
        // ask the span contents to be snipped
        r.span = buildSpan(r.offset, r.length, this.original_text, r.which.length == 0);

        // note its offset for future calculation during select
        r.span.dataset.offset = r.offset;

        // go over the colours, apply them (only last lives)
        r.which.forEach((m) => { r.span.style = `background: ${m.colour};`; });

        this.$refs.actual_text.appendChild(r.span);

        // printing-specific; check if we need to add a comment right after that
        // content-bearing span
        let comments = r.which
          .filter((m) => m.comment && m.comment.length)
          .map((m) => `"${m.comment}"`);
        if (comments && comments.length) {
          // create a new span for this comment, stick it immediately after the
          // one we created above
          let span = document.createElement('span');
          let content = document.createTextNode(` (comments: ${comments.join(', ')}) `);
          span.appendChild(content);
          span.classList.add('quote');
          span.classList.add('comment');
          this.$refs.actual_text.appendChild(span);
        }

      }

    },
  },
};
</script>

<style>
#actual_text {
  white-space: pre-wrap;
}
.quote {
  font-style: italic;
}
.comment {
  font-weight: bold;
}
</style>
