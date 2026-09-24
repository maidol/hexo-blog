'use strict';

// Keep Markdown previews relative to the post while serving the same images
// from Hexo's site-root asset directory in generated pages.
hexo.extend.filter.register('after_render:html', html => {
  return html.replace(/\.\.\/images\/drsg-harness-kit\//g, '/images/drsg-harness-kit/');
});
